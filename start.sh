#!/bin/bash
# Gym Equipment Analyzer v3
# Uses Cloud Vision (gemma3:12b via Ollama Cloud) for accurate multi-equipment detection
# Frontend: responsive grid (mobile/tablet/desktop)

set -e

APP_DIR="/opt/hermes/gym-analyzer"
PORT=5005

echo "🏋️ Starting Gym Equipment Analyzer v3..."
echo ""

# Kill any existing instances
pkill -f "python3 app.py" 2>/dev/null || true
sleep 1

# Start Flask backend
cd "$APP_DIR"
python3 app.py &
FLASK_PID=$!

# Wait for Flask to be ready
sleep 3
if ! curl -sf http://localhost:$PORT/ > /dev/null 2>&1; then
    echo "❌ Flask failed to start."
    exit 1
fi
echo "✅ Flask responding on http://localhost:$PORT"

# Start Cloudflare Tunnel for public access
cloudflared tunnel --url "http://localhost:$PORT" --no-autoupdate &
CLOUDFLARE_PID=$!

echo ""
echo "════════════════════════════════════════════"
echo "  🏋️  GYM EQUIPMENT ANALYZER v3.1"
echo "════════════════════════════════════════════"
echo ""
echo "  📱 Open on your phone/desktop:"
echo "  Check cloudflared output for the tunnel URL"
echo "  (https://xxx.trycloudflare.com)"
echo "  or run: cloudflared tunnel --url http://localhost:$PORT"
echo ""
echo "  ✅ Powered by:"
echo "  • Cloud Vision (gemma3:12b) — detects 10+ equipment per image"
echo "  • Curated exercise database — accurate instructions"
echo "  • YouTube demo videos — real demonstrations"
echo "  • Fully responsive — mobile, tablet, desktop"
echo "  • Camera capture + upload + drag & drop"
echo ""
echo "  🛑 To stop: pkill -f 'python3 app.py'"
echo "════════════════════════════════════════════"
