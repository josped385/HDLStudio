from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QToolBar


class MainToolBar(QToolBar):

    def __init__(self, parent=None):
        super().__init__("Main Toolbar", parent)

        self.setMovable(False)

        self.setIconSize(parent.iconSize())

        self._create_actions()

    def _create_actions(self):

        run_action = QAction(
            QIcon("assets/icons/play.svg"),
            "Run",
            self
        )

        compile_action = QAction(
            QIcon("assets/icons/compile.svg"),
            "Compile",
            self
        )

        wave_action = QAction(
            QIcon("assets/icons/wave.svg"),
            "GTKWave",
            self
        )

        save_action = QAction(
            QIcon("assets/icons/save.svg"),
            "Save",
            self
        )

        open_action = QAction(
            QIcon("assets/icons/open.svg"),
            "Open",
            self
        )

        self.addAction(open_action)
        self.addAction(save_action)

        self.addSeparator()

        self.addAction(compile_action)
        self.addAction(run_action)
        self.addAction(wave_action)