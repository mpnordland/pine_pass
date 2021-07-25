import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class PasswordRow(Gtk.ListBoxRow):
    def __init__(self, password_entry):
        super().__init__()
        self.entry = password_entry
        self.layout = Gtk.Box(spacing=4)
        label = Gtk.Label(label=password_entry)
        label.props.halign = Gtk.Align.START
        label.set_hexpand(True)
        self.layout.add(label)

        self.button = Gtk.Button.new_with_label("Edit")
        self.button.props.halign = Gtk.Align.END
        self.layout.add(self.button)
        self.layout.show_all()

        self.add(self.layout)

    def set_button_callback(self, callback):
        self.button.connect('clicked', callback)


class KeyIdRow(Gtk.ListBoxRow):
    def __init__(self, key_id):
        super().__init__()
        self.key_id = key_id
        label = Gtk.Label(label=key_id)
        label.props.halign = Gtk.Align.START
        self.add(label)

