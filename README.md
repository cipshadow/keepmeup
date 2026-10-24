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
- Self-contained universal app bundle for Intel and Apple Silicon Macs
- Minimal resource usage

## Requirements

- macOS 13 Ventura or later
- Intel or Apple Silicon Mac

## Install

1. Download `KeepMeUp-<version>-universal2.dmg` from the latest
   [GitHub release](https://github.com/cipshadow/keepmeup/releases).
2. Open the DMG and drag **KeepMeUp** to Applications.
3. Control-click KeepMeUp in Applications, choose **Open**, then choose
   **Open** again. This is required once per downloaded version because these
   releases are unsigned and not notarized.

The released app includes Python and all dependencies. It keeps working after
you delete the DMG or repository, and it does not need Homebrew or Python on
the Mac.

### Build from source

Building needs Python 3.10 through 3.13. That requirement is only for people
building a release, never for people running the downloaded app.

```bash
git clone https://github.com/cipshadow/keepmeup.git
cd keepmeup
./install.sh
```

`install.sh` builds an app with PyInstaller and copies it to
`~/Applications/KeepMeUp.app`.

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

For a downloaded release, open **System Settings → General → Login Items** and
add KeepMeUp under **Open at Login**.

For a source checkout, you can instead install the included LaunchAgent:

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
pgrep -fl 'KeepMeUp.app/Contents/MacOS/KeepMeUp'
cat ~/.keepmeup_app.log
```

The app writes startup failures to `~/.keepmeup_app.log` and also surfaces
them as a dialog, so that log is the first place to look.

**macOS says it cannot verify the app**

Control-click the app in Applications, choose **Open**, then choose **Open**
again. This is the expected first-launch flow for an unsigned release.

**The app crashes on launch**

The bundle is self-contained, so the usual fix is to rebuild it:

```bash
./install.sh
```

**Running the script directly (for development)**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 keepmeup_menu.py
```

## Project structure

```
keepmeup/
├── keepmeup_menu.py          # the menu bar app
├── install.sh                # builds and installs a PyInstaller app
├── scripts/build_release.sh  # creates the universal app, DMG, and checksum
├── requirements-build.txt    # PyInstaller build dependency
├── .github/workflows/release.yml # GitHub release automation
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
