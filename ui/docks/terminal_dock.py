from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDockWidget

from widgets.terminal_widget import TerminalWidget


class TerminalDock(QDockWidget):

    def __init__(self, parent=None):
        super().__init__("Terminal", parent)

        self.setAllowedAreas(
            Qt.DockWidgetArea.BottomDockWidgetArea
        )

        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable |
            QDockWidget.DockWidgetFeature.DockWidgetMovable
        )

        self.terminal = TerminalWidget()

        self.setWidget(self.terminal)