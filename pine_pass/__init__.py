"""
A python module for reading password store data
"""

import subprocess
import os

import gnupg

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
    if result.returncode == 0 and "password store is empty" not in result.stdout:
        return True
    return False


def update_remote_url(remote_url):

    command = ["pass", "git", "remote" "set-url", "origin", remote_url]
    subprocess.run(command)


def clone_from_remote(remote_url, password_store_path):
    command = ["git", "clone", remote_url, password_store_path]
    subprocess.run(command)


def get_ssh_pub_keys():
    """
    Get any registered SSH identities
    """
    command = ["ssh-add", "-L"]
    result = subprocess.run(command, text=True, capture_output=True)

    if result.returncode == 0 and "The agent has no identities." not in result.stdout:
        return result.stdout.splitlines()

    return None


def generate_ssh_keypair(key_type="rsa"):
    """
    Generates id_rsa and id_rsa.pub using ssh-keygen
    Uses default location!! Might overwrite existing keys!
    """
    command = ["ssh-keygen", "-t", key_type, "-f", os.path.expanduser("~/.ssh/id_rsa")]
    subprocess.run(command)


def export_public_keys(gpg_key_id, ssh_pub_key):
    """
    Gathers ssh and gpg public keys into a folder
    in the home directory so they can be easily
    distributed to the server, other clients, etc.
    """

    gpg = gnupg.GPG()
    ascii_armored_public_keys = gpg.export_keys([gpg_key_id])
    export_dir = os.path.expanduser("~/pine_pass_keys")

    if not os.path.exists(export_dir):
        os.makedirs(export_dir)

    with open(os.path.join(export_dir, "gpg_key.pub", "w")) as gpg_file:
        gpg_file.write(ascii_armored_public_keys)

    with open(os.path.join(export_dir, "ssh_key.pub", "w")) as gpg_file:
        gpg_file.write(ssh_pub_key)


def get_available_gpg_keys():
    """
    Gets a list of key pairs from the GPG keyring
    where a private key is available for decryption
    """
    gpg = gnupg.GPG()
    private_keys = gpg.list_keys(True)
    return list(filter(lambda key: "e" in key["cap"].lower(), private_keys))
