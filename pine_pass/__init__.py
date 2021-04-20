"""
A python module for reading password store data
"""

import subprocess

__version__ = "0.0.1"


def password_to_clipboard(password_path):
    subprocess.run(['pass', '-c', password_path])
