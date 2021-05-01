import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class PasswordRow(Gtk.ListBoxRow):
    def __init__(self, password_entry):
        super(Gtk.ListBoxRow, self).__init__()
        self.entry = password_entry
        label = Gtk.Label(label=password_entry)
        label.props.halign = Gtk.Align.START
        self.add(label)


class PreferencesDialog(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, title="Preferences", transient_for=parent, flags=0)
        self.add_buttons(
            Gtk.STOCK_OK, Gtk.ResponseType.OK
        )

        self.set_default_size(150, 100)

        label = Gtk.Label(label="Preferences are still WIP")

        box = self.get_content_area()
        box.add(label)
        self.show_all()