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


class KeyIdRow(Gtk.ListBoxRow):
    def __init__(self, key_id):
        super(Gtk.ListBoxRow, self).__init__()
        self.key_id = key_id
        label = Gtk.Label(label=key_id)
        label.props.halign = Gtk.Align.START
        self.add(label)
