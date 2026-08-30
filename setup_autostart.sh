#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 Setting up KeepMeUp to launch at startup..."
echo ""

if [ ! -d "$HOME/Applications/KeepMeUp.app" ]; then
    echo "⚠️  ~/Applications/KeepMeUp.app not found — run ./install.sh first."
    exit 1
fi

# Create LaunchAgents directory if it doesn't exist
mkdir -p ~/Library/LaunchAgents

# Expand the __HOME__ placeholder in the checked-in template as we install it,
# so the LaunchAgent points at this user's home rather than whoever's home was
# baked in when the template was written.
sed "s|__HOME__|$HOME|g" "$SCRIPT_DIR/com.local.keepmeup.plist" > ~/Library/LaunchAgents/com.local.keepmeup.plist

# Load it with launchctl
launchctl unload ~/Library/LaunchAgents/com.local.keepmeup.plist 2>/dev/null
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
