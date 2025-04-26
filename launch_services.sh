#!/bin/bash

echo "🚀 Launching microservices..."

# Paths to each service and ports
declare -a SERVICES=(
  "summarization/app.py 8001"
  "sentiment/app.py 8000"
  "preprocessing/app.py 8003"
  "qa/app.py 8002"
)

for SERVICE in "${SERVICES[@]}"; do
  FILE=$(echo $SERVICE | awk '{print $1}')
  PORT=$(echo $SERVICE | awk '{print $2}')
  DIR=$(dirname "$FILE")
  MOD=$(basename "$FILE" .py)

  osascript <<EOF
  tell application "Terminal"
    do script "cd $(pwd)/services/$DIR && uvicorn $MOD:app --host 0.0.0.0 --port $PORT --reload"
  end tell
EOF

  sleep 1
done

echo "✅ All services launching in separate terminal tabs."
