"""
Screen 5 — What Works / What Doesn't
The most important trust-building screen. Honest, warm, no spin.
"""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

from screens.base import BaseScreen


FEATURE_STATUS = [
    ("Calls and texts",         "works",    "Works great on supported networks."),
    ("WhatsApp",                "works",    "Runs via our Android compatibility layer."),
    ("Firefox browser",         "works",    "Full desktop-class browser, no compromises."),
    ("Email",                   "works",    "GNOME Mail and others available."),
    ("Signal, Telegram",        "works",    "Native Linux apps, no Android layer needed."),
    ("Camera",                  "partial",  "Photos work. Video and quality are a work in progress."),
    ("Some Android apps",       "partial",  "Most install fine via Waydroid. A few don't run yet."),
    ("Mobile payments",         "partial",  "Google Pay and Apple Pay won't work. Bank apps vary."),
    ("iMessage / FaceTime",     "not_yet",  "Apple services require an Apple device."),
    ("Netflix / Disney+ (DRM)", "not_yet",  "Streaming apps with DRM protection won't work yet."),
]

STATUS_CONFIG = {
    "works":    ("✅", "Works great"),
    "partial":  ("⚠️",  "Partially works"),
    "not_yet":  ("❌", "Doesn't work yet"),
}


class HonestScreen(BaseScreen):
    def __init__(self, on_next=None, on_back=None, **kwargs):
        super().__init__(on_next=on_next, on_back=on_back, **kwargs)

        title = Gtk.Label(label="What to expect")
        title.add_css_class("title-1")
        title.set_halign(Gtk.Align.START)
        self.content_box.append(title)

        intro = Gtk.Label(
            label="We believe in being straight with you. "
                  "MahalaOS is great for most things — here's an honest picture."
        )
        intro.add_css_class("body")
        intro.set_halign(Gtk.Align.START)
        intro.set_wrap(True)
        intro.set_xalign(0)
        self.content_box.append(intro)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)
        scroll.set_min_content_height(200)

        group = Adw.PreferencesGroup()
        for feature, status, note in FEATURE_STATUS:
            group.add(self._make_row(feature, status, note))

        scroll.set_child(group)
        self.content_box.append(scroll)

        footer = Gtk.Label(
            label="Things improve with every update. You're joining early — thank you."
        )
        footer.add_css_class("caption")
        footer.add_css_class("dim-label")
        footer.set_wrap(True)
        footer.set_xalign(0)
        footer.set_halign(Gtk.Align.START)
        self.content_box.append(footer)

        self.build_nav_buttons(next_label="Got it — let's continue", show_back=True)

    def _make_row(self, feature, status, note):
        emoji, label = STATUS_CONFIG[status]
        row = Adw.ActionRow()
        row.set_title(feature)

        # subtitle wraps automatically in Adw.ActionRow
        row.set_subtitle(note)
        row.set_subtitle_lines(3)  # allow up to 3 lines before truncating

        status_label = Gtk.Label(label=emoji)
        status_label.set_tooltip_text(label)
        status_label.set_valign(Gtk.Align.CENTER)
        row.add_prefix(status_label)

        return row
