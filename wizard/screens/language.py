"""
Screen 2 — Language & Region
Reads system locale/timezone as defaults, lets user change them.
Changes are saved and applied on wizard completion, not mid-wizard.
"""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

import subprocess
import locale
from screens.base import BaseScreen

LANGUAGES = [
    ("en_GB", "English (United Kingdom)"),
    ("en_US", "English (United States)"),
    ("fr_FR", "Français (France)"),
    ("de_DE", "Deutsch (Deutschland)"),
    ("es_ES", "Español (España)"),
    ("it_IT", "Italiano (Italia)"),
    ("pt_PT", "Português (Portugal)"),
    ("nl_NL", "Nederlands (Nederland)"),
    ("pl_PL", "Polski (Polska)"),
    ("ar_SA", "العربية"),
    ("zh_CN", "中文 (简体)"),
    ("ja_JP", "日本語"),
]

TIMEZONES = [
    "Europe/London",
    "Europe/Paris",
    "Europe/Berlin",
    "Europe/Madrid",
    "Europe/Rome",
    "Europe/Amsterdam",
    "Europe/Warsaw",
    "America/New_York",
    "America/Chicago",
    "America/Denver",
    "America/Los_Angeles",
    "Asia/Dubai",
    "Asia/Karachi",
    "Asia/Kolkata",
    "Asia/Shanghai",
    "Asia/Tokyo",
    "Australia/Sydney",
    "Africa/Johannesburg",
]


def get_system_timezone():
    try:
        result = subprocess.run(
            ["timedatectl", "show", "--property=Timezone", "--value"],
            capture_output=True, text=True, timeout=5
        )
        tz = result.stdout.strip()
        if tz and tz in TIMEZONES:
            return tz
    except Exception:
        pass
    return "Europe/London"


def get_system_locale():
    try:
        loc = locale.getdefaultlocale()[0]
        if loc:
            return loc
    except Exception:
        pass
    return "en_GB"


class LanguageScreen(BaseScreen):
    def __init__(self, on_next=None, on_back=None, **kwargs):
        super().__init__(on_next=on_next, on_back=on_back, **kwargs)

        title = Gtk.Label(label="Language & Region")
        title.add_css_class("title-1")
        title.set_halign(Gtk.Align.START)
        self.content_box.append(title)

        subtitle = Gtk.Label(
            label="We've detected your current settings. Change them here if needed."
        )
        subtitle.add_css_class("body")
        subtitle.set_halign(Gtk.Align.START)
        subtitle.set_wrap(True)
        subtitle.set_xalign(0)
        self.content_box.append(subtitle)

        current_locale = get_system_locale()
        current_tz = get_system_timezone()

        lang_index = next(
            (i for i, (code, _) in enumerate(LANGUAGES)
             if current_locale.startswith(code[:2])),
            0
        )
        tz_index = next(
            (i for i, tz in enumerate(TIMEZONES) if tz == current_tz),
            0
        )

        group = Adw.PreferencesGroup()

        self.lang_row = Adw.ComboRow()
        self.lang_row.set_title("Language")
        lang_model = Gtk.StringList()
        for _, name in LANGUAGES:
            lang_model.append(name)
        self.lang_row.set_model(lang_model)
        self.lang_row.set_selected(lang_index)
        group.add(self.lang_row)

        self.tz_row = Adw.ComboRow()
        self.tz_row.set_title("Timezone")
        tz_model = Gtk.StringList()
        for tz in TIMEZONES:
            tz_model.append(tz)
        self.tz_row.set_model(tz_model)
        self.tz_row.set_selected(tz_index)
        group.add(self.tz_row)

        self.content_box.append(group)

        note = Gtk.Label(
            label="Language changes take effect after restart. "
                  "More options available in Settings."
        )
        note.add_css_class("caption")
        note.add_css_class("dim-label")
        note.set_halign(Gtk.Align.START)
        note.set_wrap(True)
        note.set_xalign(0)
        self.content_box.append(note)

        self.build_nav_buttons(next_label="Continue", show_back=True)

    def _on_next_clicked(self):
        """Save selections — apply timezone only, defer locale to completion."""
        try:
            tz_index = self.tz_row.get_selected()
            selected_tz = TIMEZONES[tz_index]
            subprocess.run(
                ["sudo", "timedatectl", "set-timezone", selected_tz],
                timeout=5,
                capture_output=True,
            )
        except Exception:
            pass  # Non-fatal, user can fix in Settings

        # Always proceed — never block on this
        if self.on_next:
            self.on_next()
