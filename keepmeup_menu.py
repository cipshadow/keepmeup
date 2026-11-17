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

# PyInstaller places bundled data in ``sys._MEIPASS``. Keep the normal
# source-tree path for development, so running this file directly still works.
ASSETS_DIR = os.path.join(
    getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__))), "assets"
)

MODE_OFF = "off"
MODE_SCREEN_AWAKE = "screen_awake"
MODE_DEVICE_AWAKE = "device_awake"

TIMER_ACTION_OFF = "off"
TIMER_ACTION_SCREEN_OFF = "screen_off"
TIMER_ACTION_LOCK = "lock"

CGSESSION_PATH = (
    "/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession"
)

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
        self.mode_timer = None
        self.timer_action = None
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

        self.timer_menu = rumps.MenuItem("Timer")
        self.start_timer_item = rumps.MenuItem(
            "Start timer…", callback=self.configure_timer
        )
        self.cancel_timer_item = rumps.MenuItem(
            "Cancel timer", callback=self.cancel_timer
        )
        self.timer_menu.add(self.start_timer_item)
        self.timer_menu.add(self.cancel_timer_item)

        self.menu = [
            self.screen_awake_item,
            self.device_awake_item,
            self.off_item,
            None,  # Separator
            self.timer_menu,
            None,  # Separator
            rumps.MenuItem("Quit", callback=self.quit_app)
        ]

        log("Menu items created")

    # -- menu callbacks ---------------------------------------------------

    def select_screen_awake(self, sender):
        self._cancel_timer("Mode changed manually")
        self.stop_all()
        self.start_screen_awake()

    def select_device_awake(self, sender):
        self._cancel_timer("Mode changed manually")
        self.stop_all()
        self.start_device_awake()

    def select_off(self, sender):
        self._cancel_timer("Mode changed manually")
        self.stop_all()

    def quit_app(self, sender):
        """Quit the app"""
        self._cancel_timer()
        self.stop_all()
        log("Quitting app")
        rumps.quit_application()

    # -- timer ------------------------------------------------------------

    def configure_timer(self, sender):
        """Choose a mode, duration, and expiry action in native macOS dialogs."""
        mode = self._choose_from_list(
            "KeepMeUp timer",
            "Which mode should run while the timer is active?",
            [("Awake - screen on", MODE_SCREEN_AWAKE),
             ("Awake - screen off", MODE_DEVICE_AWAKE)],
        )
        if mode is None:
            return

        minutes = self._ask_timer_minutes()
        if minutes is None:
            return

        action = self._choose_from_list(
            "When the timer ends",
            "What should happen when the timer ends?",
            [("Turn KeepMeUp off", TIMER_ACTION_OFF),
             ("Awake - screen off", TIMER_ACTION_SCREEN_OFF),
             ("Lock Mac", TIMER_ACTION_LOCK)],
        )
        if action is None:
            return

        self._cancel_timer()
        self.stop_all()
        if mode == MODE_SCREEN_AWAKE:
            mode_started = self.start_screen_awake()
        else:
            mode_started = self.start_device_awake()
        if not mode_started:
            return

        self.timer_action = action
        self.mode_timer = rumps.Timer(self._timer_expired, minutes * 60)
        self.mode_timer.start()
        self.cancel_timer_item.title = "Cancel active timer"
        rumps.notification(
            "KeepMeUp timer started",
            f"{self._mode_title(mode)} for {minutes} minute{'s' if minutes != 1 else ''}",
            f"Then: {self._timer_action_title(action)}",
        )
        log(f"Timer started: {mode} for {minutes} minutes, then {action}")

    def cancel_timer(self, sender):
        if not self._cancel_timer("Timer cancelled"):
            rumps.notification("KeepMeUp timer", "No active timer", "")

    def _cancel_timer(self, notification_body=None):
        if self.mode_timer is None:
            return False
        try:
            self.mode_timer.stop()
        except Exception as e:
            log(f"Error stopping mode timer: {e}")
        self.mode_timer = None
        self.timer_action = None
        self.cancel_timer_item.title = "Cancel timer"
        if notification_body:
            rumps.notification("KeepMeUp timer cancelled", notification_body, "")
        log("Timer cancelled")
        return True

    def _timer_expired(self, sender):
        action = self.timer_action
        self._cancel_timer()
        self._apply_timer_expiry(action)
        log(f"Timer expired: {action}")

    def _apply_timer_expiry(self, action):
        if action == TIMER_ACTION_SCREEN_OFF:
            self.stop_all()
            if self.start_device_awake():
                rumps.notification("KeepMeUp timer finished", "Awake - screen off enabled", "")
        elif action == TIMER_ACTION_LOCK:
            self.stop_all()
            self._lock_mac()
        else:
            self.stop_all()
            rumps.notification("KeepMeUp timer finished", "KeepMeUp turned off", "")

    def _lock_mac(self):
        try:
            subprocess.run([CGSESSION_PATH, "-suspend"], check=True)
            log("Mac locked after timer expiry")
        except Exception as e:
            log(f"Error locking Mac: {e}")
            rumps.notification("KeepMeUp Error", "Failed to lock Mac", str(e))

    @staticmethod
    def _mode_title(mode):
        return "Awake - screen on" if mode == MODE_SCREEN_AWAKE else "Awake - screen off"

    @staticmethod
    def _timer_action_title(action):
        return {
            TIMER_ACTION_OFF: "Turn KeepMeUp off",
            TIMER_ACTION_SCREEN_OFF: "Awake - screen off",
            TIMER_ACTION_LOCK: "Lock Mac",
        }[action]

    @staticmethod
    def _choose_from_list(title, prompt, choices):
        labels = [label for label, _ in choices]
        quoted_labels = ", ".join(f'"{label}"' for label in labels)
        script = (
            f"choose from list {{{quoted_labels}}} with title \"{title}\" "
            f"with prompt \"{prompt}\""
        )
        result = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True
        )
        if result.returncode != 0:
            return None
        selected = result.stdout.strip()
        return next((value for label, value in choices if label == selected), None)

    @staticmethod
    def _ask_timer_minutes():
        script = (
            'display dialog "How many minutes should this mode run?" '
            'default answer "120" buttons {"Cancel", "Start"} '
            'default button "Start"'
        )
        result = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True
        )
        match = re.search(r"text returned:(.+)$", result.stdout.strip())
        if result.returncode != 0 or not match:
            return None
        try:
            minutes = int(match.group(1).strip())
        except ValueError:
            rumps.notification("KeepMeUp timer", "Enter a whole number of minutes", "")
            return None
        if minutes < 1:
            rumps.notification("KeepMeUp timer", "Duration must be at least one minute", "")
            return None
        return minutes

    # -- mode transitions ---------------------------------------------------

    def start_screen_awake(self):
        """Prevent both display sleep and idle system sleep."""
        try:
            self.process = subprocess.Popen(
                ["caffeinate", "-d", "-i", "-w", str(os.getpid())],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.mode = MODE_SCREEN_AWAKE
            self.screen_awake_item.state = True
            self.device_awake_item.state = False
            self.off_item.state = False
            self._set_icon("icon_screen_awake.png", template=True)
            log("Screen Awake mode started (caffeinate -d -i)")
            return True
        except Exception as e:
            log(f"Error starting screen-awake mode: {e}")
            rumps.notification("KeepMeUp Error", "Failed to enable", str(e))
            return False

    def start_device_awake(self):
        """Prevent idle system sleep only; actively cycle the display off/on."""
        try:
            self.process = subprocess.Popen(
                ["caffeinate", "-i", "-w", str(os.getpid())],
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
            return True
        except Exception as e:
            log(f"Error starting device-awake mode: {e}")
            rumps.notification("KeepMeUp Error", "Failed to enable", str(e))
            return False

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
        try:
            dialog = (
                'display dialog "KeepMeUp failed to start. '
                'See ~/.keepmeup_app.log for details." '
                'buttons {"OK"} with icon stop with title "KeepMeUp"'
            )
            subprocess.run(
                ["osascript", "-e", dialog],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                check=False,
            )
        except Exception as dialog_error:
            log(f"Error showing fatal error dialog: {dialog_error}")
        sys.exit(1)
