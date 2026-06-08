# KeepMeUp 

A lightweight macOS menu bar app that keeps your screen awake when enabled.

## Features

- 💤/✨ Toggle switch in the menu bar (top toolbar)
- One-click enable/disable screen sleep prevention
- Uses native `caffeinate` command
- Zero additional dependencies
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

1. Launch the app - you should see **○** appear in your menu bar (top right)
2. **Click the menu bar icon** to toggle between:
   - **○** = Screen can sleep normally  
   - **◉** = Screen stays awake indefinitely
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
