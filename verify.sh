#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔍 KeepMeUp Verification"
echo "========================"
echo ""

fail=0

# The install script builds the bundle in the repo directory and copies it to
# ~/Applications. Check whichever exists — the installed copy is the one that
# actually runs day to day.
BUNDLE=""
for candidate in "$HOME/Applications/KeepMeUp.app" "$SCRIPT_DIR/KeepMeUp.app"; do
    if [ -d "$candidate" ]; then BUNDLE="$candidate"; break; fi
done

if [ -z "$BUNDLE" ]; then
    echo "❌ KeepMeUp.app not found in ~/Applications or this directory"
    echo "   Run ./install.sh to build and install it."
    exit 1
fi
echo "✅ KeepMeUp.app found at $BUNDLE"

# The venv is vendored inside the bundle, not in the repo.
VENV="$BUNDLE/Contents/Resources/venv"
if [ ! -d "$VENV" ]; then
    echo "❌ Bundled virtual environment missing at $VENV"
    echo "   Run ./install.sh to rebuild."
    exit 1
fi
echo "✅ Bundled virtual environment exists"

if "$VENV/bin/python3" -c "import rumps" 2>/dev/null; then
    echo "✅ rumps available in the bundle"
else
    echo "❌ rumps missing from the bundle — run ./install.sh to rebuild"
    fail=1
fi

if [ ! -f "$SCRIPT_DIR/keepmeup_menu.py" ]; then
    echo "❌ keepmeup_menu.py not found"
    exit 1
fi

if python3 -m py_compile "$SCRIPT_DIR/keepmeup_menu.py" 2>/dev/null; then
    echo "✅ keepmeup_menu.py compiles"
else
    echo "❌ keepmeup_menu.py has syntax errors"
    fail=1
fi

if pgrep -f keepmeup_menu.py >/dev/null 2>&1; then
    echo "✅ KeepMeUp is currently running"
else
    echo "ℹ️  KeepMeUp is not running right now"
fi

echo ""
if [ "$fail" -ne 0 ]; then
    echo "⚠️  Some checks failed — see above."
    exit 1
fi

echo "📍 To launch KeepMeUp:"
echo "   open \"$BUNDLE\""
echo ""
echo "Or from Spotlight: Cmd+Space -> 'KeepMeUp' -> Enter"
echo ""
echo "✨ Look for the jagged star icon in your menu bar (top right)"
