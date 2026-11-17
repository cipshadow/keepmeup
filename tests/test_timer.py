import importlib.util
import sys
import types
import unittest
from pathlib import Path


class FakeTimer:
    def __init__(self, callback, interval):
        self.callback = callback
        self.interval = interval
        self.started = False
        self.stopped = False

    def start(self):
        self.started = True

    def stop(self):
        self.stopped = True


class FakeApp:
    def __init__(self, *args, **kwargs):
        pass


class FakeMenuItem:
    def __init__(self, title, callback=None):
        self.title = title
        self.callback = callback
        self.state = False


def load_app_module():
    fake_application = types.SimpleNamespace(setActivationPolicy_=lambda policy: None)
    fake_rumps = types.SimpleNamespace(
        App=FakeApp,
        MenuItem=FakeMenuItem,
        Timer=FakeTimer,
        notification=lambda *args: None,
        quit_application=lambda: None,
    )
    sys.modules["rumps"] = fake_rumps
    sys.modules["AppKit"] = types.SimpleNamespace(
        NSApplication=types.SimpleNamespace(sharedApplication=lambda: fake_application),
        NSApplicationActivationPolicyAccessory=1,
    )
    module_path = Path(__file__).parents[1] / "keepmeup_menu.py"
    spec = importlib.util.spec_from_file_location("keepmeup_menu_under_test", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TimerExpiryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app_module = load_app_module()

    def setUp(self):
        self.app = self.app_module.KeepMeUp.__new__(self.app_module.KeepMeUp)
        self.events = []
        self.app.stop_all = lambda: self.events.append("off")
        self.app.start_device_awake = lambda: self.events.append("screen-off")
        self.app._lock_mac = lambda: self.events.append("lock")

    def test_lock_expiry_disables_keepmeup_before_locking(self):
        self.app._apply_timer_expiry(self.app_module.TIMER_ACTION_LOCK)

        self.assertEqual(self.events, ["off", "lock"])

    def test_screen_off_expiry_replaces_the_current_mode(self):
        self.app._apply_timer_expiry(self.app_module.TIMER_ACTION_SCREEN_OFF)

        self.assertEqual(self.events, ["off", "screen-off"])

    def test_off_expiry_disables_keepmeup(self):
        self.app._apply_timer_expiry(self.app_module.TIMER_ACTION_OFF)

        self.assertEqual(self.events, ["off"])

    def test_timer_is_not_scheduled_when_its_mode_cannot_start(self):
        choices = iter([
            self.app_module.MODE_SCREEN_AWAKE,
            self.app_module.TIMER_ACTION_OFF,
        ])
        self.app._choose_from_list = lambda *args: next(choices)
        self.app._ask_timer_minutes = lambda: 5
        self.app._cancel_timer = lambda notification_body=None: False
        self.app.stop_all = lambda: None
        self.app.start_screen_awake = lambda: False
        self.app.cancel_timer_item = FakeMenuItem("Cancel timer")
        self.app.mode_timer = None

        self.app.configure_timer(None)

        self.assertIsNone(self.app.mode_timer)


if __name__ == "__main__":
    unittest.main()
