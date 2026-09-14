#!/bin/bash
# DevPortal Development Server Script
# Starts a local web server for development

set -e

PORT="${1:-3000}"
HOST="${2:-localhost}"

echo "============================================"
echo "  DevPortal Development Server"
echo "============================================"
echo ""

# Check for available servers
if command -v python3 &> /dev/null; then
    echo "Starting Python HTTP Server on http://${HOST}:${PORT}"
    echo "Press Ctrl+C to stop"
    echo "============================================"
    python3 -m http.server "$PORT" --bind "$HOST"
elif command -v php &> /dev/null; then
    echo "Starting PHP Development Server on http://${HOST}:${PORT}"
    echo "Press Ctrl+C to stop"
    echo "============================================"
    php -S "${HOST}:${PORT}"
elif command -v npx &> /dev/null; then
    echo "Starting npx serve on http://${HOST}:${PORT}"
    echo "Press Ctrl+C to stop"
    echo "============================================"
    npx serve . -l "$PORT"
else
    echo "Error: No suitable web server found."
    echo "Please install Python 3, PHP, or Node.js."
    exit 1
fi
