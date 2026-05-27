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

    @property
    def filename(self):

        if self.path is None:
            return "untitled"

        return os.path.basename(self.path)

    def load_file(self):

        if self.path is None:
            return

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                content = f.read()

            self.editor.blockSignals(True)
            self.editor.setText(content)
            self.editor.blockSignals(False)

            self.modified = False
            self.modified_changed.emit(False)

        except Exception as e:
            print(f"Error loading file: {e}")

    def save(self):

        if self.path is None:
            return

        try:
            with open(self.path, "w", encoding="utf-8") as f:
                f.write(self.editor.text())

            self.modified = False
            self.modified_changed.emit(False)

        except Exception as e:
            print(f"Error saving file: {e}")

    def _on_text_changed(self):

        if not self.modified:
            self.modified = True
            self.modified_changed.emit(True)