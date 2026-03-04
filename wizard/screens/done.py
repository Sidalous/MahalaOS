"""
Screen 7 — You're Ready
Satisfying completion screen. Quick links, website link, warm send-off.
"""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio

import subprocess
from screens.base import BaseScreen

# (label, icon, list of desktop IDs to try in order, fallback binary)
QUICK_APPS = [
    ("Phone",
     "call-start-symbolic",
     ["org.gnome.Calls.desktop", "calls.desktop"],
     "calls"),
    ("Messages",
     "message-new-symbolic",
     ["sm.puri.Chatty.desktop"],
     "chatty"),
    ("Browser",
     "web-browser-symbolic",
     ["firefox-esr.desktop", "firefox.desktop"],
     "firefox"),
    ("Settings",
     "preferences-system-symbolic",
     ["org.gnome.Settings.desktop", "gnome-control-center.desktop"],
     "gnome-control-center"),
]


class DoneScreen(BaseScreen):
    def __init__(self, on_finish=None, **kwargs):
        super().__init__(on_next=None, on_back=None, **kwargs)
        self.on_finish = on_finish

        status_page = Adw.StatusPage()
        status_page.set_vexpand(True)
        status_page.set_icon_name("emblem-ok-symbolic")
        status_page.set_title("You're all set!")
        status_page.set_description(
            "MahalaOS is ready to go.\nWelcome to a phone that respects you."
        )
        self.content_box.append(status_page)

        apps_group = Adw.PreferencesGroup()
        apps_group.set_title("Jump straight in")

        for label, icon, desktop_ids, fallback in QUICK_APPS:
            row = Adw.ActionRow()
            row.set_title(label)
            row.set_activatable(True)
            row.set_icon_name(icon)
            row.connect(
                "activated",
                lambda _, ids=desktop_ids, fb=fallback: self._launch_app(ids, fb)
            )
            row.add_suffix(Gtk.Image.new_from_icon_name("go-next-symbolic"))
            apps_group.add(row)

        # Website row
        website_row = Adw.ActionRow()
        website_row.set_title("Learn more about MahalaOS")
        website_row.set_subtitle("mahalaos.org")
        website_row.set_activatable(True)
        website_row.set_icon_name("globe-symbolic")
        website_row.connect(
            "activated",
            lambda _: self._open_url("https://mahalaos.org")
        )
        website_row.add_suffix(Gtk.Image.new_from_icon_name("go-next-symbolic"))
        apps_group.add(website_row)

        self.content_box.append(apps_group)

        finish_btn = Gtk.Button(label="Explore MahalaOS →")
        finish_btn.add_css_class("suggested-action")
        finish_btn.add_css_class("pill")
        finish_btn.set_margin_top(16)
        finish_btn.connect("clicked", lambda _: self._finish())
        self.append(finish_btn)

        bottom_pad = Gtk.Box()
        bottom_pad.set_margin_bottom(8)
        self.append(bottom_pad)

    def _launch_app(self, desktop_ids, fallback):
        """Try each desktop ID in order, then fall back to binary."""
        for desktop_id in desktop_ids:
            try:
                app_info = Gio.DesktopAppInfo.new(desktop_id)
                if app_info is not None:
                    app_info.launch([], None)
                    return
            except Exception:
                continue

        # Try gtk-launch with each ID
        for desktop_id in desktop_ids:
            try:
                result = subprocess.run(
                    ["gtk-launch", desktop_id],
                    capture_output=True, timeout=3
                )
                if result.returncode == 0:
                    return
            except Exception:
                continue

        # Last resort: binary
        try:
            subprocess.Popen([fallback])
        except Exception:
            pass

    def _open_url(self, url):
        try:
            Gio.AppInfo.launch_default_for_uri(url, None)
        except Exception:
            try:
                subprocess.Popen(["xdg-open", url])
            except Exception:
                pass

    def _finish(self):
        if self.on_finish:
            self.on_finish()
