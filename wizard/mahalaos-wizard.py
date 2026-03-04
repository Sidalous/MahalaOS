#!/usr/bin/env python3
"""
MahalaOS Setup Wizard
First-boot setup experience for MahalaOS (postmarketOS consumer layer)
"""

import sys
import os
import argparse
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, Gio, GLib

# Add wizard directory to path for screen imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from screens.welcome import WelcomeScreen
from screens.language import LanguageScreen
from screens.wifi import WifiScreen
from screens.sim import SimScreen
from screens.honest import HonestScreen
from screens.whatsapp import WhatsappScreen
from screens.done import DoneScreen

WIZARD_COMPLETE_FLAG = "/var/lib/mahalaos/wizard-complete"

SCREEN_ORDER = [
    "welcome",
    "language",
    "wifi",
    "sim",
    "honest",
    "whatsapp",
    "done",
]


class MahalaWizard(Adw.Application):
    def __init__(self, dev_mode=False):
        super().__init__(
            application_id="org.mahalaos.Wizard",
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )
        self.dev_mode = dev_mode
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        # Check if wizard has already been completed (skip in dev mode)
        if not self.dev_mode and os.path.exists(WIZARD_COMPLETE_FLAG):
            print("Wizard already completed. Run with --dev to bypass.")
            self.quit()
            return

        self.window = MahalaWizardWindow(application=self, dev_mode=self.dev_mode)
        self.window.present()


class MahalaWizardWindow(Adw.ApplicationWindow):
    def __init__(self, dev_mode=False, **kwargs):
        super().__init__(**kwargs)
        self.dev_mode = dev_mode
        self.current_screen_index = 0

        self.set_title("MahalaOS Setup")
        self.set_default_size(360, 760)  # OnePlus 6T: 1080x2340, but GTK scales
        self.set_resizable(False)

        # Prevent closing mid-wizard (user must complete or use --dev)
        if not self.dev_mode:
            self.connect("close-request", self._on_close_request)

        # Main stack for screen navigation
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
        self.stack.set_transition_duration(300)

        # Instantiate all screens, passing the navigation callback
        self.screens = {
            "welcome": WelcomeScreen(on_next=self.go_next),
            "language": LanguageScreen(on_next=self.go_next, on_back=self.go_back),
            "wifi": WifiScreen(on_next=self.go_next, on_back=self.go_back),
            "sim": SimScreen(on_next=self.go_next, on_back=self.go_back),
            "honest": HonestScreen(on_next=self.go_next, on_back=self.go_back),
            "whatsapp": WhatsappScreen(on_next=self.go_next, on_back=self.go_back),
            "done": DoneScreen(on_finish=self.finish_wizard),
        }

        for name, screen in self.screens.items():
            self.stack.add_named(screen, name)

        # Show the first screen
        self.stack.set_visible_child_name(SCREEN_ORDER[0])

        # Wrap in a simple box (allows adding a header bar later if needed)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.append(self.stack)

        self.set_content(box)

    def go_next(self):
        if self.current_screen_index < len(SCREEN_ORDER) - 1:
            self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
            self.current_screen_index += 1
            next_name = SCREEN_ORDER[self.current_screen_index]
            self.stack.set_visible_child_name(next_name)

            # Notify screen it's becoming active (for lazy init)
            screen = self.screens[next_name]
            if hasattr(screen, "on_enter"):
                screen.on_enter()

    def go_back(self):
        if self.current_screen_index > 0:
            self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_RIGHT)
            self.current_screen_index -= 1
            prev_name = SCREEN_ORDER[self.current_screen_index]
            self.stack.set_visible_child_name(prev_name)

    def finish_wizard(self):
        """Called when user completes the wizard."""
        if not self.dev_mode:
            try:
                os.makedirs(os.path.dirname(WIZARD_COMPLETE_FLAG), exist_ok=True)
                with open(WIZARD_COMPLETE_FLAG, "w") as f:
                    f.write("done\n")
            except PermissionError:
                # polkit/systemd should ensure this is writable; log and continue
                print(
                    f"Warning: could not write wizard flag to {WIZARD_COMPLETE_FLAG}"
                )
        self.close()

    def _on_close_request(self, window):
        # Block window close — user must complete the wizard
        # In production this prevents accidental dismissal on first boot
        return True  # True = block the close


def main():
    parser = argparse.ArgumentParser(description="MahalaOS Setup Wizard")
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Developer mode: bypass completion flag check, allow closing",
    )
    args = parser.parse_args()

    app = MahalaWizard(dev_mode=args.dev)
    return app.run(None)  # Don't pass sys.argv — argparse has consumed it


if __name__ == "__main__":
    sys.exit(main())
