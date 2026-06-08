#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "📦 Installing KeepMeUp..."
echo ""

# Copy to ~/Applications
mkdir -p ~/Applications
cp -r "$SCRIPT_DIR/KeepMeUp.app" ~/Applications/ || {
    echo "❌ Failed to copy app to ~/Applications"
    exit 1
}

echo "✅ KeepMeUp.app installed to ~/Applications/"
echo ""

# Rebuild the app in the project directory too
echo "🏗️  Updating project app..."

APP_NAME="KeepMeUp"
BUNDLE_NAME="$APP_NAME.app"

# Remove old build
rm -rf "$SCRIPT_DIR/$BUNDLE_NAME"

# Create bundle structure
mkdir -p "$SCRIPT_DIR/$BUNDLE_NAME/Contents/MacOS"
mkdir -p "$SCRIPT_DIR/$BUNDLE_NAME/Contents/Resources"

# Create launcher script with hardcoded path to this installation
cat > "$SCRIPT_DIR/$BUNDLE_NAME/Contents/MacOS/$APP_NAME" << LAUNCHER
#!/bin/bash
# KeepMeUp launcher - runs menu bar app
APP_DIR="$SCRIPT_DIR"
LOG_FILE="\$HOME/.keepmeup.log"

# Start logging
echo "=== KeepMeUp Launched at \$(date) ===" >> "\$LOG_FILE" 2>&1
echo "APP_DIR: \$APP_DIR" >> "\$LOG_FILE" 2>&1

# Check if venv exists
if [ ! -d "\$APP_DIR/venv" ]; then
    echo "ERROR: Virtual environment not found at \$APP_DIR/venv" >> "\$LOG_FILE" 2>&1
    exit 1
fi

# Check if keepmeup_menu.py exists
if [ ! -f "\$APP_DIR/keepmeup_menu.py" ]; then
    echo "ERROR: Script not found at \$APP_DIR/keepmeup_menu.py" >> "\$LOG_FILE" 2>&1
    exit 1
fi

# Activate venv and run
source "\$APP_DIR/venv/bin/activate" >> "\$LOG_FILE" 2>&1
cd "\$APP_DIR" >> "\$LOG_FILE" 2>&1
python3 keepmeup_menu.py >> "\$LOG_FILE" 2>&1

exit \$?
LAUNCHER

chmod +x "$SCRIPT_DIR/$BUNDLE_NAME/Contents/MacOS/$APP_NAME"

# Create Info.plist
cat > "$SCRIPT_DIR/$BUNDLE_NAME/Contents/Info.plist" << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleExecutable</key>
    <string>KeepMeUp</string>
    <key>CFBundleIdentifier</key>
    <string>com.local.keepmeup</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>KeepMeUp</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>LSUIElement</key>
    <true/>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSPrincipalClass</key>
    <string>NSApplication</string>
</dict>
</plist>
PLIST

echo "✅ Project app updated"
echo ""
echo "🚀 You can now:"
echo "   1. Find 'KeepMeUp' in Spotlight (Cmd+Space)"
echo "   2. Or open ~/Applications/KeepMeUp.app"
echo ""
echo "✨ KeepMeUp will appear in your menu bar!"
