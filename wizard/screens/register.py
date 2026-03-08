"""
Screen 6b — Device Registration
Optional, anonymous registration. Fire-and-forget POST to register.mahalaos.org.
Uses hardware-derived UUID from device_uuid.py and registration_client.py.
Copy adapts based on install_type (home / franchise / oem).
"""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib

import threading

from screens.base import BaseScreen
from install_config import read_install_config

# Import the proper registration client from the server/ module.
# device_uuid.py and registration_client.py must be copied into the wizard/
# directory alongside this file (or into wizard/screens/).
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from registration_client import register_device, skip_registration, get_registration_status
from device_uuid import get_device_uuid


# ── Copy variants by install_type ─────────────────────────────────────────────

COPY = {
    "home": {
        "heading":  "Help MahalaOS grow",
        "body":     "Register your device anonymously. We store only a hardware-derived "
                    "device ID — no name, email, or location. Ever.",
        "register": "Register my device",
        "skip":     "Skip",
    },
    "franchise": {
        "heading":  "Help MahalaOS grow",
        "body":     "Register your device anonymously. We store only a hardware-derived "
                    "device ID — no name, email, or location. Ever.",
        "register": "Register my device",
        "skip":     "Skip",
    },
    "oem": {
        "heading":  "Welcome to the MahalaOS community",
        "body":     "Join the MahalaOS community. We store only a hardware-derived "
                    "device ID — no name, email, or location. Ever.",
        "register": "Join the community",
        "skip":     "Skip for now",
    },
}


class RegisterScreen(BaseScreen):
    def __init__(self, on_next=None, on_back=None, **kwargs):
        super().__init__(on_next=on_next, on_back=on_back, **kwargs)

        self.config = read_install_config()
        install_type = self.config.get("install_type", "home")
        copy = COPY.get(install_type, COPY["home"])

        # ── Already registered? Skip straight through ─────────────────────────
        if get_registration_status() == "registered":
            GLib.idle_add(self._advance)
            return

        # ── Status page ───────────────────────────────────────────────────────
        status_page = Adw.StatusPage()
        status_page.set_vexpand(True)
        status_page.set_icon_name("system-users-symbolic")
        status_page.set_title(copy["heading"])
        status_page.set_description(copy["body"])
        self.content_box.append(status_page)

        # ── Privacy reassurance rows ──────────────────────────────────────────
        privacy_group = Adw.PreferencesGroup()
        for title, icon, subtitle in [
            ("No personal data",     "user-info-symbolic",        "No name, email, or account required."),
            ("No location tracking", "find-location-symbolic",    "We never read your GPS or IP address."),
            ("One ping only",        "network-transmit-symbolic", "Sent once on setup. Never again."),
        ]:
            row = Adw.ActionRow()
            row.set_title(title)
            row.set_subtitle(subtitle)
            row.set_icon_name(icon)
            privacy_group.add(row)
        self.content_box.append(privacy_group)

        # ── Feedback label ────────────────────────────────────────────────────
        self.feedback = Gtk.Label()
        self.feedback.set_wrap(True)
        self.feedback.set_halign(Gtk.Align.CENTER)
        self.feedback.set_margin_top(8)
        self.feedback.set_visible(False)
        self.content_box.append(self.feedback)

        # ── Register button ───────────────────────────────────────────────────
        self.register_btn = Gtk.Button(label=copy["register"])
        self.register_btn.add_css_class("suggested-action")
        self.register_btn.add_css_class("pill")
        self.register_btn.connect("clicked", lambda _: self._start_registration())
        self.append(self.register_btn)

        # ── Skip button ───────────────────────────────────────────────────────
        self.skip_btn = Gtk.Button(label=copy["skip"])
        self.skip_btn.add_css_class("flat")
        self.skip_btn.set_margin_top(8)
        self.skip_btn.set_margin_bottom(8)
        self.skip_btn.connect("clicked", lambda _: self._skip())
        self.append(self.skip_btn)

    # ── Registration flow ─────────────────────────────────────────────────────

    def _start_registration(self):
        """Kick off registration in a background thread — never blocks the UI."""
        self.register_btn.set_sensitive(False)
        self.skip_btn.set_sensitive(False)
        self._set_feedback("Registering…", style=None)

        thread = threading.Thread(target=self._registration_thread, daemon=True)
        thread.start()

    def _registration_thread(self):
        """Runs in background thread. Calls registration_client.register_device()."""
        success = register_device()
        GLib.idle_add(self._on_registration_result, success)

    def _on_registration_result(self, success):
        """Back on the GTK main thread — update UI based on result."""
        self.register_btn.set_sensitive(True)
        self.skip_btn.set_sensitive(True)

        if success:
            self._set_feedback("✓ Registered — thank you!", style="success")
            # Brief pause so user sees confirmation, then advance
            GLib.timeout_add(1200, self._advance)
        else:
            # Failed — not fatal, let user retry or skip
            self._set_feedback(
                "Couldn't register right now — no problem, you can skip.",
                style="warning",
            )

    def _skip(self):
        skip_registration()
        self._advance()

    def _advance(self):
        if self.on_next:
            self.on_next()
        return False  # Prevents GLib.timeout_add from repeating

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _set_feedback(self, text, style=None):
        self.feedback.set_text(text)
        self.feedback.set_visible(bool(text))
        for cls in ["success", "error", "warning", "dim-label"]:
            self.feedback.remove_css_class(cls)
        if style:
            self.feedback.add_css_class(style)
