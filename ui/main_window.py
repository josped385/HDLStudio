from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QMessageBox

from ui.docks.file_explorer_dock import FileExplorerDock
from ui.docks.terminal_dock import TerminalDock
from ui.editor_tabs import EditorTabs
from ui.panels.status_bar import IDEStatusBar
from ui.toolbar import MainToolBar
from ui.styles import MAIN_STYLE

from core.project import Project

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("HDLStudio")
        self.resize(1400, 900)

        self.setWindowIcon(QIcon("assets/icons/app_icon.png"))
        self.setIconSize(QSize(20, 20))

        self.setStyleSheet(MAIN_STYLE)

        self._setup_ui()

        self.project = Project()

    # ---------------- UI ----------------

    def _setup_ui(self):

        self._setup_menu_bar()
        self._setup_editor()
        self._setup_toolbar()
        self._setup_file_explorer()
        self._setup_terminal()
        self._setup_status_bar()

    # ---------------- MENU ----------------

    def _setup_menu_bar(self):

        menu_bar = self.menuBar()

        menu_bar.addMenu("File")
        menu_bar.addMenu("Edit")
        menu_bar.addMenu("View")
        menu_bar.addMenu("Build")
        menu_bar.addMenu("Tools")
        menu_bar.addMenu("Help")

    # ---------------- EDITOR ----------------

    def _setup_editor(self):

        self.editor_tabs = EditorTabs()
        self.setCentralWidget(self.editor_tabs)

    # ---------------- TOOLBAR ----------------

    def _setup_toolbar(self):

        self.toolbar = MainToolBar(self)
        self.addToolBar(self.toolbar)

        self.toolbar.open_action.triggered.connect(self.open_file)
        self.toolbar.save_action.triggered.connect(self.save_current_file)
        self.toolbar.save_as_action.triggered.connect(self.save_as_file)
        self.toolbar.new_action.triggered.connect(self.new_file)

        self.toolbar.open_project_action.triggered.connect(self.open_folder)

    # ---------------- FILE EXPLORER ----------------

    def _setup_file_explorer(self):

        self.file_explorer_dock = FileExplorerDock(self)

        self.addDockWidget(
            Qt.DockWidgetArea.LeftDockWidgetArea,
            self.file_explorer_dock
        )

        # connect file open to IDE handler (not raw tabs)
        self.file_explorer_dock.explorer.file_open_requested.connect(
            self.open_project_file
        )

    def open_project_file(self, path):

        # future hook: validate project scope
        self.editor_tabs.open_file(path)

    # ---------------- TERMINAL ----------------

    def _setup_terminal(self):

        self.terminal_dock = TerminalDock(self)

        self.addDockWidget(
            Qt.DockWidgetArea.BottomDockWidgetArea,
            self.terminal_dock
        )

    # ---------------- STATUS BAR ----------------

    def _setup_status_bar(self):

        self.status = IDEStatusBar()
        self.setStatusBar(self.status)

    # ---------------- ACTIONS ----------------

    def open_file(self):

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "HDL Files (*.vhd *.v *.sv);;All Files (*)"
        )

        if not path:
            return

        self.editor_tabs.open_file(path)

    def save_current_file(self):

        tab = self.editor_tabs.current_tab()

        if not tab:
            return

        tab.save()

    def new_file(self):

        self.editor_tabs.new_file()

    def open_folder(self):

        from PyQt6.QtWidgets import QFileDialog

        path = QFileDialog.getExistingDirectory(
            self,
            "Open Project Folder"
        )

        if not path:
            return

        self.project.load(path)

        self.editor_tabs.set_project(self.project)

        self.file_explorer_dock.explorer.setRootIndex(
            self.file_explorer_dock.explorer.model.index(path)
        )

    def save_as_file(self):

        tab = self.editor_tabs.current_tab()

        if not tab:
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save As",
            "",
            "HDL Files (*.vhd *.v *.sv);;All Files (*)"
        )

        if not path:
            return

        self.editor_tabs.save_current_as(path)

    # ---------------- CLOSE EVENT (🔥 NUEVO) ----------------

    def closeEvent(self, event):

        tabs = self.editor_tabs.tabs

        dirty_tabs = [t for t in tabs.values() if t.modified]

        if not dirty_tabs:
            event.accept()
            return

        msg = QMessageBox(self)
        msg.setWindowTitle("Unsaved Changes")
        msg.setText("There are unsaved files. What do you want to do?")

        save_btn = msg.addButton("Save All", QMessageBox.ButtonRole.AcceptRole)
        discard_btn = msg.addButton("Discard", QMessageBox.ButtonRole.DestructiveRole)
        cancel_btn = msg.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)

        msg.exec()

        clicked = msg.clickedButton()

        if clicked == cancel_btn:
            event.ignore()
            return

        if clicked == discard_btn:
            event.accept()
            return

        if clicked == save_btn:

            for tab in dirty_tabs:
                tab.save()

            event.accept()