#!/usr/bin/env bash
set -euo pipefail

cleanup() {
    kill -TERM "$AI_PID" "$BACKEND_PID" 2>/dev/null || true
    wait
}
trap cleanup TERM INT

cd /app/ai-service
/opt/venv-ai/bin/uvicorn main:app --host 0.0.0.0 --port 8001 &
AI_PID=$!

cd /app/backend
/opt/venv-backend/bin/uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

wait -n "$AI_PID" "$BACKEND_PID"
EXIT_CODE=$?
cleanup
exit "$EXIT_CODE"