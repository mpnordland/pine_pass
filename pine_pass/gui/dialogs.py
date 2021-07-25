from pine_pass import (
    get_respository_remote,
    get_key_ids,
    generate_ssh_keypair,
    get_ssh_pub_keys,
    get_unused_available_gpg_keys,
    generate_password,
)

from .background import run_background_task
from .widgets import KeyIdRow

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


@Gtk.Template(resource_path="/me/rehack/pinepass/password_edit_dialog.ui")
class PasswordEditDialog(Gtk.Dialog):

    __gtype_name__ = 'PasswordEditDialog'

    entry = Gtk.Template.Child('password_path')
    text_view = Gtk.Template.Child('password_entry')
    editor = Gtk.Template.Child('password_editor')

    password_length = Gtk.Template.Child('password_length')
    use_upper_alpha = Gtk.Template.Child('use_upper_alpha')
    use_lower_alpha = Gtk.Template.Child('use_lower_alpha')
    use_numerals = Gtk.Template.Child('use_numerals')
    use_symbols = Gtk.Template.Child('use_symbols')
    use_custom_symbols = Gtk.Template.Child('use_custom_symbols')
    custom_symbol_set = Gtk.Template.Child('custom_symbol_set')
    generated_password_display = Gtk.Template.Child(
        'generated_password_display')

    def setup(self, password_path, password_entry):
        self.entry.set_text(password_path)
        self.text_view.get_buffer().set_text(password_entry)

        if password_path.strip() == '':
            self.set_title("New Password")
        else:
            self.set_title(f"Editing {password_path}")
            self.entry.hide()

    def get_password_path(self):
        return self.entry.get_text()

    def get_password_contents(self):
        buffer = self.text_view.get_buffer()
        start = buffer.get_start_iter()
        end = buffer.get_end_iter()
        return buffer.get_text(start, end, False)

    @Gtk.Template.Callback()
    def generate_new_password(self, button):
        length = int(self.password_length.get_text())
        new_password = generate_password(length,
                                         self.use_lower_alpha.get_active(),
                                         self.use_upper_alpha.get_active(),
                                         self.use_numerals.get_active(),
                                         self.use_symbols.get_active(),
                                         self.custom_symbol_set.get_text() if self.use_custom_symbols.get_active() else None)

        self.generated_password_display.get_buffer().set_text(new_password)
        self.generated_password_display.show()

    @Gtk.Template.Callback()
    def insert_generated_password(self, button):
        generated_buffer = self.generated_password_display.get_buffer()
        start = generated_buffer.get_start_iter()
        end = generated_buffer.get_end_iter()
        generated_password = generated_buffer.get_text(start, end, False)

        self.text_view.get_buffer().set_text(
            "\n".join([generated_password, self.get_password_contents()]))


@Gtk.Template(resource_path="/me/rehack/pinepass/prefs_dialog.ui")
class PreferencesDialog(Gtk.Dialog):
    __gtype_name__ = "PreferencesDialog"

    repo_url_entry = Gtk.Template.Child("repo_url")
    gpg_key_box = Gtk.Template.Child("repository_keys")
    available_keys = Gtk.Template.Child("available_keys")
    add_key_button = Gtk.Template.Child("add_key_button")
    remove_key_button = Gtk.Template.Child("remove_key_button")
    generate_ssh_key_button = Gtk.Template.Child('generate_ssh_key_button')
    public_key_box = Gtk.Template.Child('public_key')

    def setup(self, password_store_path):

        # git repo management
        current_repo_remote = get_respository_remote()
        self.repo_url_entry.set_text(current_repo_remote or "")

        # GPG Key management
        current_key_ids = get_key_ids(password_store_path)
        self.gpg_key_box.foreach(lambda child: self.gpg_key_box.remove(child))

        for key_id in current_key_ids:
            self.gpg_key_box.add(KeyIdRow(key_id))

        self.gpg_key_box.show_all()

        run_background_task(lambda: get_unused_available_gpg_keys(
            current_key_ids)).done(self.update_available_keys, print)

        self.update_ssh_widgets(get_ssh_pub_keys())

    def get_repo_remote(self):
        return self.repo_url_entry.get_text()

    def get_selected_keys(self):
        new_key_ids = []
        self.gpg_key_box.show_all()
        self.gpg_key_box.foreach(
            lambda child: new_key_ids.append(child.key_id))
        return new_key_ids

    @Gtk.Template.Callback()
    def remove_selected_key(self, button):
        row = self.gpg_key_box.get_selected_row()
        if row is not None:
            self.gpg_key_box.remove(row)
            self.remove_key_button.set_sensitive(False)

            used_key_ids = []
            self.gpg_key_box.foreach(
                lambda child: used_key_ids.append(child.key_id))
            run_background_task(lambda: get_unused_available_gpg_keys(
                used_key_ids)).done(self.update_available_keys, print)

    @Gtk.Template.Callback()
    def add_selected_key(self, button):
        key_id = self.available_keys.get_active_text()
        if key_id is not None:
            self.gpg_key_box.add(KeyIdRow(key_id))
            used_key_ids = []
            self.gpg_key_box.show_all()
            self.gpg_key_box.foreach(
                lambda child: used_key_ids.append(child.key_id))
            run_background_task(lambda: get_unused_available_gpg_keys(
                used_key_ids)).done(self.update_available_keys)

    def update_available_keys(self, usable_keys):
        self.available_keys.remove_all()

        if usable_keys:
            for key in usable_keys:
                self.available_keys.append_text(key)
            self.add_key_button.set_sensitive(True)
            self.available_keys.set_sensitive(True)

        else:
            self.available_keys.set_sensitive(False)
            self.add_key_button.set_sensitive(False)
            self.available_keys.append_text("No keys can be added")
            self.available_keys.set_active(0)

    @Gtk.Template.Callback()
    def run_ssh_keygen_and_update(self):
        run_background_task(generate_ssh_keypair).done(
            lambda _: self.update_ssh_widgets(get_ssh_pub_keys()))

    def update_ssh_widgets(self, ssh_keys):
        if ssh_keys:
            self.public_key_box.get_buffer().set_text("\n".join(ssh_keys))
            self.public_key_box.show()
            self.generate_ssh_key_button.hide()
        else:
            self.public_key_box.hide()
            self.generate_ssh_key_button.show()

    @Gtk.Template.Callback()
    def key_selected(self, list_box, row):
        self.remove_key_button.set_sensitive(True)

    @Gtk.Template.Callback()
    def no_key_selected(self, list_box):
        self.remove_key_button.set_sensitive(False)
