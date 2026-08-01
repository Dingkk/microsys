#!/bin/bash
# Microsys 1Panel 全栈启动脚本
# 顺序：1panel-agent → relay → 1panel-core → nginx (PID 1)
set -e

LOG_DIR=/var/log/microsys
mkdir -p "$LOG_DIR"

echo "[entrypoint] Starting 1panel-agent..."
/opt/microsys/bin/1panel-agent >> "$LOG_DIR/agent.log" 2>&1 &
AGENT_PID=$!

echo "[entrypoint] Waiting for agent socket..."
for i in $(seq 1 100); do
    if [ -S /etc/1panel/agent.sock ]; then
        echo "[entrypoint] Socket ready after ${i} checks (0.2s intervals)"
        break
    fi
    sleep 0.2
done

if [ ! -S /etc/1panel/agent.sock ]; then
    echo "[entrypoint] ERROR: agent socket never appeared"
    tail -20 "$LOG_DIR/agent.log" 2>/dev/null || true
    exit 1
fi

echo "[entrypoint] Starting agent_relay (TCP↔UNIX)..."
python3 /opt/microsys/bin/agent_relay.py >> "$LOG_DIR/relay.log" 2>&1 &
RELAY_PID=$!

# 等待 relay 监听 9998
for i in $(seq 1 20); do
    if (echo > /dev/tcp/127.0.0.1/9998) 2>/dev/null; then
        echo "[entrypoint] Relay listening on 9998 (after ${i} retries)"
        break
    fi
    sleep 0.2
done

echo "[entrypoint] Starting 1panel-core..."
cd /opt/microsys
/opt/microsys/bin/1panel-core >> "$LOG_DIR/core.log" 2>&1 &
CORE_PID=$!

# 等待 core 监听 9999
for i in $(seq 1 30); do
    if (echo > /dev/tcp/127.0.0.1/9999) 2>/dev/null; then
        echo "[entrypoint] Core listening on 9999 (after ${i} retries)"
        break
    fi
    sleep 0.2
done

# 退出处理：core/agent 挂了 nginx 也跟着退
cleanup() {
    echo "[entrypoint] Shutting down..."
    kill $RELAY_PID 2>/dev/null || true
    kill $CORE_PID 2>/dev/null || true
    kill $AGENT_PID 2>/dev/null || true
    exit 0
}
trap cleanup SIGTERM SIGINT

echo "[entrypoint] All services up. Starting nginx (foreground)..."
nginx -g 'daemon off;'
