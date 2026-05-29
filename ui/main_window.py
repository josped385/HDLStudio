from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QMessageBox

from ui.docks.file_explorer_dock import FileExplorerDock
from ui.docks.terminal_dock import TerminalDock
from ui.editor_tabs import EditorTabs
from ui.panels.status_bar import IDEStatusBar
from ui.toolbar import MainToolBar
from ui.styles import MAIN_STYLE, build_stylesheet

from core.project import Project

from ui.actions import IDEActions
from themes.theme_manager import ThemeManager
from core.build_system import BuildSystem


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("HDLStudio")
        self.resize(1400, 900)

        self.setWindowIcon(QIcon("assets/icons/app_icon.png"))
        self.setIconSize(QSize(20, 20))

        self.setStyleSheet(MAIN_STYLE)

        self.ide_actions = IDEActions(self)

        self.project = Project()
        self.build_system = BuildSystem(self.project)

        self._setup_ui()
        self._warn_if_no_iverilog()

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

        menu = self.menuBar()

        # FILE
        file_menu = menu.addMenu("File")
        file_menu.addAction(self.ide_actions.new_file)
        file_menu.addAction(self.ide_actions.open_file)
        file_menu.addAction(self.ide_actions.open_project)

        file_menu.addSeparator()
        file_menu.addAction(self.ide_actions.save)
        file_menu.addAction(self.ide_actions.save_as)

        # BUILD
        build_menu = menu.addMenu("Build")
        build_menu.addAction(self.ide_actions.compile)
        build_menu.addAction(self.ide_actions.run)

        # VIEW
        view_menu = menu.addMenu("View")
        view_menu.addAction(self.ide_actions.toggle_terminal)
        view_menu.addAction(self.ide_actions.toggle_explorer)

        # VIEW
        view_menu.addSeparator()
        view_menu.addAction(self.ide_actions.toggle_theme)

        # HELP
        help_menu = menu.addMenu("Help")
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self._show_about)

    # ---------------- EDITOR ----------------

    def _setup_editor(self):

        self.editor_tabs = EditorTabs()
        self.setCentralWidget(self.editor_tabs)

    # ---------------- TOOLBAR ----------------

    def _setup_toolbar(self):

        self.toolbar = MainToolBar(self)
        self.addToolBar(self.toolbar)

    # ---------------- FILE EXPLORER ----------------

    def _setup_file_explorer(self):

        self.file_explorer_dock = FileExplorerDock(self)

        self.addDockWidget(
            Qt.DockWidgetArea.LeftDockWidgetArea,
            self.file_explorer_dock
        )

        self.file_explorer_dock.explorer.file_open_requested.connect(
            self.open_project_file
        )

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

    # ---------------- FILE CONTEXT ----------------

    def _refresh_build_context(self, filepath=None):

        if not filepath:
            tab = self.editor_tabs.current_tab()
            if tab and tab.path:
                filepath = tab.path

        if filepath:
            self.build_system.set_working_dir_from_file(filepath)

        if self.project and self.project.is_loaded():
            self.build_system.project = self.project
        else:
            self.build_system.project = None

        self.build_system.auto_select_files()
        self.toolbar.refresh_file_lists()

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
        self._refresh_build_context(path)

    def open_project_file(self, path):

        self.editor_tabs.open_file(path)
        self._refresh_build_context(path)

    def save_current_file(self):

        tab = self.editor_tabs.current_tab()

        if not tab:
            return

        if not tab.path:
            self.save_as_file()
            return

        tab.save()

    def new_file(self):

        self.editor_tabs.new_file()

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
        self._refresh_build_context(path)

    def open_folder(self):

        from PyQt6.QtWidgets import QFileDialog

        path = QFileDialog.getExistingDirectory(
            self,
            "Open Project Folder"
        )

        if not path:
            return

        self.project.load(path)
        self.build_system.project = self.project

        self.editor_tabs.set_project(self.project)

        self.file_explorer_dock.explorer.setRootIndex(
            self.file_explorer_dock.explorer.model.index(path)
        )

        self._refresh_build_context()
        self.status.showMessage(f"Project loaded: {self.project.name}")

    def _warn_if_no_iverilog(self):

        if not self.build_system.iverilog_available():
            self.status.showMessage(
                "Icarus Verilog not found in iverilog/ — compile/run disabled"
            )

    # ---------------- CLOSE EVENT ----------------

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

    # ---------------- BUILD SYSTEM ----------------

    def _ensure_files_saved(self):

        any_saved = False
        for tab in self.editor_tabs.tabs.values():
            if tab.modified:
                tab.save()
                any_saved = True
        return any_saved

    def compile_project(self):

        self._ensure_files_saved()
        self._refresh_build_context()

        self.status.showMessage("Compiling...")
        self.terminal_dock.output.append("═" * 50 + "\n")
        self.terminal_dock.output.append(">> COMPILING\n\n")

        def write(text):
            self.terminal_dock.output.append(text)

        ok = self.build_system.compile(write)

        self.status.showMessage(
            "Compilation successful" if ok else "Compilation failed"
        )

    def run_project(self):

        self._ensure_files_saved()

        self.status.showMessage("Running...")
        self.terminal_dock.output.append("═" * 50 + "\n")
        self.terminal_dock.output.append(">> RUNNING SIMULATION\n\n")

        def write(text):
            self.terminal_dock.output.append(text)

        ok = self.build_system.run(write)

        self.status.showMessage(
            "Simulation finished" if ok else "Simulation failed"
        )

    def toggle_terminal(self):

        visible = self.terminal_dock.isVisible()
        self.terminal_dock.setVisible(not visible)

    def toggle_explorer(self):

        visible = self.file_explorer_dock.isVisible()
        self.file_explorer_dock.setVisible(not visible)

    def toggle_theme(self):

        new_theme = "light" if ThemeManager.current_theme == "dark" else "dark"
        ThemeManager.set_theme(new_theme)
        self.setStyleSheet(build_stylesheet())
        self.status.showMessage(f"Switched to {new_theme} theme")

    def _show_about(self):

        QMessageBox.about(
            self,
            "About HDLStudio",
            "HDLStudio v0.1.0\n\n"
            "A lightweight IDE for HDL development.\n"
            "Supports Verilog, SystemVerilog, and VHDL."
        )