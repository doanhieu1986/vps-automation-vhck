#!/bin/bash

# Start HTTP server for VPS Automation VHCK project

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT=8000

echo "🚀 Starting HTTP Server..."
echo "Project directory: $PROJECT_DIR"
echo "Port: $PORT"

# Kill existing server if running
pkill -f "python3.*http.server.*$PORT" 2>/dev/null && echo "Stopped previous server"

# Start new server
cd "$PROJECT_DIR"
python3 -m http.server $PORT > /tmp/http_server_$PORT.log 2>&1 &

sleep 1

# Check if server started
if lsof -i :$PORT > /dev/null 2>&1; then
    echo "✅ Server started successfully!"
    echo "📍 URL: http://localhost:$PORT/web/vps_automation_vhck.html"
    echo "📊 Data: http://localhost:$PORT/data/vsd_records.json"
    echo ""
    echo "Log file: /tmp/http_server_$PORT.log"
else
    echo "❌ Failed to start server"
    exit 1
fi
