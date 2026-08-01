#!/usr/bin/env python3
"""Microsys agent relay + auth gate.

Why this exists
---------------
1. The 1Panel agent exposes its 667 real API routes ONLY on a unix socket at
   /etc/1panel/agent.sock, and the agent forcibly resets /etc/1panel to mode
   0700 root:root on every start.  nginx workers (user `nginx`) can therefore
   never reach it.  This process runs as root and re-exposes the socket on a
   loopback-only TCP port.

2. The core's session endpoint (/api/v2/core/auth/current) answers HTTP 200
   even when the caller is unauthenticated - the real status lives in the JSON
   body as {"code":401,...}.  nginx `auth_request` only looks at the HTTP
   status line, so it would happily let anonymous traffic through.  This
   process therefore also serves /__authcheck, which translates the JSON code
   into a genuine HTTP 200 / 401 that nginx can gate on.

Listening on 127.0.0.1:9998 only; never exposed publicly.
"""
import asyncio
import json
import logging
import signal
import time

SOCK_PATH = "/etc/1panel/agent.sock"
BIND_HOST = "127.0.0.1"
BIND_PORT = 9998
CORE_HOST = "127.0.0.1"
CORE_PORT = 9999
CORE_AUTH_PATH = "/api/v2/core/auth/current"
AUTH_PATH = "/__authcheck"
AUTH_TTL = 3.0          # seconds a positive auth result stays cached
MAX_HEADER = 64 * 1024

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("agent-relay")

_auth_cache = {}        # cookie -> (expires_at, ok)


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
async def pump(reader, writer):
    try:
        while True:
            data = await reader.read(65536)
            if not data:
                break
            writer.write(data)
            await writer.drain()
    except (ConnectionResetError, BrokenPipeError, asyncio.CancelledError,
            asyncio.IncompleteReadError):
        pass
    finally:
        try:
            writer.close()
        except Exception:
            pass


async def read_headers(reader):
    """Read until end of HTTP headers. Returns (raw_bytes, first_line, headers)."""
    buf = b""
    while b"\r\n\r\n" not in buf:
        chunk = await reader.read(4096)
        if not chunk:
            break
        buf += chunk
        if len(buf) > MAX_HEADER:
            break
    head = buf.split(b"\r\n\r\n", 1)[0]
    lines = head.split(b"\r\n")
    first = lines[0].decode("latin-1") if lines else ""
    headers = {}
    for line in lines[1:]:
        if b":" in line:
            k, v = line.split(b":", 1)
            headers[k.decode("latin-1").strip().lower()] = v.decode("latin-1").strip()
    return buf, first, headers


async def core_check(cookie: str) -> bool:
    """Ask the core whether this session cookie is a logged-in user."""
    now = time.time()
    hit = _auth_cache.get(cookie)
    if hit and hit[0] > now:
        return hit[1]

    ok = False
    try:
        r, w = await asyncio.wait_for(
            asyncio.open_connection(CORE_HOST, CORE_PORT), timeout=5)
        req = (
            "GET {p} HTTP/1.1\r\n"
            "Host: 127.0.0.1\r\n"
            "Cookie: {c}\r\n"
            "Connection: close\r\n\r\n"
        ).format(p=CORE_AUTH_PATH, c=cookie)
        w.write(req.encode("latin-1"))
        await w.drain()
        raw = await asyncio.wait_for(r.read(65536), timeout=5)
        w.close()
        body = raw.split(b"\r\n\r\n", 1)[1] if b"\r\n\r\n" in raw else b""
        # tolerate chunked encoding: find the first {...} json object
        s = body.find(b"{")
        e = body.rfind(b"}")
        if s != -1 and e > s:
            payload = json.loads(body[s:e + 1].decode("utf-8", "ignore"))
            ok = payload.get("code") == 200 and payload.get("data")
            ok = bool(ok)
    except Exception as exc:
        log.warning("core auth check failed: %s", exc)
        ok = False

    # only cache positives; negatives must stay cheap to re-evaluate on login
    if ok:
        _auth_cache[cookie] = (now + AUTH_TTL, True)
    if len(_auth_cache) > 4096:
        _auth_cache.clear()
    return ok


def http_response(status: str, body: bytes = b"") -> bytes:
    return (
        "HTTP/1.1 {s}\r\n"
        "Content-Length: {n}\r\n"
        "Content-Type: application/json; charset=utf-8\r\n"
        "Cache-Control: no-store\r\n"
        "Connection: close\r\n\r\n"
    ).format(s=status, n=len(body)).encode("latin-1") + body


# --------------------------------------------------------------------------
# connection handler
# --------------------------------------------------------------------------
async def handle(client_reader, client_writer):
    try:
        buf, first, headers = await read_headers(client_reader)
        if not buf:
            client_writer.close()
            return

        parts = first.split()
        path = parts[1] if len(parts) >= 2 else ""

        # ---- auth gate endpoint (consumed locally, never forwarded) ----
        if path.startswith(AUTH_PATH):
            cookie = headers.get("cookie", "")
            ok = await core_check(cookie) if cookie else False
            if ok:
                client_writer.write(http_response("200 OK", b'{"code":200}'))
            else:
                client_writer.write(http_response(
                    "401 Unauthorized",
                    '{"code":401,"message":"用户未登录"}'.encode("utf-8")))
            await client_writer.drain()
            client_writer.close()
            return

        # ---- everything else: raw pump to the agent unix socket ----
        try:
            up_reader, up_writer = await asyncio.wait_for(
                asyncio.open_unix_connection(SOCK_PATH), timeout=10)
        except Exception as exc:
            log.warning("upstream connect failed: %s", exc)
            client_writer.write(http_response(
                "502 Bad Gateway",
                b'{"code":502,"message":"agent socket unreachable"}'))
            await client_writer.drain()
            client_writer.close()
            return

        up_writer.write(buf)          # replay the bytes we already consumed
        await up_writer.drain()

        await asyncio.gather(
            pump(client_reader, up_writer),
            pump(up_reader, client_writer),
        )
    except (ConnectionResetError, BrokenPipeError, asyncio.CancelledError):
        pass
    except Exception as exc:
        log.exception("handler error: %s", exc)
        try:
            client_writer.close()
        except Exception:
            pass


async def main():
    server = await asyncio.start_server(handle, BIND_HOST, BIND_PORT)
    log.info("relay listening on %s:%s -> %s (auth gate at %s)",
             BIND_HOST, BIND_PORT, SOCK_PATH, AUTH_PATH)
    loop = asyncio.get_event_loop()
    stop = loop.create_future()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(
                sig, lambda: stop.done() or stop.set_result(None))
        except NotImplementedError:
            pass
    async with server:
        await stop


if __name__ == "__main__":
    asyncio.run(main())
