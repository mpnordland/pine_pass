from pine_pass_gui.app import PinePassApp


config = {
    'password-store-pass': '~/.password-store'
}

app = PinePassApp(config)

app.run()