import os
import os.path


class FolderStorage:
    def __init__(self, path, ext=None):
        self._path = path
        self._ext = ext

    def _to_path(self, name):
        return os.path.join(self._path, name)

    def exists(self, name):
        return os.path.isfile(self._to_path(name))

    def content(self, name, binary=False):
        path = self._to_path(name)
        if not os.path.isfile(path):
            return None
        with open(path, "rb" if binary else "r") as f:
            return f.read()

    def edit(self, name, content, binary=False):
        path = self._to_path(name)
        with open(path, "wb" if binary else "w") as f:
            f.write(content)

    def each(self):
        for i in os.listdir(self._path):
            i = os.path.join(self._path, i)
            if not os.path.isfile(i):
                continue
            i = os.path.split(i)[1]
            if self._ext is None:
                yield i
            else:
                i = os.path.splitext(i)
                if i[1] != self._ext:
                    continue
                yield i[0]

    def move(self, old_name, new_name):
        old_path = self._to_path(old_name)
        new_path = self._to_path(new_name)
        if os.path.isfile(new_path):
            return "{} already exists".format(new_name)
        try:
            os.rename(old_path, new_path)
        except OSError:
            return "failed to move '{}' to '{}', is the destination a directory?".format(old_path, new_path)

    def delete(self, name):
        path = self._to_path(name)
        try:
            os.remove(path)
        except OSError:
            return "failed to delete '{}', is it a directory?".format(path)
