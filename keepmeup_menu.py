#!/usr/bin/env python3
"""KeepMeUp - Menu bar app with two power modes: keep the screen awake, or
keep the Mac awake while letting the screen turn off (and actively force the
screen off after a short idle period, waking on input like normal)."""
import os
import re
import subprocess
import sys

import rumps

# Hide from dock - must be before rumps.App
try:
    from AppKit import NSApplication, NSApplicationActivationPolicyAccessory
    NSApplication.sharedApplication().setActivationPolicy_(NSApplicationActivationPolicyAccessory)
except ImportError:
    pass

# Enable logging
LOG_FILE = os.path.expanduser("~/.keepmeup_app.log")

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

MODE_OFF = "off"
MODE_SCREEN_AWAKE = "screen_awake"
MODE_DEVICE_AWAKE = "device_awake"

# How long the mouse/keyboard can be idle before we force the display off in
# MODE_DEVICE_AWAKE, and how often we poll for idle time.
IDLE_OFF_THRESHOLD_SECONDS = 60
IDLE_POLL_INTERVAL_SECONDS = 5
# Idle time below this is treated as "fresh input just happened" so the
# force-off can re-arm for the next idle stretch.
IDLE_RESET_THRESHOLD_SECONDS = 3

HID_IDLE_TIME_RE = re.compile(r'"HIDIdleTime"\s*=\s*(\d+)')


def log(msg):
    """Log messages to file"""
    with open(LOG_FILE, "a") as f:
        f.write(f"{msg}\n")


def get_idle_seconds():
    """Seconds since the last mouse/keyboard input, via ioreg's HIDIdleTime (ns)."""
    try:
        out = subprocess.run(
            ["ioreg", "-c", "IOHIDSystem"],
            capture_output=True, text=True, check=True
        ).stdout
        match = HID_IDLE_TIME_RE.search(out)
        if not match:
            return 0
        return int(match.group(1)) / 1_000_000_000
    except Exception as e:
        log(f"Error reading idle time: {e}")
        return 0


class KeepMeUp(rumps.App):
    def __init__(self):
        super(KeepMeUp, self).__init__(
            "",
            icon=os.path.join(ASSETS_DIR, "icon_off.png"),
            template=True,
            quit_button=None,
        )
        self.mode = MODE_OFF
        self.process = None
        self.idle_timer = None
        self.screen_forced_off = False

        log("KeepMeUp app initialized")

        self.screen_awake_item = rumps.MenuItem(
            "Awake - screen on", callback=self.select_screen_awake
        )
        self.device_awake_item = rumps.MenuItem(
            "Awake - screen off", callback=self.select_device_awake
        )
        self.off_item = rumps.MenuItem(
            "Off", callback=self.select_off
        )
        self.off_item.state = True

        self.menu = [
            self.screen_awake_item,
            self.device_awake_item,
            self.off_item,
            None,  # Separator
            rumps.MenuItem("Quit", callback=self.quit_app)
        ]

        log("Menu items created")

    # -- menu callbacks ---------------------------------------------------

    def select_screen_awake(self, sender):
        self.stop_all()
        self.start_screen_awake()

    def select_device_awake(self, sender):
        self.stop_all()
        self.start_device_awake()

    def select_off(self, sender):
        self.stop_all()

    def quit_app(self, sender):
        """Quit the app"""
        self.stop_all()
        log("Quitting app")
        rumps.quit_application()

    # -- mode transitions ---------------------------------------------------

    def start_screen_awake(self):
        """Prevent both display sleep and idle system sleep."""
        try:
            self.process = subprocess.Popen(
                ["caffeinate", "-d", "-i"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.mode = MODE_SCREEN_AWAKE
            self.screen_awake_item.state = True
            self.device_awake_item.state = False
            self.off_item.state = False
            self._set_icon("icon_screen_awake.png", template=False)
            log("Screen Awake mode started (caffeinate -d -i)")
        except Exception as e:
            log(f"Error starting screen-awake mode: {e}")
            rumps.notification("KeepMeUp Error", "Failed to enable", str(e))

    def start_device_awake(self):
        """Prevent idle system sleep only; actively cycle the display off/on."""
        try:
            self.process = subprocess.Popen(
                ["caffeinate", "-i"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.mode = MODE_DEVICE_AWAKE
            self.device_awake_item.state = True
            self.screen_awake_item.state = False
            self.off_item.state = False
            self._set_icon("icon_device_awake.png", template=True)
            self.screen_forced_off = False
            self.idle_timer = rumps.Timer(self._poll_idle, IDLE_POLL_INTERVAL_SECONDS)
            self.idle_timer.start()
            log("Device Awake mode started (caffeinate -i, idle-off polling armed)")
        except Exception as e:
            log(f"Error starting device-awake mode: {e}")
            rumps.notification("KeepMeUp Error", "Failed to enable", str(e))

    def stop_all(self):
        """Tear down whatever mode is currently active."""
        if self.idle_timer is not None:
            try:
                self.idle_timer.stop()
            except Exception as e:
                log(f"Error stopping idle timer: {e}")
            self.idle_timer = None

        if self.process:
            try:
                self.process.terminate()
                self.process.wait()
                log("caffeinate stopped")
            except Exception as e:
                log(f"Error stopping caffeinate: {e}")
            self.process = None

        self.screen_awake_item.state = False
        self.device_awake_item.state = False
        self.off_item.state = True
        self.screen_forced_off = False
        self.mode = MODE_OFF
        self._set_icon("icon_off.png", template=True)
        log("All modes stopped")

    # -- idle polling for MODE_DEVICE_AWAKE ---------------------------------

    def _poll_idle(self, sender):
        if self.mode != MODE_DEVICE_AWAKE:
            return

        idle_seconds = get_idle_seconds()

        if not self.screen_forced_off and idle_seconds >= IDLE_OFF_THRESHOLD_SECONDS:
            try:
                subprocess.run(["pmset", "displaysleepnow"], check=True)
                self.screen_forced_off = True
                log(f"Idle {idle_seconds:.0f}s >= {IDLE_OFF_THRESHOLD_SECONDS}s — forced display off")
            except Exception as e:
                log(f"Error forcing display off: {e}")
        elif self.screen_forced_off and idle_seconds < IDLE_RESET_THRESHOLD_SECONDS:
            # Fresh input detected (macOS already woke the display for us) —
            # re-arm so the next idle stretch forces it off again.
            self.screen_forced_off = False
            log("Input detected — re-armed idle-off timer")

    # -- icon ---------------------------------------------------------------

    def _set_icon(self, filename, template):
        self.icon = os.path.join(ASSETS_DIR, filename)
        self.template = template


if __name__ == "__main__":
    try:
        # Clear old log
        with open(LOG_FILE, "w") as f:
            f.write(f"KeepMeUp started at {os.path.expanduser('~')}\n")

        log("Creating KeepMeUp instance...")
        app = KeepMeUp()
        log("Running app...")
        app.run()
        log("App exited normally")
    except Exception as e:
        log(f"Fatal error: {e}")
        import traceback
        log(traceback.format_exc())
        sys.stderr.write(f"Error: {e}\n")
        # Don't exit, try to stay running
        try:
            import time
            time.sleep(60)
        except:
            pass
        sys.exit(1)
