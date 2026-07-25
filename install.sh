#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "📦 Installing KeepMeUp..."
echo ""

APP_NAME="KeepMeUp"
BUNDLE_NAME="$APP_NAME.app"
BUNDLE_PATH="$SCRIPT_DIR/$BUNDLE_NAME"
INSTALLED_PATH="$HOME/Applications/$BUNDLE_NAME"

echo "🏗️  Building self-contained app bundle..."

# Remove old build
rm -rf "$BUNDLE_PATH"

# Create bundle structure
mkdir -p "$BUNDLE_PATH/Contents/MacOS"
mkdir -p "$BUNDLE_PATH/Contents/Resources"

# Vendor a private venv + the script INSIDE the bundle, so the app no
# longer depends on this repo (or any fixed path) still existing at
# whatever location it happened to be built from.
python3 -m venv "$BUNDLE_PATH/Contents/Resources/venv"
"$BUNDLE_PATH/Contents/Resources/venv/bin/pip" install -q --upgrade pip
"$BUNDLE_PATH/Contents/Resources/venv/bin/pip" install -q rumps pyobjc-framework-Cocoa

cp "$SCRIPT_DIR/keepmeup_menu.py" "$BUNDLE_PATH/Contents/Resources/keepmeup_menu.py"

# Copy the pre-built icon assets (generated once via assets/generate_icons.py,
# checked into git — not regenerated at install time so the bundle doesn't
# need Pillow as a runtime dependency).
mkdir -p "$BUNDLE_PATH/Contents/Resources/assets"
cp "$SCRIPT_DIR"/assets/icon_*.png "$BUNDLE_PATH/Contents/Resources/assets/"
cp "$SCRIPT_DIR/assets/AppIcon.icns" "$BUNDLE_PATH/Contents/Resources/AppIcon.icns"

# Create launcher script. It locates its own Resources dir relative to
# itself, so the bundle works no matter where it's copied or run from.
cat > "$BUNDLE_PATH/Contents/MacOS/$APP_NAME" << 'LAUNCHER'
#!/bin/bash
BUNDLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../Resources" && pwd)"
LOG_FILE="$HOME/.keepmeup.log"

fail() {
    echo "ERROR: $1" >> "$LOG_FILE" 2>&1
    osascript -e "display dialog \"KeepMeUp failed to start:\n\n$1\" buttons {\"OK\"} with icon stop with title \"KeepMeUp\"" >/dev/null 2>&1
    exit 1
}

echo "=== KeepMeUp Launched at $(date) ===" >> "$LOG_FILE" 2>&1
echo "BUNDLE_DIR: $BUNDLE_DIR" >> "$LOG_FILE" 2>&1

[ -d "$BUNDLE_DIR/venv" ] || fail "Virtual environment not found at $BUNDLE_DIR/venv"
[ -f "$BUNDLE_DIR/keepmeup_menu.py" ] || fail "Script not found at $BUNDLE_DIR/keepmeup_menu.py"

source "$BUNDLE_DIR/venv/bin/activate" >> "$LOG_FILE" 2>&1
cd "$BUNDLE_DIR" >> "$LOG_FILE" 2>&1

python3 keepmeup_menu.py >> "$LOG_FILE" 2>&1
status=$?

# 143 (SIGTERM) and 137 (SIGKILL) mean something else terminated the app
# (Force Quit, Activity Monitor, a new launch replacing this one) — not a
# startup failure, so don't show a dialog for those.
if [ $status -ne 0 ] && [ $status -ne 143 ] && [ $status -ne 137 ]; then
    fail "keepmeup_menu.py exited with status $status. See $LOG_FILE for details."
fi

exit $status
LAUNCHER

chmod +x "$BUNDLE_PATH/Contents/MacOS/$APP_NAME"

# Create Info.plist
cat > "$BUNDLE_PATH/Contents/Info.plist" << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleExecutable</key>
    <string>KeepMeUp</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon.icns</string>
    <key>CFBundleIconName</key>
    <string>AppIcon</string>
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

echo "✅ Project app built (self-contained)"
echo ""

# Ad-hoc sign so Gatekeeper doesn't flag it if it's ever quarantined
# (e.g. AirDropped, downloaded, copied via a browser).
codesign --force --deep -s - "$BUNDLE_PATH" 2>/dev/null || true

# Kill any old running instances before replacing the installed copy.
pkill -f "$INSTALLED_PATH/Contents/MacOS/$APP_NAME" 2>/dev/null || true

mkdir -p "$HOME/Applications"
rm -rf "$INSTALLED_PATH"
cp -R "$BUNDLE_PATH" "$INSTALLED_PATH" || {
    echo "❌ Failed to copy app to ~/Applications"
    exit 1
}

echo "✅ KeepMeUp.app installed to ~/Applications/"
echo ""

# Point the LaunchAgent (if any) at the stable installed copy, not the repo.
LAUNCH_AGENT="$HOME/Library/LaunchAgents/com.local.keepmeup.plist"
if [ -f "$SCRIPT_DIR/com.local.keepmeup.plist" ]; then
    sed "s|/Users/[^<]*KeepMeUp.app|$INSTALLED_PATH|" "$SCRIPT_DIR/com.local.keepmeup.plist" > "$SCRIPT_DIR/com.local.keepmeup.plist.tmp" \
        && mv "$SCRIPT_DIR/com.local.keepmeup.plist.tmp" "$SCRIPT_DIR/com.local.keepmeup.plist"
fi
if [ -f "$LAUNCH_AGENT" ]; then
    launchctl unload "$LAUNCH_AGENT" 2>/dev/null || true
    cp "$SCRIPT_DIR/com.local.keepmeup.plist" "$LAUNCH_AGENT"
    launchctl load "$LAUNCH_AGENT"
    echo "✅ LaunchAgent updated to point at ~/Applications/KeepMeUp.app"
    echo ""
fi

# Refresh LaunchServices so Spotlight drops any stale registration, and touch
# the bundle so Finder/the icon cache notices the (possibly new) icon promptly.
touch "$INSTALLED_PATH"
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "$INSTALLED_PATH" >/dev/null 2>&1 || true

echo "🚀 You can now:"
echo "   1. Find 'KeepMeUp' in Spotlight (Cmd+Space)"
echo "   2. Or open ~/Applications/KeepMeUp.app"
echo ""
echo "✨ KeepMeUp will appear in your menu bar!"
