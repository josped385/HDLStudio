import os
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDockWidget, QVBoxLayout, QWidget, QLabel

from widgets.signal_tree import SignalTree
from core.hdl_parser import HDLParser


class SignalDock(QDockWidget):

    def __init__(self, parent=None):
        super().__init__("Connections", parent)

        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
        )

        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
        )

        self.container = QWidget()
        self.container.setObjectName("signalDockContainer")
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tree = SignalTree()
        layout.addWidget(self.tree)

        self.info_label = QLabel("No file open")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)
        self.info_label.hide()

        self.setWidget(self.container)

        from themes.theme_manager import ThemeManager
        self.apply_theme(ThemeManager.colors())

    def apply_theme(self, colors):
        self.container.setStyleSheet(
            f"#signalDockContainer {{ background-color: {colors['main_bg']}; }}"
        )
        self.tree.apply_theme(colors)
        self.info_label.setStyleSheet(
            f"color: {colors['text_secondary']}; padding: 20px;"
        )

    def update_from_file(self, filepath):
        if not filepath or not os.path.isfile(filepath):
            self.tree.clear()
            self.tree.hide()
            self.info_label.setText("No connections detected")
            self.info_label.show()
            return

        basename = os.path.basename(filepath)
        try:
            data = HDLParser.parse(filepath)
        except Exception:
            self.tree.clear()
            self.tree.hide()
            self.info_label.setText(f"Error parsing {basename}")
            self.info_label.show()
            return

        self.info_label.hide()
        self.tree.show()
        self.tree.display_signals(data)