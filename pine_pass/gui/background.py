import threading
from promise import Promise

import gi

gi.require_version("Gtk", "3.0")

from gi.repository import GLib

def run_background_task(task):
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