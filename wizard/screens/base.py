"""
Base screen class for MahalaOS Setup Wizard screens.
Provides shared layout helpers and navigation button builders.
"""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw


class BaseScreen(Gtk.Box):
    """
    Base class for all wizard screens.
    Provides a consistent vertical layout:
      [top padding]
      [content area — filled by subclass]
      [spacer]
      [navigation buttons]
      [bottom padding]
    """

    def __init__(self, on_next=None, on_back=None, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, **kwargs)
        self.on_next = on_next
        self.on_back = on_back

        self.set_margin_start(24)
        self.set_margin_end(24)
        self.set_margin_top(24)
        self.set_margin_bottom(24)
        self.set_spacing(0)

        # Content area — subclasses append their widgets here
        self.content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.content_box.set_spacing(16)
        self.append(self.content_box)

        # Push nav buttons to the bottom
        spacer = Gtk.Box()
        spacer.set_vexpand(True)
        self.append(spacer)

        # Navigation button row
        self.nav_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.nav_box.set_spacing(12)
        self.append(self.nav_box)

    def build_nav_buttons(
        self,
        next_label="Continue",
        back_label="Back",
        show_back=True,
        show_next=True,
        next_style="suggested-action",  # or "destructive-action" or ""
    ):
        """
        Build and add navigation buttons to the nav_box.
        Call this at the end of subclass __init__.
        """
        # Clear existing buttons
        child = self.nav_box.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.nav_box.remove(child)
            child = next_child

        if show_back and self.on_back:
            back_btn = Gtk.Button(label=back_label)
            back_btn.connect("clicked", lambda _: self.on_back())
            self.nav_box.append(back_btn)

        if show_next and self.on_next:
            next_btn = Gtk.Button(label=next_label)
            next_btn.add_css_class(next_style)
            next_btn.set_hexpand(True)
            next_btn.connect("clicked", lambda _: self._on_next_clicked())
            self.nav_box.append(next_btn)
            self.next_btn = next_btn

    def _on_next_clicked(self):
        """Override in subclass to add validation before proceeding."""
        if self.on_next:
            self.on_next()

    def set_next_sensitive(self, sensitive: bool):
        """Enable or disable the Next button (e.g. wait for WiFi connection)."""
        if hasattr(self, "next_btn"):
            self.next_btn.set_sensitive(sensitive)

    def on_enter(self):
        """
        Called when this screen becomes active.
        Override in subclasses that need to refresh state on entry.
        """
        pass
