from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtWidgets import QTreeView


class FileExplorer(QTreeView):

    file_open_requested = pyqtSignal(str)

    def __init__(self, root_path="."):
        super().__init__()

        self.model = QFileSystemModel()

        self.model.setRootPath(root_path)

        self.setModel(self.model)
        self.setRootIndex(
            self.model.index(root_path)
        )

        self.doubleClicked.connect(
            self._on_double_click
        )

        # Hide trash columns
        self.hideColumn(1)
        self.hideColumn(2)
        self.hideColumn(3)

    def _on_double_click(self, index):

        path = self.model.filePath(index)

        self.file_open_requested.emit(path)