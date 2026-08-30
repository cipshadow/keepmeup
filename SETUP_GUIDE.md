# Verifying KeepMeUp works

Install and usage are in the [README](README.md). This is the checklist for
confirming both power modes actually do what they claim, which is worth doing
once because the whole point of the app is behaviour you only notice by
*not* seeing it happen.

## Automated check

```bash
./verify.sh
```

Confirms the app bundle exists, its vendored virtualenv is intact, `rumps` is
importable, and `keepmeup_menu.py` compiles.

## Manual checks

### 1. The menu bar icon

Look at the top right of your screen, near the clock. You should see a jagged
star in one of three states:

| Icon | Meaning |
|------|---------|
| Outline star | Both modes off |
| Glowing filled star | Awake - screen on |
| Plain filled star | Awake - screen off |

### 2. The menu

Click the icon. You should get "Awake - screen on", "Awake - screen off", and
"Quit".

### 3. Awake - screen on

1. Click "Awake - screen on" — the icon becomes a glowing filled star
2. Step away and wait past your normal display-sleep timeout
3. The screen should still be on

Click it again to turn it off; the icon returns to the outline star.

### 4. Awake - screen off

1. Click "Awake - screen off" — the icon becomes a plain filled star
2. Don't touch the mouse or keyboard for about a minute — the display should
   turn itself off
3. Move the mouse — the display wakes
4. Stay idle again — after another minute it turns off again

Throughout, the Mac itself stays awake, so anything running keeps running.

## If something is wrong

**Nothing happens when you click the icon**

```bash
pkill -f keepmeup_menu.py
open ~/Applications/KeepMeUp.app
```

**The icon never appears**

The app may be running with its icon hidden behind other menu bar items —
check with `pgrep -f keepmeup_menu.py`. If it is running, try removing some
menu bar icons or using a menu bar manager.

**It crashes on launch**

The launcher logs startup failures and shows a dialog. Check the log, then
rebuild:

```bash
cat ~/.keepmeup.log
./install.sh
```
