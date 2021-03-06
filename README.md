# Pine Pass

GUI for password-store.org written with Python and GTK.
Originally written for the PinePhone but should be compatible
with most Linux distros.

## Current Features

* Can search through passwords in repository and copy the password to the clipboard
* Can display/edit passwords
* Can generate and insert new passwords
* Has a preference screen that can handle simple repository and gpg key id management
* Shows you the first SSH key it found or offers to generate one (only generates RSA keys right now, uses ssh-keygen)

## Requirements

* Python
* Python GObject introspection bindings
* GTK 3
* pass
* python-gnupg
* python-promise
* python-build
* ssh-add
* ssh-keygen

Build deps:

* Make
* setuptools
* glib-compile-resources



## No Maintenance Guarantee!

I promise not to maintain Pine Pass. If I do maintain it, you can pipe a request to `/dev/null` for your money back.

## Build instructions

Uses setuptools to make sdist and wheel


```
make
```

once that finishes, you'll find a dist folder in the project root. In there will be a Python source package and a wheel.
You can install either one (I don't think it really matters) using `pip install <name of file>`. Then you can either run `pinepass` or find it in your application menu.

Installing the built package will add the pinepass command.

## TODO
* Figure out how to add .desktop file to allow opening from launchers.
