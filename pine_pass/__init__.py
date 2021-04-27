"""
A python module for reading password store data
"""

import subprocess

__version__ = "0.0.2"


def password_to_clipboard(password_path):
    subprocess.run(['pass', '-c', password_path])


def sync_passwords():
    subprocess.run(['pass', 'git', 'pull', '--no-edit'])
    subprocess.run(['pass', 'git', 'push'])
