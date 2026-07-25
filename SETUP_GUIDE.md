# KeepMeUp Setup & Verification Guide

## Installation

Your KeepMeUp app is ready! Choose how to launch it:

### Option 1: Quick Launch (Right Now)
```bash
open ~/keepmeup/KeepMeUp.app
```

### Option 2: Install to Applications (Recommended)
```bash
bash ~/keepmeup/install.sh
```

Then find it in Spotlight (Cmd+Space → "KeepMeUp") or in Applications folder.

---

## ✅ Verification Checklist

After launching the app, do these checks:

### 1. Look for the menu bar icon
Look at the **very top right** of your screen near the clock and Wifi icon.
You should see a jagged star icon in one of three states:
- **Outline star** = both modes off
- **Glowing filled star** = Awake - screen on is on
- **Plain filled star** = Awake - screen off is on

### 2. Check the menu
- Click the icon
- You should see a menu with:
  - "Awake - screen on"
  - "Awake - screen off"
  - "Quit"

### 3. Test Awake - screen on
- Click "Awake - screen on" — icon becomes a glowing filled star
- Your screen and Mac should now stay awake indefinitely
- Move away from your Mac and wait - normally the screen would sleep, but now it won't
- Click it again to turn it off (icon returns to outline)

### 4. Test Awake - screen off
- Click "Awake - screen off" — icon becomes a plain filled star
- Don't touch the mouse/keyboard for about a minute — the display should turn off on its own
- Move the mouse — the display wakes up
- Stay idle again — after another minute, it turns off again

---

## 🔧 Troubleshooting

### Problem: Nothing happens when I click the icon

**Solution 1: Restart the app**
```bash
pkill -f keepmeup_menu.py
open ~/keepmeup/KeepMeUp.app
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
cd ~/keepmeup
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
| Outline star | Both modes off |
| Glowing filled star | Awake - screen on is on |
| Plain filled star | Awake - screen off is on |

**To verify Awake - screen on works:**
1. Click "Awake - screen on"
2. Step away from your Mac
3. Wait 5 minutes
4. Screen should still be on (normally it would sleep after ~5 min)

**To verify Awake - screen off works:**
1. Click "Awake - screen off"
2. Don't touch anything for about a minute
3. Screen should turn off on its own, Mac stays reachable/running
4. Move the mouse — screen wakes immediately

---

## 🔄 Auto-start at Login

To make KeepMeUp automatically launch every time you turn on your Mac:

```bash
bash ~/keepmeup/setup_autostart.sh
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
