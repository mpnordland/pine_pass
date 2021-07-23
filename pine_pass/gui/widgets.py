import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk


class PasswordRow(Gtk.ListBoxRow):
    def __init__(self, password_entry):
        super(Gtk.ListBoxRow, self).__init__()
        self.entry = password_entry
        self.layout = Gtk.Box(spacing=4)
        label = Gtk.Label(label=password_entry)
        label.props.halign = Gtk.Align.START
        self.layout.add(label)

        self.button = Gtk.Button.new_with_label("Edit")
        self.layout.add(self.button)
        self.layout.show_all()

        self.add(self.layout)


    def set_button_callback(self, callback):
        self.button.connect('clicked', callback)


class KeyIdRow(Gtk.ListBoxRow):
    def __init__(self, key_id):
        super(Gtk.ListBoxRow, self).__init__()
        self.key_id = key_id
        label = Gtk.Label(label=key_id)
        label.props.halign = Gtk.Align.START
        self.add(label)


class PasswordEditDialog(Gtk.Dialog):
    def __init__(self, password_path, password_entry, parent):
        super().__init__(title="Editing " + password_path, transient_for=parent, flags=0)
        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_APPLY, Gtk.ResponseType.APPLY
        )

        self.text_view = Gtk.TextView()

        self.text_view.get_buffer().set_text(password_entry)

        box = self.get_content_area()
        box.add(self.text_view)
        self.show_all()

    def get_password_contents(self):
        return self.text_view.get_buffer().get_text()
