import os
from PyQt6.QtCore import QObject, pyqtSignal

from widgets.code_editor import CodeEditor


class EditorTab(QObject):

    modified_changed = pyqtSignal(bool)

    def __init__(self, path=None):

        super().__init__()

        self.path = path
        self.editor = CodeEditor()
        self.modified = False

        self.editor.textChanged.connect(
            self._on_text_changed
        )

    # ---------------- NAME ----------------

    @property
    def filename(self):

        if self.path:
            return os.path.basename(self.path)

        return "untitled"

    # ---------------- LOAD ----------------

    def load_file(self):

        if not self.path:
            return

        with open(self.path, "r", encoding="utf-8") as f:
            content = f.read()

        self.editor.blockSignals(True)
        self.editor.setText(content)
        self.editor.blockSignals(False)

        self._set_modified(False)

    # ---------------- SAVE ----------------

    def save(self):

        if not self.path:
            return self.save_as()

        self._write_to_disk(self.path)
        self._set_modified(False)

    def save_as(self, new_path=None):

        # If no path provided, caller must give one
        if not new_path:
            return False

        self.path = new_path
        self._write_to_disk(self.path)
        self._set_modified(False)

        return True

    # ---------------- INTERNAL ----------------

    def _write_to_disk(self, path):

        with open(path, "w", encoding="utf-8") as f:
            f.write(self.editor.text())

    def _set_modified(self, value):

        if self.modified != value:
            self.modified = value
            self.modified_changed.emit(value)

    def _on_text_changed(self):

        if not self.modified:
            self._set_modified(True)