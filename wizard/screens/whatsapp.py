"""
Screen 6 — WhatsApp Setup (stub)
Full implementation: check Waydroid state, initialise session, launch Play Store.
"""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

import subprocess
from screens.base import BaseScreen


class WhatsappScreen(BaseScreen):
    def __init__(self, on_next=None, on_back=None, **kwargs):
        super().__init__(on_next=on_next, on_back=on_back, **kwargs)

        status_page = Adw.StatusPage()
        status_page.set_vexpand(True)
        status_page.set_icon_name("chat-symbolic")
        status_page.set_title("Set up WhatsApp?")
        status_page.set_description(
            "WhatsApp runs via Waydroid, our Android compatibility layer.\n\n"
            "We'll open the app store so you can install it. "
            "This takes a minute or two on first run."
        )
        self.content_box.append(status_page)

        # Launch button
        self.launch_btn = Gtk.Button(label="Open app store")
        self.launch_btn.add_css_class("suggested-action")
        self.launch_btn.add_css_class("pill")
        self.launch_btn.connect("clicked", lambda _: self._launch_waydroid())
        self.content_box.append(self.launch_btn)

        self.status_label = Gtk.Label()
        self.status_label.set_wrap(True)
        self.status_label.set_halign(Gtk.Align.CENTER)
        self.status_label.set_visible(False)
        self.content_box.append(self.status_label)

        stub_note = Gtk.Label(label="⚙️  Waydroid state detection coming soon")
        stub_note.add_css_class("caption")
        stub_note.add_css_class("dim-label")
        stub_note.set_halign(Gtk.Align.CENTER)
        self.content_box.append(stub_note)

        self.build_nav_buttons(next_label="Continue", show_back=True)
        # Skip is effectively "Continue" — both just move forward
        skip_btn = Gtk.Button(label="Skip for now")
        skip_btn.add_css_class("flat")
        skip_btn.connect("clicked", lambda _: on_next())
        self.nav_box.prepend(skip_btn)

    def _launch_waydroid(self):
        """
        STUB: In full implementation:
        1. Check if Waydroid is initialised (waydroid status)
        2. If not, run waydroid init
        3. Start session (waydroid session start)
        4. Launch Play Store (waydroid app launch com.android.vending)
        """
        self.launch_btn.set_sensitive(False)
        self.status_label.set_text("Starting Waydroid…")
        self.status_label.set_visible(True)

        try:
            # TODO: replace stub with real implementation
            # subprocess.run(["waydroid", "session", "start"], check=True)
            # subprocess.run(["waydroid", "app", "launch", "com.android.vending"])
            self.status_label.set_text(
                "⚙️  Waydroid launch is stubbed — will work on device"
            )
        except FileNotFoundError:
            self.status_label.set_text("Waydroid not found. Install it first via Settings.")
        except subprocess.CalledProcessError as e:
            self.status_label.set_text(f"Couldn't start Waydroid: {e}")

        self.launch_btn.set_sensitive(True)
