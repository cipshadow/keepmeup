#!/bin/bash
# Build an unsigned, ad-hoc-signed universal macOS application bundle.
# The release workflow runs this from a universal2 CPython interpreter.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
APP_NAME="KeepMeUp"
VERSION="${VERSION:-$(git -C "$REPO_DIR" describe --tags --always --dirty 2>/dev/null || echo dev)}"
BUILD_DIR="$REPO_DIR/build"
DIST_DIR="$REPO_DIR/dist"
RELEASE_DIR="$REPO_DIR/release"
VENV_DIR="$REPO_DIR/.build-venv"
INSTALL=false
REQUIRE_UNIVERSAL=false

usage() {
    echo "Usage: $0 [--install] [--require-universal]"
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --install) INSTALL=true ;;
        --require-universal) REQUIRE_UNIVERSAL=true ;;
        -h|--help) usage; exit 0 ;;
        *) usage >&2; exit 2 ;;
    esac
    shift
done

cd "$REPO_DIR"

if ! command -v python3 >/dev/null; then
    echo "Python 3.10 or newer is required to build from source." >&2
    exit 1
fi

PYTHON_VERSION="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
case "$PYTHON_VERSION" in
    3.10|3.11|3.12|3.13) ;;
    *)
        echo "Python 3.10 through 3.13 is required to build from source; found $PYTHON_VERSION." >&2
        exit 1
        ;;
esac

if [ "$REQUIRE_UNIVERSAL" = true ]; then
    PYTHON_EXECUTABLE="$(python3 -c 'import os, sys; print(os.path.realpath(sys.executable))')"
    PYTHON_ARCHS="$(lipo -archs "$PYTHON_EXECUTABLE" 2>/dev/null || true)"
    if ! printf '%s\n' "$PYTHON_ARCHS" | grep -qw x86_64 || ! printf '%s\n' "$PYTHON_ARCHS" | grep -qw arm64; then
        echo "A universal2 CPython is required for a universal release; found: $PYTHON_ARCHS" >&2
        exit 1
    fi
fi

# This venv exists only while building. It is never copied into the app.
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/python" -m pip install --upgrade pip >/dev/null
"$VENV_DIR/bin/python" -m pip install -r requirements.txt -r requirements-build.txt

rm -rf "$BUILD_DIR" "$DIST_DIR" "$RELEASE_DIR"
mkdir -p "$RELEASE_DIR"

PYINSTALLER_ARGS=(
    --noconfirm
    --clean
    --windowed
    --name "$APP_NAME"
    --osx-bundle-identifier com.local.keepmeup
    --icon assets/AppIcon.icns
    --add-data "$REPO_DIR/assets:assets"
    --collect-all rumps
    --hidden-import AppKit
    --target-architecture universal2
    --distpath "$DIST_DIR"
    --workpath "$BUILD_DIR"
    --specpath "$BUILD_DIR"
    keepmeup_menu.py
)

MACOSX_DEPLOYMENT_TARGET=13.0 "$VENV_DIR/bin/python" -m PyInstaller "${PYINSTALLER_ARGS[@]}"

APP_PATH="$DIST_DIR/$APP_NAME.app"
if [ ! -d "$APP_PATH" ]; then
    echo "PyInstaller did not produce $APP_PATH" >&2
    exit 1
fi

# PyInstaller generates the application Info.plist. Declare the project
# support floor before signing, so Finder prevents installation on older Macs.
PLIST="$APP_PATH/Contents/Info.plist"
if /usr/libexec/PlistBuddy -c 'Print :LSMinimumSystemVersion' "$PLIST" >/dev/null 2>&1; then
    /usr/libexec/PlistBuddy -c 'Set :LSMinimumSystemVersion 13.0' "$PLIST"
else
    /usr/libexec/PlistBuddy -c 'Add :LSMinimumSystemVersion string 13.0' "$PLIST"
fi

# Ad-hoc signing keeps the bundle internally consistent. It is deliberately
# not notarized: first launch of a downloaded build uses Control-click > Open.
codesign --force --deep --sign - "$APP_PATH"
codesign --verify --deep --strict --verbose=2 "$APP_PATH"

VERIFY_ARGS=(--bundle "$APP_PATH")
if [ "$REQUIRE_UNIVERSAL" = true ]; then
    VERIFY_ARGS+=(--require-universal)
fi
"$REPO_DIR/verify.sh" "${VERIFY_ARGS[@]}"

DMG_PATH="$RELEASE_DIR/$APP_NAME-$VERSION-universal2.dmg"
hdiutil create -volname "$APP_NAME" -srcfolder "$APP_PATH" -ov -format UDZO "$DMG_PATH" >/dev/null
(cd "$RELEASE_DIR" && shasum -a 256 "$(basename "$DMG_PATH")" > "$(basename "$DMG_PATH").sha256")

echo "✅ Built $DMG_PATH"

if [ "$INSTALL" = true ]; then
    INSTALLED_PATH="$HOME/Applications/$APP_NAME.app"
    mkdir -p "$HOME/Applications"
    pkill -f "$INSTALLED_PATH/Contents/MacOS/$APP_NAME" 2>/dev/null || true
    rm -rf "$INSTALLED_PATH"
    ditto "$APP_PATH" "$INSTALLED_PATH"
    /System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "$INSTALLED_PATH" >/dev/null 2>&1 || true
    echo "✅ Installed $INSTALLED_PATH"
fi
