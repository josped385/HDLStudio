from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDockWidget

from ui.file_explorer import FileExplorer


class FileExplorerDock(QDockWidget):

    def __init__(self, parent=None):
        super().__init__("Project", parent)

        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
        )

        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable |
            QDockWidget.DockWidgetFeature.DockWidgetMovable
        )

        self.explorer = FileExplorer()

        self.setWidget(self.explorer)