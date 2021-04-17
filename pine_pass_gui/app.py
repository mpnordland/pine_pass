from pine_pass.indexer import index_passwords
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk



class PinePassApp:

    def __init__(self, config):

        self._index = index_passwords(config['password-store-pass'])
        self._builder = Gtk.Builder()
        self._builder.add_from_file("./ui.glade")

    def run(self):
        handlers = {
            "gtk_main_quit": Gtk.main_quit,
            "on_password_search_changed": self.update_search_results,
        }
        self._builder.connect_signals(handlers)
        win = self._builder.get_object('main_window')
        win.show_all()
        Gtk.main()

    def update_search_results(self, entry):
        results = self._index.lookup(entry.get_text())
        if results:
            list_box = self._builder.get_object('results_list')
            list_box.foreach(lambda child: list_box.remove(child))

            for result in results:
                row = Gtk.ListBoxRow()
                row.add(Gtk.Label(label=result))
                list_box.add(row)
            
            list_box.show_all()
