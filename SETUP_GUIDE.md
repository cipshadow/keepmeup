# KeepMeUp Setup & Verification Guide

## Installation

Your KeepMeUp app is ready! Choose how to launch it:

### Option 1: Quick Launch (Right Now)
```bash
open ~/KeepMeUp/KeepMeUp.app
```

### Option 2: Install to Applications (Recommended)
```bash
bash ~/KeepMeUp/install.sh
```

Then find it in Spotlight (Cmd+Space → "KeepMeUp") or in Applications folder.

---

## ✅ Verification Checklist

After launching the app, do these checks:

### 1. Look for the menu bar icon
Look at the **very top right** of your screen near the clock and Wifi icon.
You should see either:
- **○** = App is running and screen sleep is OFF
- **◉** = App is running and screen sleep is ON

### 2. Click the icon to test
- Click the **○** icon 
- It should change to **◉**
- Click again to toggle back to **○**

### 3. Check the menu
- Click and hold the icon (or right-click)
- You should see a menu with:
  - "Toggle Screen Awake"
  - "Quit"

### 4. Test the functionality
- Click "Toggle Screen Awake" to enable (should change to ✨)
- Your screen should now stay awake indefinitely
- Move away from your Mac and wait - normally the screen would sleep, but now it won't

---

## 🔧 Troubleshooting

### Problem: Nothing happens when I click the icon

**Solution 1: Restart the app**
```bash
pkill -f keepmeup_menu.py
open ~/KeepMeUp/KeepMeUp.app
```

**Solution 2: Check the logs**
```bash
cat ~/.keepmeup_app.log
```

### Problem: Icon doesn't appear in menu bar

Try clicking the Spotlight search (Cmd+Space) and searching for "KeepMeUp" - the app may be running but the menu bar icon might be hidden (try hidden Icon Hider or similar if you have other menu bar icons).

### Problem: App crashes on startup

Run this to rebuild the environment:
```bash
cd ~/KeepMeUp
python3 -m venv venv --upgrade-deps
source venv/bin/activate
pip install rumps --upgrade
```

Then test it:
```bash
python3 keepmeup_menu.py
```

---

## 📝 Quick Reference

| Icon | Status |
|------|--------|
| ○ | Screen can sleep normally |
| ◉ | Screen forced to stay awake |

**To verify screen is actually awake:**
1. Toggle to ◉
2. Step away from your Mac
3. Wait 5 minutes
4. Screen should still be on (normally it would sleep after ~5 min)

---

## 🔄 Auto-start at Login

To make KeepMeUp automatically launch every time you turn on your Mac:

```bash
bash ~/KeepMeUp/setup_autostart.sh
```

That's it! Next time you restart, KeepMeUp will be in your menu bar automatically.

**To disable auto-start later:**
```bash
launchctl unload ~/Library/LaunchAgents/com.local.keepmeup.plist
```

---

## 🆘 Still Having Issues?

Check the detailed logs:
```bash
# App activity log
cat ~/.keepmeup_app.log

# Launcher log
cat ~/.keepmeup.log
```

Copy the output and review it for error messages.
