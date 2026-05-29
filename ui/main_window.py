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

        self._setup_ui()

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

    # ---------------- BUILD SYSTEM (STUBS) ----------------

    def _collect_hdl_files(self):

        if not self.project or not self.project.is_loaded():
            return []

        import glob as globmod
        hdl_files = []
        for ext in ("**/*.v", "**/*.sv", "**/*.vhd", "**/*.vhdl"):
            pattern = self.project.to_absolute(ext)
            hdl_files.extend(globmod.glob(pattern, recursive=True))
        return sorted(hdl_files)

    def compile_project(self):

        if not self.project or not self.project.is_loaded():
            self.status.showMessage("No project loaded")
            return

        self.status.showMessage("Compiling project...")

        files = self._collect_hdl_files()
        if files:
            self.terminal_dock.output.append(
                f"Found {len(files)} HDL file(s) for compilation:\n"
            )
            for f in files:
                rel = self.project.to_relative(f)
                self.terminal_dock.output.append(f"  {rel}\n")
            self.terminal_dock.output.append(
                "Compilation pipeline not yet configured.\n"
                "Install a simulator (iverilog/ghdl/verilator) to enable compilation.\n"
            )
        else:
            self.terminal_dock.output.append(
                "No HDL files found in project.\n"
            )

    def run_project(self):

        if not self.project or not self.project.is_loaded():
            self.status.showMessage("No project loaded")
            return

        self.status.showMessage("Running simulation...")

        files = self._collect_hdl_files()
        if files:
            self.terminal_dock.output.append(
                f"Run pipeline not yet configured.\n"
                f"Found {len(files)} HDL file(s) - compile before running.\n"
            )
        else:
            self.terminal_dock.output.append(
                "No HDL files found in project.\n"
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