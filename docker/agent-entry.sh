#!/bin/sh
set -e

echo "[agent-entry] Starting 1panel-agent..."
/opt/microsys/bin/1panel-agent &
AGENT_PID=$!

echo "[agent-entry] Waiting for agent socket..."
for i in $(seq 1 100); do
    if [ -S /etc/1panel/agent.sock ]; then
        echo "[agent-entry] Socket ready after ${i} checks"
        break
    fi
    sleep 0.2
done

if [ ! -S /etc/1panel/agent.sock ]; then
    echo "[agent-entry] ERROR: agent socket never appeared"
    exit 1
fi

echo "[agent-entry] Starting relay on 0.0.0.0:9998..."
exec python3 /opt/microsys/bin/agent_relay.py
