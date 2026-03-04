"""
Screen 1 — Welcome
First thing the user sees. Sets the tone: warm, honest, not scary.
"""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

from screens.base import BaseScreen


class WelcomeScreen(BaseScreen):
    def __init__(self, on_next=None, **kwargs):
        super().__init__(on_next=on_next, on_back=None, **kwargs)

        status_page = Adw.StatusPage()
        status_page.set_vexpand(True)

        # Use the mahalaos icon once installed; GTK shows a fallback until then.
        # To add the real icon, install a 128x128 SVG to:
        #   /usr/share/icons/hicolor/scalable/apps/mahalaos.svg
        # and run: gtk-update-icon-cache /usr/share/icons/hicolor/
        status_page.set_icon_name("mahalaos")

        status_page.set_title("Welcome to MahalaOS")
        status_page.set_description(
            "A private, open phone OS built for real people.\n\n"
            "This is a little different to Android or iPhone. "
            "Let's take a couple of minutes to get you set up."
        )

        self.content_box.append(status_page)

        # Single large CTA — no Back on the first screen
        lets_go_btn = Gtk.Button(label="Let's go →")
        lets_go_btn.add_css_class("suggested-action")
        lets_go_btn.add_css_class("pill")
        lets_go_btn.set_margin_top(8)
        lets_go_btn.connect("clicked", lambda _: on_next())
        self.append(lets_go_btn)

        # Subtle website link — dim, doesn't compete with the CTA
        website_btn = Gtk.LinkButton.new_with_label(
            "https://mahalaos.org", "mahalaos.org"
        )
        website_btn.add_css_class("dim-label")
        website_btn.set_margin_top(12)
        website_btn.set_margin_bottom(8)
        self.append(website_btn)
