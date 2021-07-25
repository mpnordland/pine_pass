import os


import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, Gio

Gio.Resource._register(Gio.Resource.load(os.path.join(os.path.dirname(__file__), "ui_definitions/ui.gresource")))

from .main_window import MainWindow

class PinePassApp:
    def __init__(self, config):

        self._config = config

        self._window = MainWindow()
        self._window.setup(self._config)

    def run(self):

        style_provider = Gtk.CssProvider()
        style_provider.load_from_resource("/me/rehack/pinepass/ui.css")

        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        self._window.show_all()
        Gtk.main()
