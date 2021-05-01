"""
A python module for reading password store data
"""

import subprocess

__version__ = "0.0.2"


def get_password(password_path):
    result = subprocess.run(['pass', password_path], text=True, capture_output=True)
    if result.returncode == 0 and result.stdout:
        return result.stdout.splitlines()[0]

    return None


def sync_passwords():
    subprocess.run(['pass', 'git', 'pull', '--no-edit'])
    subprocess.run(['pass', 'git', 'push'])
