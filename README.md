# 📋 Qboard

> Queue your clipboard - copy multiple items, paste in order

A simple macOS menu bar app for FIFO (First-In-First-Out) clipboard management. Stop switching back and forth while copying and pasting!

![Qboard Demo](demo.gif)

## 💡 The Problem

Traditional copy-paste workflow:
Copy item A → Switch app → Paste A → Switch back →
Copy item B → Switch app → Paste B → Switch back →
Copy item C → Switch app → Paste C

**Annoying!** 😫

## ✨ The Solution

With Qboard:

Copy A → Copy B → Copy C → Switch app →
Paste A → Load next → Paste B → Load next → Paste C

**Much better!** 🎉

## 🎯 Features

- 📥 **Copy Mode**: Automatically captures everything you copy (Cmd+C)
- 📤 **Paste Mode**: Paste items in the exact order you copied them
- ⌨️ **Quick Hotkey**: `Cmd+Shift+N` loads next item
- 🎨 **Menu Bar Icon**: Color-coded status (Gray/Blue/Green)
- 🔄 **Simple Controls**: Start, stop, clear queue anytime
- 🆓 **Free & Open Source**: MIT License

## 🚀 Quick Start

### Requirements

- macOS 10.14 or later
- Python 3.7+

### Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/qboard.git
cd qboard

# Install dependencies
chmod +x install.sh
./install.sh

# Run it!
python3 qboard.py


🎨 Icon Guide
The menu bar icon changes color based on mode:

Gray Clipboard 📋 - Inactive (idle)
Blue Arrow Down ⬇️ - Copy Mode (collecting items)
Green Arrow Up ⬆️ - Paste Mode (ready to paste)


🤝 Contributing
Contributions welcome! This started as a personal tool but I'm happy to improve it.

🐛 Bug reports: Open an issue
💡 Feature ideas: Open an issue with your idea

Made with ❤️ by Sai Lokeshwar

Queue your clipboard, paste with ease! 🚀
