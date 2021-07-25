from pine_pass import (
    get_password,
    sync_passwords,
    get_respository_remote,
    check_for_password_store,
    get_key_ids,
    update_remote_url,
    clone_from_remote,
    get_available_gpg_keys,
    update_key_ids,
    get_ssh_pub_keys,
    generate_ssh_keypair,
    get_password_entry,
    write_password_entry,
)

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib


from .widgets import PasswordRow, KeyIdRow
from .dialogs import PasswordEditDialog, PreferencesDialog
from .background import run_background_task
from pine_pass.indexer import index_passwords

@Gtk.Template(resource_path="/me/rehack/pinepass/main_window.ui")
class MainWindow(Gtk.Window):
    __gtype_name__ = "MainWindow"

    _clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
    list_box = Gtk.Template.Child("results_list")
    revealer = Gtk.Template.Child("revealer")
    password_label = Gtk.Template.Child("notification_password_name")

    def setup(self, config):
        self._config = config
        self.reindex_passwords()

    @Gtk.Template.Callback()
    def gtk_main_quit(self, *args):
        Gtk.main_quit()

    @Gtk.Template.Callback("on_password_search_changed")
    def update_search_results(self, entry):
        results = self._index.lookup(entry.get_text())
        if results:
            self.list_box.foreach(lambda child: self.list_box.remove(child))

            for result in results:
                row = PasswordRow(result)
                row.set_button_callback(
                    lambda _: self.show_password_edit(result))
                self.list_box.add(row)

            self.list_box.show_all()

    @Gtk.Template.Callback('password_row_activated')
    def copy_password(self, list_box, row):
        password = get_password(row.entry)

        if password:
            self._clipboard.set_text(password, -1)

            self.password_label.set_text(row.entry)
            self.revealer.set_reveal_child(True)
            GLib.timeout_add_seconds(2, self.hide_notification, None)
            GLib.timeout_add_seconds(
                45, lambda _: self._clipboard.clear(), None)

    def hide_notification(self, what):
        self.revealer.set_reveal_child(False)
        return False

    @Gtk.Template.Callback("on_refresh_menu_item_activate")
    def refresh_passwords(self, button):
        run_background_task(sync_passwords).done(
            lambda _: self.reindex_passwords())

    def reindex_passwords(self):
        self._index = index_passwords(self._config["password-store-path"])

    def show_password_edit(self, password_path):
        password_entry = get_password_entry(password_path)

        dialog = PasswordEditDialog(transient_for=self)
        dialog.setup(password_path, password_entry)

        response = dialog.run()

        if response == Gtk.ResponseType.APPLY:
            new_password_entry = dialog.get_password_contents()
            write_password_entry(password_path, new_password_entry)
        else:
            pass

        dialog.destroy()

        
    @Gtk.Template.Callback("on_add_password_menu_item_activate")
    def add_new_password(self, menu_item):
        dialog = PasswordEditDialog(transient_for=self)
        dialog.setup('', '')

        while True:
            response = dialog.run()

            if response == Gtk.ResponseType.APPLY:
                new_password_path = dialog.get_password_path()
                new_password_entry = dialog.get_password_contents()
                write_password = False
                if get_password(new_password_path) is None:
                    write_password = True
                else:
                    write_password = self.check_if_overwrite_desired(
                        new_password_path)

                if write_password:
                    write_password_entry(new_password_path, new_password_entry)
                    break

            else:
                break

        dialog.destroy()

    def check_if_overwrite_desired(self, password_path):

        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"There is an existing password entry at {password_path}",
        )
        dialog.format_secondary_text(
            "Do you want to overwrite that password entry?"
        )
        response = dialog.run()
        dialog.destroy()

        return response == Gtk.ResponseType.YES


    @Gtk.Template.Callback('on_prefs_menu_item_activate')
    def show_preferences(self, menu_item):
        dialog = PreferencesDialog(transient_for=self)
        password_store_path = self._config['password-store-path']
        dialog.setup(password_store_path)

        response = dialog.run()
        if response == Gtk.ResponseType.APPLY:
            new_repo_remote = dialog.get_repo_remote()

            new_key_ids = dialog.get_selected_keys()
            # the keys have changed
            if set(get_key_ids(password_store_path)) != set(new_key_ids):
                run_background_task(lambda: update_key_ids(new_key_ids)).done(
                    lambda _: self.reindex_passwords())

            # if repository exists, update git repo remote
            if check_for_password_store():
                update_remote_url(new_repo_remote)
            else:  # otherwise clone from remote server
                clone_from_remote(
                    new_repo_remote, self._config["password-store-path"])

        else:
            pass

        dialog.hide()