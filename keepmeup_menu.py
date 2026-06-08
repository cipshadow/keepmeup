#!/usr/bin/env python3
"""KeepMeUp - Menu bar app to keep screen awake"""
import rumps
import subprocess
import sys
import os

# Hide from dock - must be before rumps.App
try:
    from AppKit import NSApplication, NSApplicationActivationPolicyAccessory
    NSApplication.sharedApplication().setActivationPolicy_(NSApplicationActivationPolicyAccessory)
except ImportError:
    pass

# Enable logging
LOG_FILE = os.path.expanduser("~/.keepmeup_app.log")

def log(msg):
    """Log messages to file"""
    with open(LOG_FILE, "a") as f:
        f.write(f"{msg}\n")

class KeepMeUp(rumps.App):
    def __init__(self):
        super(KeepMeUp, self).__init__("○", quit_button=None)
        self.enabled = False
        self.process = None

        log("KeepMeUp app initialized")

        # Create menu items
        self.menu = [
            rumps.MenuItem("Toggle Screen Awake", callback=self.toggle),
            None,  # Separator
            rumps.MenuItem("Quit", callback=self.quit_app)
        ]

        log("Menu items created")

    def toggle(self, sender):
        """Toggle screen awake on/off"""
        self.enabled = not self.enabled
        self.title = "◉" if self.enabled else "○"
        log(f"Toggled: {self.title}")

        if self.enabled:
            self.start_caffeinate()
            sender.title = "Turn Off"
        else:
            self.stop_caffeinate()
            sender.title = "Toggle Screen Awake"

    def start_caffeinate(self):
        """Start caffeinate process"""
        try:
            self.process = subprocess.Popen(
                ["caffeinate", "-d"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            log("caffeinate started")
        except Exception as e:
            log(f"Error starting caffeinate: {e}")
            rumps.notification("KeepMeUp Error", "Failed to enable", str(e))

    def stop_caffeinate(self):
        """Stop caffeinate process"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait()
                log("caffeinate stopped")
            except Exception as e:
                log(f"Error stopping caffeinate: {e}")
            self.process = None

    def quit_app(self, sender):
        """Quit the app"""
        self.stop_caffeinate()
        log("Quitting app")
        rumps.quit_app()


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
