# Pine Pass

GUI for password-store.org written with Python and GTK.
Originally written for the PinePhone but should be compatible
with most Linux distros.

## Current Features

Can search through passwords in repository and copy the password to the clipboard

## Requirements

* Python
* Python GObject introspection bindings
* GTK 3
* pass
* python-gnupg
* python-promise

## Build instructions

Uses flit to make sdist and wheel

```
flit build

```

Installing the built package will add the pinepass command.

## TODO
* Add settings screen/wizard for setting up from scratch
* Add button and screen to add/generate new passwords
* Add support for pass-otp extension
* Figure out how to add .desktop file to allow opening from launchers.
* Add screen to show all info in password file

### Plan for wizard

Decided not to use GtkAssistant because getting it to work with Glade was slowing me down.
Going to try to make settings dialog cover my cases. Probably easier/more flexible for users too.

Step 1 checks for existing ssh keys and offers to generate one if
it doesn't exist.

Step 2 checks for any GPG keys that have a private key for decryption.
Offers to generate one if none exists

Step 3 dumps the public keys of the selected key pairs from steps 1 & 2
into a folder in the home directory

Intermission: User distributes the public keys as needed. Would be good to have a way
to resume to this step if user closes application and restarts.

Step 4 prompts user for password repository git url and tries to clone it
proceed to step 5 if it succeeds

Step 5 checks key ids listed in password repository against the GPG keyring,
reporting any missing or untrusted keys. Asks user to fix any and then confirm

Step 6 Congratulate user