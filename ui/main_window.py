from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow

from ui.docks.file_explorer_dock import FileExplorerDock
from ui.docks.terminal_dock import TerminalDock
from ui.editor_tabs import EditorTabs
from ui.panels.status_bar import IDEStatusBar
from ui.toolbar import MainToolBar
from ui.styles import MAIN_STYLE


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("HDLStudio")
        self.resize(1400, 900)

        self.setWindowIcon(
            QIcon("assets/icons/app_icon.png")
        )

        self.setIconSize(QSize(20, 20))

        self.setStyleSheet(MAIN_STYLE)

        self._setup_ui()

    def _setup_ui(self):

        self._setup_menu_bar()

        self._setup_editor()

        self._setup_toolbar()

        self._setup_file_explorer()

        self._setup_terminal()

        self._setup_status_bar()

    def _setup_menu_bar(self):

        menu_bar = self.menuBar()

        menu_bar.addMenu("File")
        menu_bar.addMenu("Edit")
        menu_bar.addMenu("View")
        menu_bar.addMenu("Build")
        menu_bar.addMenu("Tools")
        menu_bar.addMenu("Help")

    def _setup_editor(self):

        self.editor_tabs = EditorTabs()

        self.setCentralWidget(
            self.editor_tabs
        )

    def _setup_toolbar(self):

        toolbar = MainToolBar(self)

        self.addToolBar(toolbar)

    def _setup_file_explorer(self):

        self.file_explorer_dock = FileExplorerDock(self)

        self.addDockWidget(
            Qt.DockWidgetArea.LeftDockWidgetArea,
            self.file_explorer_dock
        )

        self.file_explorer_dock.explorer.file_open_requested.connect(
            self.editor_tabs.open_file
        )

    def _setup_terminal(self):

        self.terminal_dock = TerminalDock(self)

        self.addDockWidget(
            Qt.DockWidgetArea.BottomDockWidgetArea,
            self.terminal_dock
        )

    def _setup_status_bar(self):

        self.status = IDEStatusBar()

        self.setStatusBar(self.status)