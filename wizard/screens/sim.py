"""
Screen 4 — SIM Detection
Queries ModemManager via mmcli. Hard timeout so it never hangs.
"""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib

import subprocess
import threading
import json

from screens.base import BaseScreen


def get_modem_info():
    result = {"found": False, "carrier": None, "volte": None}
    try:
        r = subprocess.run(
            ["mmcli", "-L", "--output-json"],
            capture_output=True, text=True, timeout=6
        )
        if r.returncode != 0 or not r.stdout.strip():
            return result

        data = json.loads(r.stdout)
        modems = data.get("modem-list", [])
        if not modems:
            return result

        r2 = subprocess.run(
            ["mmcli", "-m", modems[0], "--output-json"],
            capture_output=True, text=True, timeout=6
        )
        if r2.returncode != 0 or not r2.stdout.strip():
            return result

        modem = json.loads(r2.stdout).get("modem", {})
        carrier = modem.get("3gpp", {}).get("operator-name", "").strip()
        if not carrier or carrier == "--":
            carrier = "Unknown carrier"

        caps = modem.get("generic", {}).get("current-capabilities", "")
        result.update({
            "found": True,
            "carrier": carrier,
            "volte": "lte" in (caps if isinstance(caps, str) else " ".join(caps)).lower(),
        })
    except Exception:
        pass
    return result


class SimScreen(BaseScreen):
    def __init__(self, on_next=None, on_back=None, **kwargs):
        super().__init__(on_next=on_next, on_back=on_back, **kwargs)

        title = Gtk.Label(label="SIM Card")
        title.add_css_class("title-1")
        title.set_halign(Gtk.Align.START)
        self.content_box.append(title)

        self.status_page = Adw.StatusPage()
        self.status_page.set_vexpand(True)
        self.status_page.set_icon_name("network-cellular-symbolic")
        self.status_page.set_title("Checking SIM…")
        self.status_page.set_description("Just a moment.")
        self.content_box.append(self.status_page)

        self.build_nav_buttons(next_label="Continue", show_back=True)

        # Fallback: if detection takes too long, show skip option
        self._timeout_id = None

    def on_enter(self):
        # Hard 8-second timeout — if mmcli doesn't respond, give up gracefully
        self._timeout_id = GLib.timeout_add(8000, self._on_timeout)
        thread = threading.Thread(target=self._detect_thread, daemon=True)
        thread.start()

    def _detect_thread(self):
        info = get_modem_info()
        GLib.idle_add(self._show_result, info)

    def _show_result(self, info):
        # Cancel timeout if we got a result in time
        if self._timeout_id:
            GLib.source_remove(self._timeout_id)
            self._timeout_id = None

        if not info["found"]:
            self.status_page.set_icon_name("network-cellular-offline-symbolic")
            self.status_page.set_title("No SIM detected")
            self.status_page.set_description(
                "You can insert a SIM and configure it later in Settings.\n"
                "WiFi calling and messaging apps will still work."
            )
            return

        self.status_page.set_icon_name("network-cellular-symbolic")
        self.status_page.set_title(f"SIM detected: {info['carrier']}")
        if info["volte"]:
            desc = "Your SIM is ready. Calls, texts, and mobile data should work."
        else:
            desc = "Your SIM is ready. Calls and texts should work.\nVoLTE depends on your carrier."
        self.status_page.set_description(desc)

    def _on_timeout(self):
        self._timeout_id = None
        self.status_page.set_icon_name("network-cellular-offline-symbolic")
        self.status_page.set_title("Couldn't detect SIM")
        self.status_page.set_description(
            "This sometimes takes a moment on first boot.\n"
            "You can check your SIM status in Settings after setup."
        )
        return False  # Don't repeat
