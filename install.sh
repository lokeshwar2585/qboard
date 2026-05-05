#!/bin/bash

echo "🚀 Installing Qboard..."
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null
then
    echo "❌ Python 3 is not installed. Please install it first:"
    echo "   brew install python3"
    exit 1
fi

echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

echo ""
echo "✅ Installation complete!"
echo ""
echo "🎯 To run Qboard:"
echo "   python3 qboard.py"
echo ""
echo "⚠️  IMPORTANT: Grant Accessibility permissions"
echo "   1. System Preferences → Security & Privacy"
echo "   2. Privacy tab → Accessibility"
echo "   3. Click 🔒 to unlock"
echo "   4. Add Terminal (or your terminal app)"
echo "   5. ✅ Check the box"
echo ""
echo "Then restart Qboard for hotkeys to work!"
echo ""
