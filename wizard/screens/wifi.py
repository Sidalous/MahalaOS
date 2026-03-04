"""
Screen 3 — WiFi
Scans for networks via nmcli, connects, verifies before allowing Next.
Handles already-connected state gracefully.
"""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib

import subprocess
import threading

from screens.base import BaseScreen


def run_nmcli(*args):
    cmd = ["nmcli", "--terse", "--colors", "no"] + list(args)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return 1, "", "Timeout"
    except FileNotFoundError:
        return 1, "", "nmcli not found"


def get_active_connection():
    """Return the SSID of the currently active WiFi connection, or None."""
    rc, stdout, _ = run_nmcli(
        "-f", "ACTIVE,SSID", "device", "wifi", "list"
    )
    if rc != 0:
        return None
    for line in stdout.splitlines():
        parts = line.split(":", 1)
        if len(parts) == 2 and parts[0].strip() == "yes":
            return parts[1].strip()
    return None


class WifiNetworkRow(Adw.ActionRow):
    def __init__(self, ssid, signal, secured, active, on_select):
        super().__init__()
        self.ssid = ssid
        self.secured = secured

        self.set_title(ssid)
        self.set_activatable(True)

        if signal >= 75:
            icon_name = "network-wireless-signal-excellent-symbolic"
        elif signal >= 50:
            icon_name = "network-wireless-signal-good-symbolic"
        elif signal >= 25:
            icon_name = "network-wireless-signal-ok-symbolic"
        else:
            icon_name = "network-wireless-signal-weak-symbolic"

        signal_icon = Gtk.Image.new_from_icon_name(icon_name)
        self.add_prefix(signal_icon)

        if active:
            self.set_subtitle("Connected")
            tick = Gtk.Image.new_from_icon_name("emblem-ok-symbolic")
            self.add_suffix(tick)
        elif secured:
            lock_icon = Gtk.Image.new_from_icon_name("channel-secure-symbolic")
            self.add_suffix(lock_icon)

        self.connect("activated", lambda _: on_select(self))


class WifiScreen(BaseScreen):
    def __init__(self, on_next=None, on_back=None, **kwargs):
        super().__init__(on_next=on_next, on_back=on_back, **kwargs)

        self.selected_ssid = None
        self.selected_secured = False
        self.connected = False
        self._scanning = False
        self._network_rows = []

        # Header
        title = Gtk.Label(label="Connect to WiFi")
        title.add_css_class("title-1")
        title.set_halign(Gtk.Align.START)
        self.content_box.append(title)

        self.subtitle = Gtk.Label(label="Choose your WiFi network to get started.")
        self.subtitle.add_css_class("body")
        self.subtitle.set_halign(Gtk.Align.START)
        self.subtitle.set_wrap(True)
        self.subtitle.set_xalign(0)
        self.content_box.append(self.subtitle)

        # Network list
        self.network_group = Adw.PreferencesGroup()
        self.network_group.set_title("Available networks")

        self.scan_btn = Gtk.Button()
        self.scan_btn.set_icon_name("view-refresh-symbolic")
        self.scan_btn.add_css_class("flat")
        self.scan_btn.set_tooltip_text("Scan for networks")
        self.scan_btn.connect("clicked", lambda _: self._start_scan())
        self.network_group.set_header_suffix(self.scan_btn)

        self.content_box.append(self.network_group)

        # Spinner row — added/removed from group dynamically
        self.spinner = Gtk.Spinner()
        self.spinner_row = Adw.ActionRow()
        self.spinner_row.set_title("Scanning…")
        self.spinner_row.add_prefix(self.spinner)

        # Password entry
        self.password_group = Adw.PreferencesGroup()
        self.password_group.set_title("Password")
        self.password_group.set_visible(False)
        self.password_row = Adw.PasswordEntryRow()
        self.password_row.set_title("WiFi Password")
        self.password_group.add(self.password_row)
        self.content_box.append(self.password_group)

        # Connect button
        self.connect_btn = Gtk.Button(label="Connect")
        self.connect_btn.add_css_class("suggested-action")
        self.connect_btn.set_visible(False)
        self.connect_btn.connect("clicked", lambda _: self._connect())
        self.content_box.append(self.connect_btn)

        # Status label
        self.status_label = Gtk.Label()
        self.status_label.set_halign(Gtk.Align.CENTER)
        self.status_label.set_wrap(True)
        self.status_label.set_visible(False)
        self.content_box.append(self.status_label)

        # Nav buttons
        self.build_nav_buttons(next_label="Continue", show_back=True)
        self.set_next_sensitive(False)

        skip_btn = Gtk.Button(label="Skip for now")
        skip_btn.add_css_class("flat")
        skip_btn.connect("clicked", lambda _: on_next())
        self.nav_box.prepend(skip_btn)

    def on_enter(self):
        self._start_scan()

    def _clear_network_rows(self):
        """Remove only network rows, not the spinner row."""
        for row in self._network_rows:
            self.network_group.remove(row)
        self._network_rows.clear()

    def _start_scan(self):
        if self._scanning:
            return
        self._scanning = True

        self._clear_network_rows()
        self.network_group.add(self.spinner_row)
        self.spinner.start()
        self.scan_btn.set_sensitive(False)
        self.connect_btn.set_visible(False)
        self.password_group.set_visible(False)
        self._set_status("", visible=False)

        thread = threading.Thread(target=self._scan_thread, daemon=True)
        thread.start()

    def _scan_thread(self):
        # Trigger a hardware rescan
        run_nmcli("device", "wifi", "rescan")

        # Get active connection first
        active_ssid = get_active_connection()

        # List all networks: SSID, SIGNAL, SECURITY, IN-USE
        rc, stdout, _ = run_nmcli(
            "-f", "IN-USE,SSID,SIGNAL,SECURITY",
            "device", "wifi", "list"
        )

        networks = []
        if rc == 0 and stdout:
            seen = set()
            for line in stdout.splitlines():
                parts = line.split(":", 3)
                if len(parts) < 4:
                    continue
                in_use = parts[0].strip() == "*"
                ssid = parts[1].strip()
                if not ssid or ssid == "--" or ssid in seen:
                    continue
                seen.add(ssid)
                try:
                    signal = int(parts[2].strip())
                except ValueError:
                    signal = 0
                security = parts[3].strip()
                secured = bool(security and security != "--")
                networks.append((ssid, signal, secured, in_use))

            # Active connection first, then sort by signal
            networks.sort(key=lambda x: (not x[3], -x[1]))

        GLib.idle_add(self._populate_networks, networks, active_ssid)

    def _populate_networks(self, networks, active_ssid):
        # Remove spinner
        try:
            self.network_group.remove(self.spinner_row)
        except Exception:
            pass
        self.spinner.stop()
        self.scan_btn.set_sensitive(True)
        self._scanning = False

        if not networks:
            row = Adw.ActionRow()
            row.set_title("No networks found")
            row.set_subtitle("Make sure WiFi is enabled, then tap refresh")
            self.network_group.add(row)
            self._network_rows.append(row)
            return

        for ssid, signal, secured, active in networks:
            row = WifiNetworkRow(
                ssid=ssid,
                signal=signal,
                secured=secured,
                active=active,
                on_select=self._on_network_selected,
            )
            self.network_group.add(row)
            self._network_rows.append(row)

        # If already connected, reflect that immediately
        if active_ssid:
            self.connected = True
            self.set_next_sensitive(True)
            self.subtitle.set_text(f"You're connected to {active_ssid}. You can continue or switch networks.")
            self._set_status(f"✓ Connected to {active_ssid}", style="success")

    def _on_network_selected(self, row):
        self.selected_ssid = row.ssid
        self.selected_secured = row.secured

        # Don't reset connected state if they're just tapping the active network
        active = get_active_connection()
        if active == row.ssid:
            self._set_status(f"✓ Already connected to {row.ssid}", style="success")
            self.set_next_sensitive(True)
            self.connect_btn.set_visible(False)
            self.password_group.set_visible(False)
            return

        self.connected = False
        self.set_next_sensitive(False)
        self.password_group.set_visible(row.secured)
        self.connect_btn.set_visible(True)
        self._set_status("", visible=False)

    def _connect(self):
        if not self.selected_ssid:
            return
        password = self.password_row.get_text() if self.selected_secured else None
        self.connect_btn.set_sensitive(False)
        self._set_status("Connecting…", style=None)

        thread = threading.Thread(
            target=self._connect_thread,
            args=(self.selected_ssid, password),
            daemon=True,
        )
        thread.start()

    def _connect_thread(self, ssid, password):
        if password:
            cmd = ["device", "wifi", "connect", ssid, "password", password]
        else:
            cmd = ["device", "wifi", "connect", ssid]
        rc, stdout, stderr = run_nmcli(*cmd)
        success = rc == 0 and "successfully activated" in stdout.lower()
        GLib.idle_add(self._on_connect_result, success, stderr)

    def _on_connect_result(self, success, error_msg):
        self.connect_btn.set_sensitive(True)
        if success:
            self.connected = True
            self._set_status(f"✓ Connected to {self.selected_ssid}!", style="success")
            self.set_next_sensitive(True)
            self.connect_btn.set_visible(False)
            self.password_group.set_visible(False)
        else:
            self.connected = False
            self.set_next_sensitive(False)
            msg = "Couldn't connect. Check your password and try again."
            if "secrets" in error_msg.lower() or "wrong" in error_msg.lower():
                msg = "Wrong password. Please try again."
            self._set_status(f"✗ {msg}", style="error")

    def _set_status(self, text, style=None, visible=True):
        self.status_label.set_text(text)
        self.status_label.set_visible(visible and bool(text))
        for cls in ["success", "error", "warning", "dim-label"]:
            self.status_label.remove_css_class(cls)
        if style:
            self.status_label.add_css_class(style)
