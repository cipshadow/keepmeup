# KeepMeUp 

A lightweight macOS menu bar app with two power modes: keep your screen awake,
or keep your Mac awake while letting the screen turn off.

## Features

- Jagged star icon in the menu bar, three states (off / screen awake / device awake)
- Two independent modes, click to toggle each on/off
- Uses native `caffeinate` and `pmset` commands
- Self-contained app bundle (vendors its own Python venv — no external dependency on this repo's location)
- Minimal resource usage

## Quick Start

### Run from project directory

```bash
open ~/keepmeup/KeepMeUp.app
```

### Install to Applications folder

```bash
bash ~/keepmeup/install.sh
```

Or manually:
```bash
cp -r ~/keepmeup/KeepMeUp.app ~/Applications/
```

Then launch from Applications or Spotlight (Cmd+Space → "KeepMeUp").

## How to use

1. Launch the app — a jagged star icon (outline) appears in your menu bar (top right)
2. Click the icon to open the menu, with three options:
   - **Awake - screen on** — display and system both stay awake indefinitely.
     Icon becomes a glowing filled star.
   - **Awake - screen off** — the Mac won't idle-sleep, but the
     display is actively turned off after 1 minute of no mouse/keyboard input
     (and wakes normally on the next input, then turns off again after another
     minute of inactivity). Icon becomes a plain filled star.
   - **Off** — both stopped. Icon returns to the outline star.
3. Select "Quit" from the menu to stop the app

## Auto-start on login

To make KeepMeUp launch automatically when you turn on your Mac:

```bash
bash ~/keepmeup/setup_autostart.sh
```

This adds the app to your login items. To disable it later:

```bash
launchctl unload ~/Library/LaunchAgents/com.local.keepmeup.plist
```

## Troubleshooting

### Nothing appears in the menu bar

If you don't see the KeepMeUp icon in the menu bar:

1. Check that the app is actually running:
```bash
ps aux | grep keepmeup_menu | grep -v grep
```

2. Check the app logs:
```bash
cat ~/.keepmeup_app.log
cat ~/.keepmeup.log
```

3. If you see errors about missing files, try rebuilding:
```bash
bash ~/keepmeup/install.sh
```

### The app crashes on launch

1. Make sure Python and the virtual environment are set up:
```bash
cd ~/keepmeup
python3 -m venv venv
source venv/bin/activate
pip install rumps
```

2. Test the app directly:
```bash
source ~/keepmeup/venv/bin/activate
python3 ~/keepmeup/keepmeup_menu.py
```

## Project Structure

```
~/keepmeup/
├── KeepMeUp.app/              # The app (menu bar)
├── keepmeup_menu.py           # Main app code
├── venv/                      # Python virtual environment
├── install.sh                 # Install to ~/Applications
└── README.md                  # This file
```
