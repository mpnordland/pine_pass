import os
import threading
from promise import Promise
from pine_pass import (
    get_password,
    sync_passwords,
    get_respository_remote,
    check_for_password_store,
    get_key_ids,
    update_remote_url,
    clone_from_remote,
    get_available_gpg_keys,
)

from .widgets import PasswordRow, KeyIdRow
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
                list_box.add(PasswordRow(result))

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
        self.run_background_task(sync_passwords).done(lambda _: self.reindex_passwords())

    def run_background_task(self, task):
        def _resolver(resolve, reject):
            def _inner_task():
                try:
                    result = task()
                    def _inner_callback():
                        resolve(result)
                        return False
                    GLib.idle_add(_inner_callback)
                except Exception as e:
                    reject(e)

            thread = threading.Thread(target=_inner_task)
            thread.daemon = True
            thread.start()


        return Promise(_resolver)


    def reindex_passwords(self):
        self._index = index_passwords(self._config["password-store-path"])

    def show_preferences(self, menu_item):
        dialog = self._builder.get_object("preferences_dialog")

        current_repo_remote = get_respository_remote()
        current_key_ids = get_key_ids(self._config["password-store-path"])

        repo_url_entry = self._builder.get_object("repo_url")

        repo_url_entry.set_text(current_repo_remote or "")

        list_box = self._builder.get_object("repository_keys")
        list_box.foreach(lambda child: list_box.remove(child))

        for key_id in current_key_ids:
            list_box.add(KeyIdRow(key_id))

        list_box.show_all()


        available_keys = self._builder.get_object("available_keys")
        add_key_button = self._builder.get_object("add_key_button")
        remove_key_button = self._builder.get_object("remove_key_button")

        list_box.connect('row-activated', lambda _, __: remove_key_button.set_sensitive(True))
        list_box.connect('unselect-all', lambda _: remove_key_button.set_sensitive(False))

        def get_unused_available_keys(used_keys) :
            private_keys = get_available_gpg_keys()
            def key_filter(key):
                for cur_key in used_keys:
                    if f"<{cur_key}>" in key['uids'][0] or key['fingerprint'].endswith(cur_key):
                        return False
                return True

            return [ key['fingerprint'] for key in filter(key_filter,private_keys)]
            
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

        self.run_background_task(lambda: get_unused_available_keys(current_key_ids)).done(update_available_keys, print)



        def remove_selected_key(button):
            row = list_box.get_selected_row()
            if row is not None:
                list_box.remove(row)
                remove_key_button.set_sensitive(False)

                used_key_ids = []
                list_box.foreach(lambda child: used_key_ids.append(child.key_id))
                self.run_background_task(lambda: get_unused_available_keys(used_key_ids)).done(update_available_keys, print)

        remove_key_button.connect('clicked', remove_selected_key)
            
        def add_selected_key(button):
            key_id = available_keys.get_active_text()
            if key_id is not None:
                list_box.add(KeyIdRow(key_id))
                used_key_ids = []
                list_box.show_all()
                list_box.foreach(lambda child: used_key_ids.append(child.key_id))
                self.run_background_task(lambda: get_unused_available_keys(used_key_ids)).done(update_available_keys)
        
        add_key_button.connect('clicked', add_selected_key)


        response = dialog.run()
        if response == Gtk.ResponseType.APPLY:
            new_repo_remote = repo_url_entry.get_text()

            # TODO: manage key ids something like this:
            # new_key_ids = [id.strip() for id in key_id_entry.get_text().split(",")]
            # we assume that duplicate key id's aren't useful
            # if set(current_key_ids) == set(new_key_ids):

            # if repository exists, update git repo remote
            if check_for_password_store():
                update_remote_url(new_repo_remote)
            else:  # otherwise clone from remote server
                clone_from_remote(
                    new_repo_remote, self._config["password-store-path"])

        else:
            pass

        dialog.hide()
