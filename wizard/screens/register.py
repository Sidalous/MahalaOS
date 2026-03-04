"""
Screen 6b — Device Registration
Optional, anonymous registration. Fire-and-forget POST to registration endpoint.
Copy adapts based on install_type (home / franchise / oem).
"""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib

import uuid
import json
import threading
import urllib.request
import urllib.error
import os

from screens.base import BaseScreen
from install_config import read_install_config, save_device_id, load_device_id

REGISTRATION_ENDPOINT = "https://register.mahalaos.org/v1/device"
REGISTRATION_FLAG     = "/var/lib/mahalaos/registration-status"  # stores result

# Copy variants by install_type
COPY = {
    "home": {
        "heading":     "Help MahalaOS grow",
        "body":        "Register your device anonymously. We record only a random "
                       "device ID and your country — nothing personal, ever.",
        "register":    "Register my device",
        "skip":        "Skip",
    },
    "franchise": {
        "heading":     "Help MahalaOS grow",
        "body":        "Register your device anonymously. We record only a random "
                       "device ID and your country — nothing personal, ever.",
        "register":    "Register my device",
        "skip":        "Skip",
    },
    "oem": {
        "heading":     "Welcome to the MahalaOS community",
        "body":        "Join thousands of people using MahalaOS. We'll record only "
                       "a random device ID and your country — nothing personal, ever.",
        "register":    "Join the community",
        "skip":        "Skip for now",
    },
}


class RegisterScreen(BaseScreen):
    def __init__(self, on_next=None, on_back=None, **kwargs):
        super().__init__(on_next=on_next, on_back=on_back, **kwargs)

        self.config = read_install_config()
        install_type = self.config.get("install_type", "home")
        copy = COPY.get(install_type, COPY["home"])

        # Status page — icon + heading + body
        status_page = Adw.StatusPage()
        status_page.set_vexpand(True)
        status_page.set_icon_name("system-users-symbolic")
        status_page.set_title(copy["heading"])
        status_page.set_description(copy["body"])
        self.content_box.append(status_page)

        # Privacy reassurance row
        privacy_group = Adw.PreferencesGroup()
        for line in [
            ("No personal data",      "user-info-symbolic",         "No name, email, or account required."),
            ("No location tracking",  "find-location-symbolic",     "Country from your locale setting — not GPS."),
            ("One ping only",         "network-transmit-symbolic",  "Sent once on setup. Never again."),
        ]:
            row = Adw.ActionRow()
            row.set_title(line[0])
            row.set_subtitle(line[2])
            row.set_icon_name(line[1])
            privacy_group.add(row)
        self.content_box.append(privacy_group)

        # Feedback label (shown during/after registration attempt)
        self.feedback = Gtk.Label()
        self.feedback.set_wrap(True)
        self.feedback.set_halign(Gtk.Align.CENTER)
        self.feedback.set_visible(False)
        self.content_box.append(self.feedback)

        # Buttons — Register (primary) + Skip (flat)
        self.register_btn = Gtk.Button(label=copy["register"])
        self.register_btn.add_css_class("suggested-action")
        self.register_btn.add_css_class("pill")
        self.register_btn.connect("clicked", lambda _: self._register())
        self.append(self.register_btn)

        skip_btn = Gtk.Button(label=copy["skip"])
        skip_btn.add_css_class("flat")
        skip_btn.set_margin_top(8)
        skip_btn.set_margin_bottom(8)
        skip_btn.connect("clicked", lambda _: self._skip())
        self.append(skip_btn)

    def _register(self):
        self.register_btn.set_sensitive(False)
        self._set_feedback("Registering…", style=None)

        thread = threading.Thread(target=self._register_thread, daemon=True)
        thread.start()

    def _register_thread(self):
        config = self.config
        install_type = config.get("install_type", "home")
        partner_token = config.get("partner_token", None)

        # Reuse existing device_id if present (handles reflash case)
        device_id = load_device_id()
        if not device_id:
            device_id = str(uuid.uuid4())
            save_device_id(device_id)

        # Derive country from locale
        country = self._get_country()

        payload = {
            "device_id":     device_id,
            "install_type":  install_type,
            "partner_token": partner_token,
            "country":       country,
            "os_version":    config.get("os_version", "unknown"),
        }

        success = False
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                REGISTRATION_ENDPOINT,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                success = resp.status in (200, 201)
        except Exception:
            success = False

        # Write registration status flag for potential future retry
        self._write_flag("registered" if success else "failed")

        GLib.idle_add(self._on_register_result, success)

    def _on_register_result(self, success):
        self.register_btn.set_sensitive(True)
        if success:
            self._set_feedback("✓ Registered — thank you!", style="success")
            # Brief pause so user sees confirmation, then advance
            GLib.timeout_add(1200, self._advance)
        else:
            # Registration failed — not the end of the world, just move on
            self._set_feedback(
                "Couldn't register right now — no problem, you can skip.",
                style="warning"
            )

    def _skip(self):
        self._write_flag("skipped")
        if self.on_next:
            self.on_next()

    def _advance(self):
        if self.on_next:
            self.on_next()
        return False  # Don't repeat timeout

    def _get_country(self):
        """Derive ISO country code from system locale."""
        try:
            import locale as locale_mod
            loc = locale_mod.getdefaultlocale()[0] or ""
            # e.g. "en_GB" → "GB"
            if "_" in loc:
                return loc.split("_")[1][:2].upper()
        except Exception:
            pass
        return None

    def _write_flag(self, status):
        """
        Write registration status to flag file.
        Values: "registered", "skipped", "failed"
        "failed" can be checked later by a background service to retry.
        """
        try:
            os.makedirs(os.path.dirname(REGISTRATION_FLAG), exist_ok=True)
            with open(REGISTRATION_FLAG, "w") as f:
                f.write(status + "\n")
        except Exception:
            pass

    def _set_feedback(self, text, style=None):
        self.feedback.set_text(text)
        self.feedback.set_visible(bool(text))
        for cls in ["success", "error", "warning", "dim-label"]:
            self.feedback.remove_css_class(cls)
        if style:
            self.feedback.add_css_class(style)
