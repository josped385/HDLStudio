from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QTextEdit,
    QDockWidget,
)


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

        self.terminal = QTextEdit()

        self.terminal.setReadOnly(True)

        self.terminal.setPlainText(
            "HDLStudio terminal initialized...\n"
        )

        self.setWidget(self.terminal)