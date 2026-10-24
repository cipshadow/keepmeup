#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUNDLE=""
REQUIRE_UNIVERSAL=false

usage() {
    echo "Usage: $0 [--bundle /path/to/KeepMeUp.app] [--require-universal]"
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --bundle) BUNDLE="$2"; shift ;;
        --require-universal) REQUIRE_UNIVERSAL=true ;;
        -h|--help) usage; exit 0 ;;
        *) usage >&2; exit 2 ;;
    esac
    shift
done

if [ -z "$BUNDLE" ]; then
    BUNDLE="$HOME/Applications/KeepMeUp.app"
fi

fail=0
if [ ! -d "$BUNDLE" ]; then
    echo "❌ KeepMeUp.app not found at $BUNDLE" >&2
    exit 1
fi

EXECUTABLE="$BUNDLE/Contents/MacOS/KeepMeUp"
INFO_PLIST="$BUNDLE/Contents/Info.plist"
echo "🔍 Verifying $BUNDLE"

[ -x "$EXECUTABLE" ] || { echo "❌ App executable is missing" >&2; exit 1; }
[ -f "$INFO_PLIST" ] || { echo "❌ Info.plist is missing" >&2; exit 1; }

if plutil -extract LSMinimumSystemVersion raw "$INFO_PLIST" | grep -qx '13.0'; then
    echo "✅ macOS 13.0 minimum deployment target"
else
    echo "❌ App does not declare macOS 13.0 as its minimum version" >&2
    fail=1
fi

if [ -f "$BUNDLE/Contents/Resources/assets/icon_off.png" ] || find "$BUNDLE" -path '*/assets/icon_off.png' -print -quit | grep -q .; then
    echo "✅ menu bar assets bundled"
else
    echo "❌ menu bar assets are missing" >&2
    fail=1
fi

if codesign --verify --deep --strict --verbose=2 "$BUNDLE"; then
    echo "✅ code signature verifies"
else
    echo "❌ code signature verification failed" >&2
    fail=1
fi

if [ "$REQUIRE_UNIVERSAL" = true ]; then
    MACH_O_FAILURES=0
    while IFS= read -r -d '' file_path; do
        file_type="$(file -b "$file_path")"
        case "$file_type" in
            *"Mach-O"*)
                archs="$(lipo -archs "$file_path" 2>/dev/null || true)"
                if ! printf '%s\n' "$archs" | grep -qw x86_64 || ! printf '%s\n' "$archs" | grep -qw arm64; then
                    echo "❌ Not universal2: $file_path ($archs)" >&2
                    MACH_O_FAILURES=1
                fi
                ;;
        esac
    done < <(find "$BUNDLE" -type f -print0)
    if [ "$MACH_O_FAILURES" -eq 0 ]; then
        echo "✅ every Mach-O binary supports Intel and Apple Silicon"
    else
        fail=1
    fi
fi

exit "$fail"
