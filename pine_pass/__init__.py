"""
A python module for reading password store data
"""

import subprocess
import os

__version__ = "0.0.2"


def get_password(password_path):
    result = subprocess.run(["pass", password_path], text=True, capture_output=True)
    if result.returncode == 0 and result.stdout:
        return result.stdout.splitlines()[0]

    return None


def sync_passwords():
    subprocess.run(["pass", "git", "pull", "--no-edit"])
    subprocess.run(["pass", "git", "push"])


def get_respository_remote():
    result = subprocess.run(
        ["pass", "git", "remote", "get-url", "origin"], text=True, capture_output=True
    )
    if result.returncode == 0 and result.stdout:
        return result.stdout.strip()
    return None


def get_key_ids(repository_path):
    try:
        with open(os.path.join(repository_path, ".gpg-id")) as key_id_file:
            return [id.strip() for id in key_id_file.readlines()]
    except IOError:
        pass  # we couldn't find the file

    return []


def update_key_ids(key_ids, sub_folder=None):
    command = ["pass", "init"]

    if sub_folder:
        command.extend(["-p", sub_folder])

    command.extend(key_ids)
    subprocess.run(command)


def check_for_password_store():
    result = subprocess.run(["pass"], text=True, capture_output=True)
    print(result.returncode)
    if result.returncode == 0 and "pasword store is empty" not in result.stdout:
        return True
    return False


def update_remote_url(remote_url):

    command = ["pass", "git", "remote" "set-url", "origin", remote_url]
    subprocess.run(command)


def clone_from_remote(remote_url, password_store_path):
    command = ["git", "clone", remote_url, password_store_path]
    subprocess.run(command)
