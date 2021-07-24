# Pine Pass

GUI for password-store.org written with Python and GTK.
Originally written for the PinePhone but should be compatible
with most Linux distros.

## Current Features

* Can search through passwords in repository and copy the password to the clipboard
* Can display/edit passwords
* Can insert new passwords (can't generate passwords yet!)
* Has a preference screen that can handle simple repository and gpg key id management
* Shows you the first SSH key it found or offers to generate one (only generates RSA keys right now, uses ssh-keygen)

## Requirements

* Python
* Python GObject introspection bindings
* GTK 3
* pass
* python-gnupg
* python-promise
* ssh-add
* ssh-keygen


## No Maintenance Guarantee!

I promise not to maintain Pine Pass. If I do maintain it, you can pipe a request to `/dev/null` for your money back.

## Build instructions

Uses flit to make sdist and wheel

```
flit build

```

Installing the built package will add the pinepass command.

## TODO
* Add button to generate new password on add/edit screens
* Unify add/edit password dialogs
* Figure out how to add .desktop file to allow opening from launchers.
