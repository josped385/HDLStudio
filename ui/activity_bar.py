from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QToolBar, QWidget, QSizePolicy


class ActivityBar(QToolBar):

    def __init__(self, parent=None):
        super().__init__("Activity Bar", parent)

        self.setMovable(False)
        self.setOrientation(Qt.Orientation.Vertical)
        self.setIconSize(QSize(22, 22))
        self.setFixedWidth(44)

        self.setStyleSheet("""
            QToolBar {
                background-color: #252526;
                border: none;
                spacing: 0px;
                padding: 0px;
            }
            QToolButton {
                border: none;
                border-radius: 0px;
                padding: 10px 8px;
                margin: 0px;
                icon-size: 22px;
            }
            QToolButton:hover {
                background-color: #2a2d2e;
            }
            QToolButton:checked {
                background-color: #37373d;
                border-left: 2px solid #3d7eff;
            }
        """)

        self.main = parent
        self._build()

    def _build(self):

        self.explorer_btn = self.addAction(
            QIcon("assets/icons/file_explorer.svg"),
            "File Explorer"
        )
        self.explorer_btn.setCheckable(True)
        self.explorer_btn.setChecked(True)
        self.explorer_btn.triggered.connect(self._on_explorer)

        self.connections_btn = self.addAction(
            QIcon("assets/icons/connections.svg"),
            "Connections"
        )
        self.connections_btn.setCheckable(True)
        self.connections_btn.triggered.connect(self._on_connections)

        spacer = QWidget()
        spacer.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.addWidget(spacer)

    def _on_explorer(self):
        self.explorer_btn.setChecked(True)
        self.connections_btn.setChecked(False)
        self.main._show_activity_panel("explorer")

    def _on_connections(self):
        self.connections_btn.setChecked(True)
        self.explorer_btn.setChecked(False)
        self.main._show_activity_panel("connections")