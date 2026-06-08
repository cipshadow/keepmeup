#!/bin/bash

echo "🔍 KeepMeUp Verification"
echo "========================"
echo ""

# Check if app exists
if [ ! -d "KeepMeUp.app" ]; then
    echo "❌ KeepMeUp.app not found"
    exit 1
fi
echo "✅ KeepMeUp.app exists"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found"
    exit 1
fi
echo "✅ Virtual environment exists"

# Check if rumps is installed
source venv/bin/activate
if python3 -c "import rumps" 2>/dev/null; then
    echo "✅ rumps library installed"
else
    echo "❌ rumps not installed - installing now..."
    pip install rumps -q
    if python3 -c "import rumps" 2>/dev/null; then
        echo "✅ rumps library installed"
    else
        echo "❌ Failed to install rumps"
        exit 1
    fi
fi

# Check if keepmeup_menu.py exists and is valid
if [ ! -f "keepmeup_menu.py" ]; then
    echo "❌ keepmeup_menu.py not found"
    exit 1
fi

if python3 -m py_compile keepmeup_menu.py 2>/dev/null; then
    echo "✅ keepmeup_menu.py is valid"
else
    echo "❌ keepmeup_menu.py has errors"
    exit 1
fi

echo ""
echo "📍 To launch KeepMeUp:"
echo "   open KeepMeUp.app"
echo ""
echo "Or from Spotlight:"
echo "   Cmd+Space -> type 'KeepMeUp' -> press Enter"
echo ""
echo "✨ App should show 💤 in your menu bar (top right)"
