import os
from collections import defaultdict

class PasswordIndex:
    def __init__(self):
        self._index = defaultdict(list)

    def insert(self, key, path, sort=True):
        self._index[key].append(path)
        if sort:
            self.sort()


    def sort(self):
        self._index = defaultdict(list, [ (key, self._index[key]) for key in sorted(self._index.keys())])


    def lookup(self, key):
        key = key.lower()
        matched = False
        result = []
        for index_key, paths in self._index.items():
            if index_key.startswith(key):
                matched = True
                result.extend(paths)
            elif matched:
                break
        
        return result


def index_passwords(path="~/.password-store/"):
    path = os.path.expanduser(path)
    index = PasswordIndex()

    for dirpath, dirnames, filenames in os.walk(path):
        if '.git' in dirnames:
            dirnames.remove('.git')
        for filename in filter(lambda fname: not fname.startswith('.'), filenames):
            index.insert(filename.strip(".gpg").lower(), os.path.join(dirpath, filename), False)

    index.sort()
    return index
