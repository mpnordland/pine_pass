import os
from .app import PinePassApp


def start_app():
    config = {
        "password-store-path": os.path.expanduser(
            os.getenv("PASSWORD_STORE_DIR") or "~/.password-store"
        )
    }

    app = PinePassApp(config)

    app.run()
