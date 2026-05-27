from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QToolBar


class MainToolBar(QToolBar):

    def __init__(self, parent=None):
        super().__init__("Main Toolbar", parent)

        self.setMovable(False)
        self.setIconSize(parent.iconSize())

        self._create_actions()

    def _create_actions(self):

        self.open_project_action = QAction(
            QIcon("assets/icons/open_folder.svg"),
            "Open Project",
            self
        )

        self.new_action = QAction(
            QIcon("assets/icons/new.svg"),
            "New File",
            self
        )

        self.open_action = QAction(
            QIcon("assets/icons/open.svg"),
            "Open File",
            self
        )

        self.save_action = QAction(
            QIcon("assets/icons/save.svg"),
            "Save",
            self
        )

        self.save_as_action = QAction(
            QIcon("assets/icons/save_as.svg"),
            "Save As",
            self
        )

        self.compile_action = QAction(
            QIcon("assets/icons/compile.svg"),
            "Compile",
            self
        )

        self.run_action = QAction(
            QIcon("assets/icons/play.svg"),
            "Run",
            self
        )

        self.wave_action = QAction(
            QIcon("assets/icons/wave.svg"),
            "GTKWave",
            self
        )

        self.addAction(self.open_project_action)
        self.addAction(self.new_action)
        self.addAction(self.open_action)
        self.addAction(self.save_action)
        self.addAction(self.save_as_action)

        self.addSeparator()

        self.addAction(self.compile_action)
        self.addAction(self.run_action)
        self.addAction(self.wave_action)