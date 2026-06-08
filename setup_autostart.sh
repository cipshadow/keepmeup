#!/bin/bash

echo "🚀 Setting up KeepMeUp to launch at startup..."
echo ""

# Create LaunchAgents directory if it doesn't exist
mkdir -p ~/Library/LaunchAgents

# Copy the plist file
cp com.local.keepmeup.plist ~/Library/LaunchAgents/

# Load it with launchctl
launchctl load ~/Library/LaunchAgents/com.local.keepmeup.plist

if [ $? -eq 0 ]; then
    echo "✅ KeepMeUp will now launch automatically when you start your Mac!"
    echo ""
    echo "To disable autostart, run:"
    echo "  launchctl unload ~/Library/LaunchAgents/com.local.keepmeup.plist"
else
    echo "⚠️  There was an issue setting up autostart"
    echo "Try running: launchctl load ~/Library/LaunchAgents/com.local.keepmeup.plist"
fi
