"""
A python module for reading password store data
"""

import string
import secrets
import subprocess
import os

import gnupg

__version__ = "0.0.2"


def get_password_entry(password_path):
    result = subprocess.run(["pass", password_path],
                            text=True, capture_output=True)
    if result.returncode == 0 and result.stdout:
        return result.stdout

    return None


def get_password(password_path):
    result = get_password_entry(password_path)
    if result:
        return result.splitlines()[0]

    return None


def write_password_entry(password_path, password_entry):
    """
    Writes password back to file. Will overwrite existing entries.
    """
    command = ["pass", "insert", "--multiline", "--force", password_path]
    subprocess.run(command, input=password_entry,
                            text=True, capture_output=True)

def move_password_entry(old_path, new_path):
    """
    Changes locaction of password file. Will overwrite existing entries.
    """
    command = ["pass", "mv", "--force", old_path, new_path]
    subprocess.run(command)



def check_for_password_store():
    result = subprocess.run(["pass"], text=True, capture_output=True)
    print(result.returncode)
    if result.returncode == 0 and "password store is empty" not in result.stdout:
        return True
    return False


def generate_password(length=100, lower_alpha=True, upper_alpha=True, numerals=True, symbols=True, custom_symbols=None):
    alphabet = ''
    if lower_alpha or upper_alpha:
        alphabet += string.ascii_letters

    if numerals:
        alphabet += string.digits

    symbol_list = ''
    if symbols and isinstance(custom_symbols, str):
        alphabet += custom_symbols
        symbol_list = custom_symbols
    elif symbols:
        alphabet += string.punctuation
        symbol_list = string.punctuation

    while True:
        password = ''.join(secrets.choice(alphabet) for i in range(length))

        passes_lower_alpha = (not lower_alpha) or any(c.islower() for c in password)

        passes_upper_alpha = (not upper_alpha) or any(c.isupper() for c in password)
        
        passes_numerals =  (not numerals) or any(c.isdigit() for c in password)

        passes_symbols = (not symbols) or any(c in symbol_list for c in password)

        if passes_lower_alpha and passes_upper_alpha and passes_numerals and passes_symbols:
            return password


# repository management

def update_remote_url(remote_url):

    command=["pass", "git", "remote" "set-url", "origin", remote_url]
    subprocess.run(command)


def clone_from_remote(remote_url, password_store_path):
    command=["git", "clone", remote_url, password_store_path]
    subprocess.run(command)

def get_respository_remote():
    result=subprocess.run(
        ["pass", "git", "remote", "get-url", "origin"], text=True, capture_output=True
    )
    if result.returncode == 0 and result.stdout:
        return result.stdout.strip()
    return None

def sync_passwords():
    subprocess.run(["pass", "git", "pull", "--no-edit"])
    subprocess.run(["pass", "git", "push"])


# Key Management

def get_key_ids(repository_path):
    try:
        with open(os.path.join(repository_path, ".gpg-id")) as key_id_file:
            return [id.strip() for id in key_id_file.readlines()]
    except IOError:
        pass  # we couldn't find the file

    return []


def update_key_ids(key_ids, sub_folder=None):
    command=["pass", "init"]

    if sub_folder:
        command.extend(["-p", sub_folder])

    command.extend(key_ids)
    subprocess.run(command)


def get_ssh_pub_keys():
    """
    Get any registered SSH identities
    """
    command=["ssh-add", "-L"]
    result=subprocess.run(command, text=True, capture_output=True)

    if result.returncode == 0 and "The agent has no identities." not in result.stdout:
        return result.stdout.splitlines()

    return None


def generate_ssh_keypair(key_type="rsa"):
    """
    Generates id_rsa and id_rsa.pub using ssh-keygen
    Uses default location!! Might overwrite existing keys!
    """
    command=["ssh-keygen", "-t", key_type, "-f",
               os.path.expanduser("~/.ssh/id_" + key_type)]
    subprocess.run(command)


def export_public_keys(gpg_key_id, ssh_pub_key):
    """
    Gathers ssh and gpg public keys into a folder
    in the home directory so they can be easily
    distributed to the server, other clients, etc.
    """

    gpg=gnupg.GPG()
    ascii_armored_public_keys=gpg.export_keys([gpg_key_id])
    export_dir=os.path.expanduser("~/pine_pass_keys")

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
    gpg=gnupg.GPG()
    private_keys=gpg.list_keys(True)  # Gets private keys
    return list(filter(lambda key: "e" in key["cap"].lower(), private_keys))

def get_unused_available_gpg_keys(used_gpg_keys):
    private_keys = get_available_gpg_keys()

    def key_filter(key):
        for cur_key in used_gpg_keys:
            if f"<{cur_key}>" in key['uids'][0] or key['fingerprint'].endswith(cur_key):
                return False
        return True

    return [key['fingerprint'] for key in filter(key_filter, private_keys)]