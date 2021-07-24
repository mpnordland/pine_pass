import os
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

from .widgets import PasswordRow, KeyIdRow, PasswordEditDialog, NewPasswordDialog
from .background import run_background_task
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
        glade_file = os.path.join(self._assets_path, "ui.glade")
        self._builder.add_from_file(glade_file)

        self._window = self._builder.get_object("main_window")
        self._clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

    def run(self):
        handlers = {
            "gtk_main_quit": Gtk.main_quit,
            "on_password_search_changed": self.update_search_results,
            "password_row_activated": self.copy_password,
            "on_refresh_menu_item_activate": self.refresh_passwords,
            "on_prefs_menu_item_activate": self.show_preferences,
            "on_add_password_menu_item_activate": self.add_new_password,
        }
        self._builder.connect_signals(handlers)

        style_provider = Gtk.CssProvider()
        style_provider.load_from_path(
            os.path.join(self._assets_path, "ui.css"))

        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        self._window.show_all()
        Gtk.main()

    def update_search_results(self, entry):
        results = self._index.lookup(entry.get_text())
        if results:
            list_box = self._builder.get_object("results_list")
            list_box.foreach(lambda child: list_box.remove(child))

            for result in results:
                row = PasswordRow(result)
                row.set_button_callback(
                    lambda _: self.show_password_edit(result))
                list_box.add(row)

            list_box.show_all()

    def copy_password(self, list_box, row):
        password = get_password(row.entry)

        if password:
            self._clipboard.set_text(password, -1)
            revealer = self._builder.get_object("revealer")
            password_label = self._builder.get_object(
                "notification_password_name")

            password_label.set_text(row.entry)
            revealer.set_reveal_child(True)
            GLib.timeout_add_seconds(2, self.hide_notification, None)
            GLib.timeout_add_seconds(
                45, lambda _: self._clipboard.clear(), None)

    def hide_notification(self, what):
        revealer = self._builder.get_object("revealer")
        revealer.set_reveal_child(False)
        return False

    def refresh_passwords(self, button):
        run_background_task(sync_passwords).done(
            lambda _: self.reindex_passwords())

    def reindex_passwords(self):
        self._index = index_passwords(self._config["password-store-path"])

    def show_password_edit(self, password_path):
        password_entry = get_password_entry(password_path)

        dialog = PasswordEditDialog(
            password_path, password_entry, self._window)

        response = dialog.run()

        if response == Gtk.ResponseType.APPLY:
            new_password_entry = dialog.get_password_contents()
            write_password_entry(password_path, new_password_entry)
        else:
            pass

        dialog.destroy()

    def add_new_password(self, menu_item):
        dialog = NewPasswordDialog('', '', self._window)


        while True:
            response = dialog.run()

            if response == Gtk.ResponseType.APPLY:
                new_password_path = dialog.get_password_path()
                new_password_entry = dialog.get_password_contents()
                write_password = False
                if get_password(new_password_path) is None:
                    write_password = True
                else:
                    write_password = self.check_if_overwrite_desired(new_password_path)

                if write_password:
                    write_password_entry(new_password_path, new_password_entry)
                    break
                
            else:
                break

        dialog.destroy()

    def check_if_overwrite_desired(self, password_path):

        dialog = Gtk.MessageDialog(
            transient_for=self._window,
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

    def show_preferences(self, menu_item):
        dialog = self._builder.get_object("preferences_dialog")

        # git repo management
        current_repo_remote = get_respository_remote()

        repo_url_entry = self._builder.get_object("repo_url")

        repo_url_entry.set_text(current_repo_remote or "")

        # GPG Key management
        current_key_ids = get_key_ids(self._config["password-store-path"])
        gpg_key_box = self._builder.get_object("repository_keys")
        gpg_key_box.foreach(lambda child: gpg_key_box.remove(child))

        for key_id in current_key_ids:
            gpg_key_box.add(KeyIdRow(key_id))

        gpg_key_box.show_all()

        available_keys = self._builder.get_object("available_keys")
        add_key_button = self._builder.get_object("add_key_button")
        remove_key_button = self._builder.get_object("remove_key_button")

        gpg_key_box.connect('row-activated', lambda _,
                            __: remove_key_button.set_sensitive(True))
        gpg_key_box.connect(
            'unselect-all', lambda _: remove_key_button.set_sensitive(False))

        def get_unused_available_keys(used_keys):
            private_keys = get_available_gpg_keys()

            def key_filter(key):
                for cur_key in used_keys:
                    if f"<{cur_key}>" in key['uids'][0] or key['fingerprint'].endswith(cur_key):
                        return False
                return True

            return [key['fingerprint'] for key in filter(key_filter, private_keys)]

        def update_available_keys(usable_keys):
            available_keys.remove_all()

            if usable_keys:
                for key in usable_keys:
                    available_keys.append_text(key)
                add_key_button.set_sensitive(True)
                available_keys.set_sensitive(True)

            else:
                available_keys.set_sensitive(False)
                add_key_button.set_sensitive(False)
                available_keys.append_text("No keys can be added")
                available_keys.set_active(0)

        run_background_task(lambda: get_unused_available_keys(
            current_key_ids)).done(update_available_keys, print)

        def remove_selected_key(button):
            row = gpg_key_box.get_selected_row()
            if row is not None:
                gpg_key_box.remove(row)
                remove_key_button.set_sensitive(False)

                used_key_ids = []
                gpg_key_box.foreach(
                    lambda child: used_key_ids.append(child.key_id))
                run_background_task(lambda: get_unused_available_keys(
                    used_key_ids)).done(update_available_keys, print)

        remove_key_button.connect('clicked', remove_selected_key)

        def add_selected_key(button):
            key_id = available_keys.get_active_text()
            if key_id is not None:
                gpg_key_box.add(KeyIdRow(key_id))
                used_key_ids = []
                gpg_key_box.show_all()
                gpg_key_box.foreach(
                    lambda child: used_key_ids.append(child.key_id))
                run_background_task(lambda: get_unused_available_keys(
                    used_key_ids)).done(update_available_keys)

        add_key_button.connect('clicked', add_selected_key)

        # SSH management
        generate_ssh_key_button = self._builder.get_object(
            'generate_ssh_key_button')
        public_key_box = self._builder.get_object('public_key')

        def update_ssh_widgets(ssh_keys):
            if ssh_keys:
                public_key_box.get_buffer().set_text("\n".join(ssh_keys))
                public_key_box.show()
                generate_ssh_key_button.hide()
            else:
                public_key_box.hide()
                generate_ssh_key_button.show()

        def run_ssh_keygen_and_update():
            run_background_task(generate_ssh_keypair).done(
                lambda _: update_ssh_widgets(get_ssh_pub_keys()))

        generate_ssh_key_button.connect('clicked', run_ssh_keygen_and_update)

        update_ssh_widgets(get_ssh_pub_keys())

        response = dialog.run()
        if response == Gtk.ResponseType.APPLY:
            new_repo_remote = repo_url_entry.get_text()

            new_key_ids = []
            gpg_key_box.show_all()
            gpg_key_box.foreach(lambda child: new_key_ids.append(child.key_id))

            # the keys have changed
            if set(current_key_ids) != set(new_key_ids):
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
