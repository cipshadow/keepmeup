# KeepMeUp

A lightweight macOS menu bar app with two power modes: keep your screen awake,
or keep your Mac awake while letting the screen turn off.

The second mode is the useful one — long downloads, builds, or renders finish
without the machine idle-sleeping, while the display still switches off instead
of burning for hours.

## Features

- Jagged star icon in the menu bar, three states (off / screen awake / device awake)
- Two independent modes, click to toggle each on/off
- Uses native `caffeinate` and `pmset`, no kernel extensions or privileged helpers
- Self-contained app bundle: vendors its own Python venv, so the installed app
  keeps working no matter where it was built from or whether this repo still exists
- Minimal resource usage

## Requirements

- macOS 10.13 or later
- Python 3 (the system `python3` is fine)

## Install

```bash
git clone https://github.com/cipshadow/keepmeup.git
cd keepmeup
./install.sh
```

`install.sh` builds the app bundle (creating a private virtualenv inside it and
installing `rumps` and `pyobjc`), ad-hoc signs it, and copies it to
`~/Applications/KeepMeUp.app`.

Then launch it from Applications or Spotlight (Cmd+Space → "KeepMeUp").

The `.app` bundle is built, not committed, so it will not exist until you run
the install script.

## How to use

Launch the app and a jagged star icon (outline) appears in the menu bar. Click
it for three options:

- **Awake - screen on** — display and system both stay awake indefinitely.
  Icon becomes a glowing filled star.
- **Awake - screen off** — the Mac won't idle-sleep, but the display turns off
  after 1 minute of no input (and wakes on the next input, then turns off again
  after another idle minute). Icon becomes a plain filled star.
- **Off** — both stopped. Icon returns to the outline star.

"Quit" stops the app.

## Auto-start on login

```bash
./setup_autostart.sh
```

This adds the installed app to your login items. To disable it later:

```bash
launchctl unload ~/Library/LaunchAgents/com.local.keepmeup.plist
```

## Troubleshooting

**Nothing appears in the menu bar**

Check it's running, then check the logs:

```bash
ps aux | grep keepmeup_menu | grep -v grep
cat ~/.keepmeup.log
```

The launcher writes startup failures to `~/.keepmeup.log` and also surfaces
them as a dialog, so that log is the first place to look.

**The app crashes on launch, or the log mentions a missing venv or script**

The bundle is self-contained, so the usual fix is to rebuild it:

```bash
./install.sh
```

**Running the script directly (for development)**

```bash
python3 -m venv venv
source venv/bin/activate
pip install rumps pyobjc-framework-Cocoa
python3 keepmeup_menu.py
```

## Project structure

```
keepmeup/
├── keepmeup_menu.py          # the menu bar app
├── install.sh                # builds the .app bundle and installs it
├── setup_autostart.sh        # registers the LaunchAgent
├── verify.sh                 # post-install sanity checks
├── com.local.keepmeup.plist  # LaunchAgent template
└── assets/
    ├── generate_icons.py     # regenerates the icon PNGs (needs Pillow)
    ├── icon_*.png            # menu bar icons, checked in so install needs no Pillow
    └── AppIcon.icns          # app bundle icon
```

## License

MIT — see [LICENSE](LICENSE).
