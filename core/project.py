import os


class Project:

    def __init__(self, root_path=None):

        self.root_path = None
        self.name = None

        if root_path:
            self.load(root_path)

    def load(self, root_path):

        self.root_path = os.path.abspath(root_path)
        self.name = os.path.basename(root_path)

    def is_loaded(self):

        return self.root_path is not None

    # ---------------- PATH HELPERS ----------------

    def is_inside(self, path):

        if not self.root_path:
            return False

        path = os.path.abspath(path)

        return os.path.commonpath([path, self.root_path]) == self.root_path

    def to_relative(self, path):

        if not self.root_path:
            return path

        return os.path.relpath(path, self.root_path)

    def to_absolute(self, path):

        if not self.root_path:
            return path

        if os.path.isabs(path):
            return path

        return os.path.join(self.root_path, path)