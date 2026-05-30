import os

from PyQt6.QtCore import Qt, QSize, QEvent
from PyQt6.QtGui import QIcon, QKeySequence, QShortcut
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QApplication

from ui.docks.file_explorer_dock import FileExplorerDock
from ui.docks.signal_dock import SignalDock
from ui.docks.terminal_dock import TerminalDock
from ui.editor_tabs import EditorTabs
from ui.panels.status_bar import IDEStatusBar
from ui.toolbar import MainToolBar
from ui.activity_bar import ActivityBar
from ui.styles import MAIN_STYLE, build_stylesheet

from core.project import Project

from ui.actions import IDEActions
from themes.theme_manager import ThemeManager
from core.build_system import BuildSystem
from core.wave_viewer import WaveViewer


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
        self.wave_viewer = WaveViewer()

        self._setup_ui()
        self._warn_if_no_iverilog()
        self._refresh_icons()

        QApplication.instance().installEventFilter(self)

    # ---------------- UI ----------------

    def _setup_ui(self):

        self._setup_menu_bar()
        self._setup_editor()
        self._setup_toolbar()
        self._setup_activity_bar()
        self._setup_file_explorer()
        self._setup_connections()
        self._setup_terminal()
        self._setup_status_bar()

    # ---------------- MENU ----------------

    def _setup_menu_bar(self):

        menu = self.menuBar()

        file_menu = menu.addMenu("File")
        file_menu.addAction(self.ide_actions.new_file)
        file_menu.addAction(self.ide_actions.open_file)
        file_menu.addAction(self.ide_actions.open_project)

        file_menu.addSeparator()
        file_menu.addAction(self.ide_actions.save)
        file_menu.addAction(self.ide_actions.save_as)

        build_menu = menu.addMenu("Build")
        build_menu.addAction(self.ide_actions.compile)
        build_menu.addAction(self.ide_actions.run)

        view_menu = menu.addMenu("View")
        view_menu.addAction(self.ide_actions.toggle_terminal)
        view_menu.addAction(self.ide_actions.toggle_explorer)

        view_menu.addAction(self.ide_actions.view_waves)

        view_menu.addSeparator()
        view_menu.addAction(self.ide_actions.toggle_theme)

        help_menu = menu.addMenu("Help")
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self._show_about)

    # ---------------- EDITOR ----------------

    def _setup_editor(self):

        self.editor_tabs = EditorTabs()
        self.setCentralWidget(self.editor_tabs)
        self.editor_tabs.currentChanged.connect(self._on_tab_changed)

    # ---------------- TOOLBAR ----------------

    def _setup_toolbar(self):

        self.toolbar = MainToolBar(self)
        self.addToolBar(self.toolbar)

    # ---------------- ACTIVITY BAR ----------------

    def _setup_activity_bar(self):

        self.activity_bar = ActivityBar(self)
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.activity_bar)

    def _show_activity_panel(self, panel):

        if panel == "explorer":
            self.signal_dock.hide()
            self.file_explorer_dock.show()
            self.file_explorer_dock.raise_()
        else:
            self.file_explorer_dock.hide()
            self.signal_dock.show()
            self.signal_dock.raise_()

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

    # ---------------- CONNECTIONS ----------------

    def _setup_connections(self):

        self.signal_dock = SignalDock(self)

        self.addDockWidget(
            Qt.DockWidgetArea.LeftDockWidgetArea,
            self.signal_dock
        )

        self.signal_dock.hide()

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

    # ---------------- TAB CHANGE ----------------

    def _on_tab_changed(self, index):

        tab = self.editor_tabs.current_tab()
        if tab and tab.path:
            self.signal_dock.update_from_file(tab.path)
        else:
            self.signal_dock.update_from_file(None)

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
        self.signal_dock.update_from_file(filepath)

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
        self.signal_dock.update_from_file(tab.path)

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

        path, _ = QFileDialog.getSaveFileName(
            self, "Save compiled simulation as",
            "build/simulation.vvp",
            "VVP files (*.vvp);;All Files (*)"
        )
        if not path:
            return

        self.status.showMessage("Compiling...")
        self.terminal_dock.output.append("=" * 50 + "\n")
        self.terminal_dock.output.append(">> COMPILING\n\n")

        def write(text):
            self.terminal_dock.output.append(text)

        ok = self.build_system.compile(write, output_path=path)

        self.status.showMessage(
            "Compilation successful" if ok else "Compilation failed"
        )

    def run_project(self):

        self._ensure_files_saved()
        self._refresh_build_context()

        vvp_path, _ = QFileDialog.getOpenFileName(
            self, "Select simulation to run",
            "build/",
            "VVP files (*.vvp);;All Files (*)"
        )
        if not vvp_path:
            return

        vcd_path, _ = QFileDialog.getSaveFileName(
            self, "Save waveform as",
            "waves.vcd",
            "VCD files (*.vcd);;FST files (*.fst);;All Files (*)"
        )
        if not vcd_path:
            return

        self.status.showMessage("Running...")
        self.terminal_dock.output.append("=" * 50 + "\n")
        self.terminal_dock.output.append(">> RUNNING SIMULATION\n\n")

        def write(text):
            self.terminal_dock.output.append(text)

        ok = self.build_system.run(write, vvp_path=vvp_path)

        if ok:
            generated = self.build_system.last_vcd_path
            if generated and os.path.isfile(generated):
                os.makedirs(os.path.dirname(vcd_path), exist_ok=True)
                try:
                    if os.path.normpath(generated) != os.path.normpath(vcd_path):
                        os.replace(generated, vcd_path)
                    self.build_system.last_vcd_path = vcd_path
                    write(f"\n>> Waveform saved as: {os.path.basename(vcd_path)}\n")
                    write(f"   Press F7 to open in GTKWave\n")
                except OSError as e:
                    write(f"\n>> Could not rename waveform: {e}\n")

        self.status.showMessage(
            "Simulation finished" if ok else "Simulation failed"
        )

    def view_waves(self):

        if not self.wave_viewer.available:
            self.status.showMessage(
                "GTKWave not found — check gtkwave/bin/gtkwave.exe"
            )
            return

        vcd, _ = QFileDialog.getOpenFileName(
            self, "Open waveform",
            "",
            "Waveform files (*.vcd *.fst *.lxt *.lxt2 *.ghw);;All Files (*)"
        )
        if not vcd:
            return

        ok = self.wave_viewer.open(vcd)
        if ok:
            self.status.showMessage(f"GTKWave: {os.path.basename(vcd)}")
        else:
            self.status.showMessage("Failed to launch GTKWave")

    def toggle_terminal(self):

        visible = self.terminal_dock.isVisible()
        self.terminal_dock.setVisible(not visible)

    def toggle_explorer(self):

        visible = self.file_explorer_dock.isVisible()
        if visible:
            self.file_explorer_dock.hide()
            self.activity_bar.explorer_btn.setChecked(False)
        else:
            self._show_activity_panel("explorer")

    def _refresh_icons(self):

        from themes.theme_manager import ThemeManager as TM
        icon_map = {
            "file_explorer": self.activity_bar.explorer_btn,
            "connections": self.activity_bar.connections_btn,
        }
        for name, action in icon_map.items():
            action.setIcon(QIcon(TM.icon(name)))

        toolbar_icons = {
            "new": self.ide_actions.new_file,
            "open": self.ide_actions.open_file,
            "open_folder": self.ide_actions.open_project,
            "save": self.ide_actions.save,
            "save_as": self.ide_actions.save_as,
            "compile": self.ide_actions.compile,
            "play": self.ide_actions.run,
            "wave": self.ide_actions.view_waves,
            "darklight": self.ide_actions.toggle_theme,
            "terminal": self.ide_actions.toggle_terminal,
        }
        for name, action in toolbar_icons.items():
            action.setIcon(QIcon(TM.icon(name)))

        for i in range(self.editor_tabs.count()):
            self.editor_tabs.setTabIcon(i, QIcon(TM.icon("file")))

    def toggle_theme(self):

        new_theme = "light" if ThemeManager.current_theme == "dark" else "dark"
        ThemeManager.set_theme(new_theme)
        colors = ThemeManager.colors()

        self.setStyleSheet(build_stylesheet())

        self.activity_bar.apply_theme(colors)
        self.toolbar.apply_theme(colors)
        self.terminal_dock.apply_theme(colors)
        self.signal_dock.apply_theme(colors)

        self.editor_tabs._style_plus_tab_bar()
        for tab in self.editor_tabs.tabs.values():
            tab.editor.apply_theme_from_colors(colors)

        self._refresh_icons()

        self.status.showMessage(f"Switched to {new_theme} theme")

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            mods = event.modifiers()
            if (event.key() == Qt.Key.Key_T
                    and mods & Qt.KeyboardModifier.ControlModifier
                    and mods & Qt.KeyboardModifier.ShiftModifier
                    and not (mods & Qt.KeyboardModifier.AltModifier)):
                self.toggle_theme()
                return True
        return super().eventFilter(obj, event)

    def _show_about(self):

        QMessageBox.about(
            self,
            "About HDLStudio",
            "HDLStudio v0.1.0\n\n"
            "A lightweight IDE for HDL development.\n"
            "Supports Verilog, SystemVerilog, and VHDL."
        )