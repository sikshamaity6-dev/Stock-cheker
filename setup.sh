#!/bin/bash
echo "🤖 Shein Wishlist Bot Setup"
echo "============================"
echo ""
echo "Step 1: Installing Python dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed!"
echo ""
echo "Step 2: Installing Playwright browsers..."
python -m playwright install
echo "✅ Playwright installed!"
echo ""
echo "Step 3: Checking config.json..."
if [ -f config.json ]; then
echo "✅ config.json found!"
echo ""
echo "Current configuration:"
cat config.json
else
echo "❌ config.json not found!"
exit 1
fi
echo ""
echo "============================"
echo "✅ Setup complete!"
echo "============================"
echo ""
echo "To start the bot, run:"
echo "  python main.py"
echo ""
echo "The bot will check your Shein wishlist every 5 minutes"
echo "and send Telegram notifications for any changes!"
echo ""