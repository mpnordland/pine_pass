from .app import PinePassApp


def start_app():
    config = {
        'password-store-pass': '~/.password-store'
    }

    app = PinePassApp(config)

    app.run()
