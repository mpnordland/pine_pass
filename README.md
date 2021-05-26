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