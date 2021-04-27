import os
from pine_pass import password_to_clipboard, sync_passwords
from .widgets import PasswordRow
from pine_pass.indexer import index_passwords
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib


class PinePassApp:

    def __init__(self, config):

        self._config = config
        self.reindex_passwords()
        self._builder = Gtk.Builder()
        self._assets_path = os.path.dirname(__file__)
        glade_file = os.path.join(self._assets_path, 'ui.glade')
        self._builder.add_from_file(glade_file)

    def run(self):
        handlers = {
            "gtk_main_quit": Gtk.main_quit,
            "on_password_search_changed": self.update_search_results,
            "password_row_activated": self.copy_password,
            "on_refresh_button_clicked": self.refresh_passwords,
        }
        self._builder.connect_signals(handlers)
        win = self._builder.get_object('main_window')

        style_provider = Gtk.CssProvider()
        style_provider.load_from_path(os.path.join(self._assets_path, "ui.css"))

        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        win.show_all()
        Gtk.main()

    def update_search_results(self, entry):
        results = self._index.lookup(entry.get_text())
        if results:
            list_box = self._builder.get_object('results_list')
            list_box.foreach(lambda child: list_box.remove(child))

            for result in results:
                list_box.add(PasswordRow(result))

            list_box.show_all()

    def copy_password(self, list_box, row):
        revealer = self._builder.get_object("revealer")
        password_label = self._builder.get_object("notification_password_name")

        password_label.set_text(row.entry)
        revealer.set_reveal_child(True)
        password_to_clipboard(row.entry)

        GLib.timeout_add(2000, self.hide_notification, None)

    def hide_notification(self, what):
        revealer = self._builder.get_object("revealer")
        revealer.set_reveal_child(False)
        return False

    def refresh_passwords(self, button):
        # TODO: make search and results inactive while refresh is happening
        sync_passwords()
        self.reindex_passwords()

    def reindex_passwords(self):
        self._index = index_passwords(self._config['password-store-pass'])

