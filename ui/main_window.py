import sys
import os
import re

from PyQt6.QtCore import QSize, Qt, QEvent
from PyQt6.QtGui import QIcon, QKeySequence, QShortcut
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QApplication, QDialog

from ui.docks.file_explorer_dock import FileExplorerDock
from ui.docks.git_dock import GitDock
from ui.docks.hierarchy_dock import HierarchyDock
from ui.docks.signal_dock import SignalDock
from ui.docks.bottom_panel import BottomPanel
from ui.docks.template_dock import TemplateDock
from ui.docks.debug_dock import DebugDock
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
from core.hover_data import HoverDatabase
from extensions.manager import ExtensionManager


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("HDLStudio")
        self.resize(1400, 900)

        if getattr(sys, 'frozen', False):
            _root = sys._MEIPASS
        else:
            _root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.setWindowIcon(QIcon(os.path.join(_root, "assets", "icons", "app_icon.png")))
        self.setIconSize(QSize(20, 20))

        self.setStyleSheet(MAIN_STYLE)

        self.ide_actions = IDEActions(self)

        self.project = Project()
        self.build_system = BuildSystem(self.project)
        self.wave_viewer = WaveViewer(self)
        self.wave_viewer.error_occurred.connect(self._on_wave_error)
        self.hover_db = HoverDatabase()
        self._last_synthesis_blif = None
        self._last_synthesis_json = None

        self.ext_manager = ExtensionManager(self)

        self._setup_ui()
        self._warn_if_no_iverilog()
        self._refresh_icons()
        self.ext_manager.discover_and_load_all()

        QApplication.instance().installEventFilter(self)

    # ---------------- UI ----------------

    def _setup_ui(self):

        self._setup_menu_bar()
        self._setup_editor()
        self._setup_toolbar()
        self._setup_activity_bar()
        self._setup_file_explorer()
        self._setup_connections()
        self._setup_templates()
        self._setup_hierarchy()
        self._setup_git()
        self._setup_terminal()
        self._setup_debug_dock()
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

        tools_menu = menu.addMenu("Tools")
        tools_menu.addAction(self.ide_actions.gen_tb)
        tools_menu.addAction(self.ide_actions.synthesize)
        tools_menu.addAction(self.ide_actions.show_schematic)
        tools_menu.addAction(self.ide_actions.place_and_route)

        view_menu = menu.addMenu("View")
        view_menu.addAction(self.ide_actions.toggle_terminal)
        view_menu.addAction(self.ide_actions.toggle_explorer)

        view_menu.addAction(self.ide_actions.view_waves)

        view_menu.addSeparator()
        view_menu.addAction(self.ide_actions.toggle_theme)

        tools_menu.addSeparator()
        settings_action = tools_menu.addAction("Settings...")
        settings_action.setShortcut(QKeySequence("Ctrl+,"))
        settings_action.triggered.connect(self._show_settings)

        help_menu = menu.addMenu("Help")
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self._show_about)

    # ---------------- EDITOR ----------------

    def _setup_editor(self):

        self.editor_tabs = EditorTabs(hover_db=self.hover_db)
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

        self.signal_dock.hide()
        self.template_dock.hide()
        self.file_explorer_dock.hide()
        self.hierarchy_dock.hide()
        self.git_dock.hide()

        if panel == "explorer":
            self.file_explorer_dock.show()
            self.file_explorer_dock.raise_()
        elif panel == "templates":
            self.template_dock.show()
            self.template_dock.raise_()
        elif panel == "hierarchy":
            self.hierarchy_dock.show()
            self.hierarchy_dock.raise_()
        elif panel == "git":
            self.git_dock.show()
            self.git_dock.raise_()
        else:
            self.signal_dock.show()
            self.signal_dock.raise_()

    # ---------------- FILE EXPLORER ----------------

    def _setup_file_explorer(self):

        self.file_explorer_dock = FileExplorerDock(self)

        self.addDockWidget(
            Qt.DockWidgetArea.LeftDockWidgetArea,
            self.file_explorer_dock
        )

        explorer = self.file_explorer_dock.explorer
        explorer.file_open_requested.connect(self.open_project_file)
        explorer.compile_requested.connect(self.compile_file)
        explorer.run_requested.connect(self.run_file)
        explorer.wave_requested.connect(self.open_wave_file)
        explorer.gen_tb_requested.connect(self.generate_testbench)
        explorer.synthesize_requested.connect(self.synthesize_file)
        explorer.show_schematic_requested.connect(self._on_show_schematic_from_explorer)
        explorer.pnr_requested.connect(self._on_pnr_from_explorer)

    # ---------------- CONNECTIONS ----------------

    def _setup_connections(self):

        self.signal_dock = SignalDock(self)

        self.addDockWidget(
            Qt.DockWidgetArea.LeftDockWidgetArea,
            self.signal_dock
        )

        self.signal_dock.hide()

    # ---------------- TEMPLATES ----------------

    def _setup_templates(self):

        self.template_dock = TemplateDock(self)

        self.addDockWidget(
            Qt.DockWidgetArea.LeftDockWidgetArea,
            self.template_dock
        )

        self.template_dock.new_file_requested.connect(self._on_template_new_file)
        self.template_dock.hide()

    def _on_template_new_file(self, filename, code):
        self.editor_tabs.new_file(content=code, suggested_name=filename)

    # ---------------- HIERARCHY ----------------

    def _setup_hierarchy(self):

        self.hierarchy_dock = HierarchyDock(self)

        self.addDockWidget(
            Qt.DockWidgetArea.LeftDockWidgetArea,
            self.hierarchy_dock
        )

        self.hierarchy_dock.hide()

    # ---------------- GIT ----------------

    def _setup_git(self):

        self.git_dock = GitDock(self)

        self.addDockWidget(
            Qt.DockWidgetArea.LeftDockWidgetArea,
            self.git_dock
        )

        self.git_dock.hide()

    # ---------------- DEBUG DOCK ----------------

    def _setup_debug_dock(self):

        self.debug_dock = DebugDock(self)

        self.addDockWidget(
            Qt.DockWidgetArea.LeftDockWidgetArea,
            self.debug_dock
        )

        self.debug_dock.hide()

    # ---------------- TERMINAL ----------------

    def _setup_terminal(self):

        self.bottom_panel = BottomPanel(self)
        self.addDockWidget(
            Qt.DockWidgetArea.BottomDockWidgetArea,
            self.bottom_panel
        )
        self.bottom_panel.error_clicked.connect(self._on_error_clicked)

    # ---------------- STATUS BAR ----------------

    def _setup_status_bar(self):

        self.status = IDEStatusBar()
        self.setStatusBar(self.status)

    # ---------------- TAB CHANGE ----------------

    def _on_tab_changed(self, index):

        tab = self.editor_tabs.current_tab()
        if tab and tab.path:
            self.signal_dock.update_from_file(tab.path)
            self.hierarchy_dock.update_from_file(tab.path)
        else:
            self.signal_dock.update_from_file(None)
            self.hierarchy_dock.update_from_file(None)

    def _on_error_clicked(self, filepath, lineno):
        filepath = filepath.replace("/", "\\")
        if not os.path.isabs(filepath):
            filepath = os.path.join(self.project.root_path or "", filepath)
        filepath = os.path.abspath(filepath)

        # Try case-insensitive tab match first (avoids duplicate on Windows)
        for p, t in self.editor_tabs.tabs.items():
            if os.path.abspath(p).lower() == filepath.lower():
                self.editor_tabs.setCurrentWidget(t.editor)
                t.editor.set_error_lines([lineno - 1])
                return

        # Not found -> open file normally
        self.editor_tabs.open_file(filepath)
        tab = self.editor_tabs.current_tab()
        if tab:
            tab.editor.set_error_lines([lineno - 1])

    # ---------------- FILE CONTEXT ----------------

    def _refresh_build_context(self, filepath=None, initial=False):

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

        self.toolbar.populate(initial=initial)
        self.signal_dock.update_from_file(filepath)
        self.hierarchy_dock.update_from_file(filepath)

    def _default_dialog_dir(self):
        if self.project and self.project.is_loaded():
            return self.project.root_path
        tab = self.editor_tabs.current_tab()
        if tab and tab.path:
            return os.path.dirname(tab.path)
        return ""

    # ---------------- ACTIONS ----------------

    def open_file(self):

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            self._default_dialog_dir(),
            "HDL Files (*.vhd *.v *.sv);;All Files (*)"
        )

        if not path:
            return

        self.editor_tabs.open_file(path)
        self._refresh_build_context(path, initial=True)
        self.bottom_panel.append_history(f"Opened file: {os.path.basename(path)}")

    def open_project_file(self, path):

        self.editor_tabs.open_file(path)
        self._refresh_build_context(path, initial=True)
        self.bottom_panel.append_history(f"Opened file: {os.path.basename(path)}")

    def _parse_and_mark_errors(self, raw_output):
        errors_by_file = {}
        # Greedy (.+) to handle Windows paths with drive letters
        pat = re.compile(r'^(.+):(\d+):\s*(error|warning|syntax)\s*:\s*(.*)', re.IGNORECASE)
        for line in raw_output.split("\n"):
            m = pat.match(line)
            if m:
                fpath = m.group(1).strip()
                try:
                    lineno = int(m.group(2))
                except ValueError:
                    continue
                if not os.path.isabs(fpath):
                    fpath = os.path.abspath(os.path.join(self.project.root_path or "", fpath))
                else:
                    fpath = os.path.normpath(fpath)
                if fpath not in errors_by_file:
                    errors_by_file[fpath] = set()
                errors_by_file[fpath].add(lineno - 1)
        for fpath, lines in errors_by_file.items():
            tab = self.editor_tabs.tabs.get(fpath)
            if tab:
                try:
                    tab.editor.set_error_lines(sorted(lines))
                except Exception:
                    pass

    def compile_file(self, path):
        self._ensure_files_saved()
        self._refresh_build_context(path)

        bs = self.build_system
        base = os.path.splitext(os.path.basename(path))[0]
        if bs.simulator == bs.SIM_VERILATOR:
            vvp_path, _ = QFileDialog.getSaveFileName(
                self, f"Compile {os.path.basename(path)} with Verilator",
                os.path.join(self._default_dialog_dir(), "build", f"{base}_vlsim"),
                "All Files (*)"
            )
            if not vvp_path:
                return
        else:
            vvp_path, _ = QFileDialog.getSaveFileName(
                self, f"Compile {os.path.basename(path)}",
                os.path.join(self._default_dialog_dir(), "build", f"{base}.vvp"),
                "VVP files (*.vvp);;All Files (*)"
            )
            if not vvp_path:
                return

        self.status.showMessage("Compiling...")
        self.bottom_panel.clear_console()
        self.bottom_panel.tabs.setCurrentIndex(0)
        self.bottom_panel.write_header(f"COMPILING: {os.path.basename(path)}")

        raw_buf = []

        def write(text):
            raw_buf.append(text)
            self.bottom_panel.write_raw(text)

        ok = bs.compile(write, output_path=vvp_path)
        self.bottom_panel.append_history(f"Compiled {os.path.basename(path)}")
        if ok:
            self.bottom_panel.write_ok("Compilation successful")
            self.status.showMessage("Compilation successful")
        else:
            self.bottom_panel.write_error("Compilation failed")
            self.status.showMessage("Compilation failed")

    def run_file(self, path):
        self._ensure_files_saved()
        self._refresh_build_context()

        bs = self.build_system
        if bs.simulator == bs.SIM_VERILATOR:
            sim_path = None
        else:
            sim_path = path

        vcd_path, _ = QFileDialog.getSaveFileName(
            self, f"Run {os.path.basename(path)}",
            os.path.join(self._default_dialog_dir(), "waves.vcd"),
            "VCD files (*.vcd);;FST files (*.fst);;All Files (*)"
        )
        if not vcd_path:
            return

        self.status.showMessage("Running...")
        self.bottom_panel.write_header(f"RUNNING: {os.path.basename(path)}")
        self.bottom_panel.tabs.setCurrentIndex(0)

        write = self.bottom_panel.write_raw

        ok = bs.run(write, sim_path=sim_path)
        self.bottom_panel.append_history(f"Ran {os.path.basename(path)}")

        if ok:
            generated = bs.last_vcd_path
            if generated and os.path.isfile(generated):
                os.makedirs(os.path.dirname(vcd_path), exist_ok=True)
                try:
                    if os.path.normpath(generated) != os.path.normpath(vcd_path):
                        os.replace(generated, vcd_path)
                    bs.last_vcd_path = vcd_path
                    write(f"\n>> Waveform saved as: {os.path.basename(vcd_path)}\n")
                    write(f"   Press F7 to open in GTKWave\n")
                except OSError as e:
                    write(f"\n>> Could not rename waveform: {e}\n")

        self.status.showMessage("Simulation finished" if ok else "Simulation failed")

    def open_wave_file(self, path):
        if not self.wave_viewer.available:
            self.status.showMessage("GTKWave not found — check tools/gtkwave/bin/gtkwave.exe")
            return

        ok = self.wave_viewer.open(path)
        if ok:
            self.status.showMessage(f"GTKWave: {os.path.basename(path)}")
            self.bottom_panel.append_history(f"Opened waveform: {os.path.basename(path)}")
        else:
            self.status.showMessage("Failed to launch GTKWave")

    def save_current_file(self):

        tab = self.editor_tabs.current_tab()

        if not tab:
            return

        if not tab.path:
            self.save_as_file()
            return

        tab.save()
        if tab.path and self.hover_db:
            self.hover_db.add_file(tab.path)
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
            self._default_dialog_dir(),
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

        self._index_project_files()
        self._refresh_build_context(initial=True)
        self.status.showMessage(f"Project loaded: {self.project.name}")

    def _index_project_files(self):
        self.hover_db.clear()
        if not self.project or not self.project.is_loaded():
            return
        import glob
        root = self.project.root_path
        for ext in ("*.v", "*.sv", "*.vhd", "*.vhdl"):
            for f in glob.glob(os.path.join(root, "**", ext), recursive=True):
                self.hover_db.add_file(f)
        self.hierarchy_dock.update_from_project(self.project)
        self.git_dock.set_root(root)

    def _warn_if_no_iverilog(self):

        msgs = []
        if not self.build_system.iverilog_available():
            msgs.append("Icarus Verilog not found in tools/iverilog/")
        if not self.build_system.verilator_available():
            msgs.append("Verilator not found on PATH")
        if msgs:
            self.status.showMessage(" — ".join(msgs))

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
            self.ext_manager.unload_all()
            event.accept()
            return

        if clicked == save_btn:

            for tab in dirty_tabs:
                tab.save()

        self.ext_manager.unload_all()
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

        bs = self.build_system
        if bs.simulator == bs.SIM_VERILATOR:
            path, _ = QFileDialog.getSaveFileName(
                self, "Save Verilator simulation as",
                os.path.join(self._default_dialog_dir(), "build", "simulation_vlsim"),
                "All Files (*)"
            )
            if not path:
                return
        else:
            path, _ = QFileDialog.getSaveFileName(
                self, "Save compiled simulation as",
                os.path.join(self._default_dialog_dir(), "build", "simulation.vvp"),
                "VVP files (*.vvp);;All Files (*)"
            )
            if not path:
                return

        self.status.showMessage("Compiling...")
        self.bottom_panel.clear_console()
        self.bottom_panel.tabs.setCurrentIndex(0)
        self.bottom_panel.write_header("COMPILING PROJECT")

        raw_buf = []

        def write(text):
            raw_buf.append(text)
            self.bottom_panel.write_raw(text)

        ok = bs.compile(write, output_path=path)
        if ok:
            self.bottom_panel.write_ok(
                f"Compilation successful — {os.path.basename(path)} generated"
            )
            self.status.showMessage("Compilation successful")
        else:
            self.bottom_panel.write_error(
                f"Compilation failed — check errors above for details"
            )
            self.status.showMessage("Compilation failed")
        self.bottom_panel.append_history(
            f"Compile: {'OK' if ok else 'FAILED'} ({os.path.basename(path)})"
        )

    def run_project(self):

        self._ensure_files_saved()
        self._refresh_build_context()

        bs = self.build_system
        if bs.simulator == bs.SIM_VERILATOR:
            sim_path = None
        else:
            sim_path, _ = QFileDialog.getOpenFileName(
                self, "Select simulation to run",
                os.path.join(self._default_dialog_dir(), "build"),
                "VVP files (*.vvp);;All Files (*)"
            )
            if not sim_path:
                return

        vcd_path, _ = QFileDialog.getSaveFileName(
            self, "Save waveform as",
            os.path.join(self._default_dialog_dir(), "waves.vcd"),
            "VCD files (*.vcd);;FST files (*.fst);;All Files (*)"
        )
        if not vcd_path:
            return

        self.status.showMessage("Running...")
        self.bottom_panel.write_header("RUNNING SIMULATION")
        self.bottom_panel.tabs.setCurrentIndex(0)

        write = self.bottom_panel.write_raw

        ok = bs.run(write, sim_path=sim_path)
        sim_name = os.path.basename(sim_path) if sim_path else "vvp"

        if ok:
            generated = bs.last_vcd_path
            if generated and os.path.isfile(generated):
                os.makedirs(os.path.dirname(vcd_path), exist_ok=True)
                try:
                    if os.path.normpath(generated) != os.path.normpath(vcd_path):
                        os.replace(generated, vcd_path)
                    bs.last_vcd_path = vcd_path
                    write(f"\n>> Waveform saved as: {os.path.basename(vcd_path)}\n")
                    write(f"   Press F7 to open in GTKWave\n")
                except OSError as e:
                    write(f"\n>> Could not rename waveform: {e}\n")

        if ok:
            self.bottom_panel.write_ok(
                f"Simulation completed — VCD saved to {os.path.basename(vcd_path)}"
            )
        else:
            self.bottom_panel.write_error(
                f"Simulation failed — check errors above for details"
            )
        self.bottom_panel.append_history(
            f"Run: {'OK' if ok else 'FAILED'} (VCD: {os.path.basename(vcd_path)})"
        )
        self.status.showMessage(
            "Simulation finished" if ok else "Simulation failed"
        )

    def debug_project(self):

        try:
            self._debug_project_impl()
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            self.bottom_panel.clear_console()
            self.bottom_panel.tabs.setCurrentIndex(0)
            self.bottom_panel.write_error(f"Debug error: {e}")
            for line in tb.split("\n"):
                self.bottom_panel.write_raw(line + "\n")
            self.status.showMessage("Debug: error — see console")
            self.bottom_panel.append_history("Debug: error")

    def _debug_project_impl(self):

        from ui.debug_dialog import DebugDialog
        bs = self.build_system
        default_sim_name = "simulation_vlsim" if bs.simulator == bs.SIM_VERILATOR else "simulation.vvp"
        default_sim = os.path.join(self._default_dialog_dir(), "build", default_sim_name)
        dlg = DebugDialog(
            default_dir=self._default_dialog_dir(),
            default_sim_path=default_sim,
            parent=self
        )
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        mode = dlg.mode()
        vcd_out = dlg.vcd_path()
        sim_out = dlg.sim_path()

        self._ensure_files_saved()
        self._refresh_build_context()

        bs = self.build_system
        root = bs.root_dir or self._default_dialog_dir()
        build_dir = os.path.dirname(sim_out) or os.path.join(root, "build")
        os.makedirs(build_dir, exist_ok=True)

        self.status.showMessage("Debug: Compiling...")
        self.bottom_panel.clear_console()
        self.bottom_panel.tabs.setCurrentIndex(0)
        self.bottom_panel.write_header(f"DEBUG ({mode.upper()}) — COMPILE")

        def write(text):
            self.bottom_panel.write_raw(text)

        ok = bs.compile(write, output_path=sim_out)
        if not ok:
            self.bottom_panel.write_error(
                "Compilation failed — aborting debug. Check errors above."
            )
            self.bottom_panel.append_history("Debug: compile FAILED")
            self.status.showMessage("Debug: compilation failed")
            return

        self.bottom_panel.write_ok(
            f"Compilation OK ({os.path.basename(sim_out)}) — starting simulation"
        )
        self.bottom_panel.write_header("DEBUG — RUN")

        ok = bs.run(write, sim_path=None if bs.simulator == bs.SIM_VERILATOR else sim_out)
        self.bottom_panel.append_history("Debug: ran simulation")

        if not ok:
            self.bottom_panel.write_error(
                "Simulation failed — check errors above for details"
            )
            self.status.showMessage("Debug: simulation failed")
            self.bottom_panel.append_history("Debug finished (FAILED)")
            return

        self.bottom_panel.write_ok("Simulation completed successfully")

        generated = bs.last_vcd_path
        if generated and os.path.isfile(generated):
            try:
                if os.path.normpath(generated) != os.path.normpath(vcd_out):
                    os.replace(generated, vcd_out)
                bs.last_vcd_path = vcd_out
                write(f"\n>> Waveform saved: {vcd_out}\n")
            except OSError as e:
                write(f"\n>> Could not rename waveform: {e}\n")

        if mode == DebugDialog.MODE_STEP:
            self._start_step_debug(vcd_out, dlg.step_size_ns(), dlg.max_time_ns())
        else:
            self._open_gtkwave(vcd_out)

        self.bottom_panel.append_history("Debug finished")

    def _open_gtkwave(self, vcd_path):
        if not vcd_path or not os.path.isfile(vcd_path):
            self.status.showMessage("No waveform file to open")
            return
        if self.wave_viewer.available:
            self.wave_viewer.open(vcd_path)
            self.bottom_panel.write_ok("GTKWave launched")
            self.status.showMessage("Debug: GTKWave opened")
        else:
            self.bottom_panel.write_info("GTKWave not available — press F7 to view waves manually")
            self.status.showMessage("Debug: done (no GTKWave)")

    def _start_step_debug(self, vcd_path, step_ns, max_time_ns):
        try:
            self._start_step_debug_impl(vcd_path, step_ns, max_time_ns)
        except Exception as e:
            import traceback
            self.bottom_panel.write_error(f"Step debug error: {e}")
            for line in traceback.format_exc().split("\n"):
                self.bottom_panel.write_raw(line + "\n")
            self.status.showMessage("Debug: step init error")

    def _start_step_debug_impl(self, vcd_path, step_ns, max_time_ns):

        from core.vcd_parser import VCDParser
        self._debug_vcd = vcd_path
        self._debug_step_ns = step_ns
        self._debug_parser = VCDParser(vcd_path)
        self._debug_parser.parse()
        self._debug_time_idx = 0
        self._debug_tb_file = self.build_system.testbench_file
        self._debug_tb_delay_lines = []
        self._debug_max_time = max_time_ns

        if self._debug_tb_file and os.path.isfile(self._debug_tb_file):
            self._debug_tb_delay_lines = self._parse_delay_lines(self._debug_tb_file)

        if not self._debug_parser.time_values:
            self.bottom_panel.write_warning("No time points found in VCD — falling back to full mode")
            self._open_gtkwave(vcd_path)
            return

        self.toolbar.set_step_controls_visible(True)
        self.debug_dock.show()
        self.debug_dock.raise_()

        self.bottom_panel.write_ok(f"VCD parsed: {len(self._debug_parser.time_values)} time points")
        self.bottom_panel.write_info(f"Timescale: {self._debug_parser.timescale}")
        self.bottom_panel.write_header("STEP DEBUG — use Step Forward/Back buttons or shortcuts")

        self._open_gtkwave(vcd_path)

        self._step_show_current()

    def _parse_delay_lines(self, tb_path):
        import re
        lines = []
        with open(tb_path, 'r', encoding='utf-8', errors='replace') as f:
            for i, line in enumerate(f.readlines(), 1):
                m = re.findall(r'#(\d+)', line)
                for val in m:
                    lines.append((int(val), i))
        return sorted(lines, key=lambda x: x[0])

    def _step_show_current(self):

        parser = self._debug_parser
        if not parser or not parser.time_values:
            return

        idx = self._debug_time_idx
        if idx < 0:
            idx = 0
            self._debug_time_idx = 0
        if idx >= len(parser.time_values):
            idx = len(parser.time_values) - 1
            self._debug_time_idx = idx

        t = parser.time_values[idx]

        self.bottom_panel.clear_console()
        self.bottom_panel.write_header(f"STEP — t={t} {parser.timescale}  ({idx+1}/{len(parser.time_values)})")
        text = parser.snapshot_text(t, max_signals=30)
        for line in text.split("\n"):
            self.bottom_panel.write_raw(line)

        self.debug_dock.update_from_step(
            parser, t, self._debug_time_idx, len(parser.time_values)
        )

        self.status.showMessage(f"Debug: t={t} {parser.timescale}")

        tb_file = self._debug_tb_file
        if not tb_file or not self._debug_tb_delay_lines:
            return

        closest_line = None
        for delay, lineno in reversed(self._debug_tb_delay_lines):
            if delay <= t:
                closest_line = lineno
                break

        for tab in self.editor_tabs.tabs.values():
            path = getattr(tab, 'path', None) or ''
            if os.path.normpath(path) == os.path.normpath(tb_file):
                if closest_line is not None:
                    tab.editor.set_error_lines([closest_line - 1])
                break

    def _step_forward(self):
        try:
            parser = self._debug_parser
            if not parser or not parser.time_values:
                return
            if self._debug_time_idx < len(parser.time_values) - 1:
                self._debug_time_idx += 1
            self._step_show_current()
        except Exception as e:
            self.bottom_panel.write_error(f"Step forward error: {e}")

    def _step_back(self):
        try:
            parser = self._debug_parser
            if not parser or not parser.time_values:
                return
            if self._debug_time_idx > 0:
                self._debug_time_idx -= 1
            self._step_show_current()
        except Exception as e:
            self.bottom_panel.write_error(f"Step back error: {e}")

    def _stop_debug(self):
        try:
            self._debug_parser = None
            self._debug_vcd = None
            self._debug_time_idx = 0
            for tab in self.editor_tabs.tabs.values():
                tab.editor.clear_error_markers()
            self.toolbar.set_step_controls_visible(False)
            self.debug_dock.clear_display()
            self.debug_dock.hide()
            self.status.showMessage("Debug stopped")
        except Exception as e:
            self.bottom_panel.write_error(f"Stop debug error: {e}")

    def view_waves(self):

        if not self.wave_viewer.available:
            self.status.showMessage(
                "GTKWave not found — check tools/gtkwave/bin/gtkwave.exe"
            )
            return

        vcd, _ = QFileDialog.getOpenFileName(
            self, "Open waveform",
            self._default_dialog_dir(),
            "Waveform files (*.vcd *.fst *.lxt *.lxt2 *.ghw);;All Files (*)"
        )
        if not vcd:
            return

        ok = self.wave_viewer.open(vcd)
        if ok:
            self.status.showMessage(f"GTKWave: {os.path.basename(vcd)}")
        else:
            self.status.showMessage("Failed to launch GTKWave")

    def _on_wave_error(self, msg):
        self.bottom_panel.clear_console()
        self.bottom_panel.tabs.setCurrentIndex(0)
        self.bottom_panel.write_error(f"GTKWave error:\n{msg}\n")
        self.status.showMessage("GTKWave reported an error — see terminal")

    def toggle_terminal(self):

        visible = self.bottom_panel.isVisible()
        self.bottom_panel.setVisible(not visible)

    def generate_testbench(self, path=None):

        if path is None:
            # Called from Tools menu — show file dialog
            path, _ = QFileDialog.getOpenFileName(
                self, "Select HDL file for testbench",
                self._default_dialog_dir(),
                "HDL Files (*.v *.sv *.vhd *.vhdl);;All Files (*)"
            )
            if not path:
                return

        if not os.path.isfile(path):
            self.status.showMessage("No HDL file selected")
            return

        from core.testbench_generator import generate_testbench
        try:
            result = generate_testbench(path)
            if result is None:
                self.status.showMessage("Could not parse module/entity from file")
                return
            dst_file, code = result
            self.editor_tabs.new_file(content=code, suggested_name=dst_file)
            self.status.showMessage(f"Generated {dst_file}")
        except Exception as e:
            self.status.showMessage(f"Testbench generation failed: {e}")

    def synthesize_file(self, path=None):
        if path is None:
            path, _ = QFileDialog.getOpenFileName(
                self, "Select HDL file to synthesize",
                self._default_dialog_dir(),
                "HDL Files (*.v *.sv *.vhd *.vhdl);;All Files (*)"
            )
            if not path:
                return

        if not os.path.isfile(path):
            self.status.showMessage("No HDL file selected")
            return

        if not self.build_system.yosys_available():
            self.status.showMessage("yowasp-yosys not installed — run: pip install yowasp-yosys")
            return

        out_path, _ = QFileDialog.getSaveFileName(
            self, "Save synthesis output",
            os.path.join(self._default_dialog_dir(), os.path.splitext(os.path.basename(path))[0] + ".blif"),
            "BLIF (*.blif);;Verilog (*.v);;EDIF (*.edif);;JSON (*.json);;All Files (*)"
        )

        if not out_path:
            return

        self.bottom_panel.clear_console()
        self.bottom_panel.tabs.setCurrentIndex(0)
        self.bottom_panel.write_header(f"SYNTHESIS: {os.path.basename(path)}")

        write = self.bottom_panel.write_raw

        self.status.showMessage("Synthesizing...")
        try:
            ok = self.build_system.synthesize(write, path, output_path=out_path)
            if ok:
                self.bottom_panel.write_ok("Synthesis complete")
                self.status.showMessage("Synthesis complete")
                self.bottom_panel.append_history(f"Synthesized {os.path.basename(path)}")
                if out_path and os.path.isfile(out_path):
                    out_lower = out_path.lower()
                    if out_lower.endswith(".json"):
                        self._last_synthesis_json = out_path
                        self.bottom_panel.write_raw("Use Place & Route (Ctrl+Shift+P) to run PnR on this design.\n")
                    else:
                        self._last_synthesis_blif = out_path
                        self.bottom_panel.write_raw("Opening gate-level schematic...\n")
                        self._show_schematic(out_path)
            else:
                self.bottom_panel.write_error("Synthesis failed")
                self.status.showMessage("Synthesis failed")
        except Exception as e:
            self.bottom_panel.write_error(f"Synthesis error: {e}")
            self.status.showMessage(f"Synthesis error: {e}")

    def _show_schematic(self, blif_path):
        from core.schematic_viewer import show_schematic
        try:
            dlg = show_schematic(blif_path, self)
            if dlg:
                dlg.exec()
            else:
                self.status.showMessage("Could not generate schematic")
        except Exception as e:
            self.status.showMessage(f"Schematic error: {e}")

    def _on_show_schematic_from_explorer(self, path):
        if not self.build_system.yosys_available():
            self.status.showMessage("yowasp-yosys not installed — run: pip install yowasp-yosys")
            return
        from core.schematic_viewer import show_schematic_from_hdl, show_schematic
        try:
            is_blif = path.lower().endswith(".blif")
            dlg = show_schematic(path, self) if is_blif else show_schematic_from_hdl(path, self)
            if dlg:
                dlg.exec()
                self.status.showMessage(f"Schematic: {os.path.basename(path)}")
            else:
                self.status.showMessage("Could not generate schematic")
        except Exception as e:
            self.status.showMessage(f"Schematic error: {e}")

    def show_schematic_current_file(self):
        if not self.build_system.yosys_available():
            self.status.showMessage("yowasp-yosys not installed — run: pip install yowasp-yosys")
            return

        from core.schematic_viewer import show_schematic_from_hdl, show_schematic

        # Priority: last synthesis BLIF → current editor file → file dialog
        target = None
        label = None

        if self._last_synthesis_blif and os.path.isfile(self._last_synthesis_blif):
            target = self._last_synthesis_blif
            label = "last synthesis"
        else:
            tab = self.editor_tabs.current_tab()
            if tab and tab.path:
                target = tab.path
                label = os.path.basename(tab.path)

        if not target:
            target, _ = QFileDialog.getOpenFileName(
                self, "Select HDL or BLIF file for schematic",
                self._default_dialog_dir(),
                "HDL/BLIF Files (*.v *.sv *.vhd *.vhdl *.blif);;All Files (*)"
            )
            if not target:
                return
            label = os.path.basename(target)

        is_blif = target.lower().endswith(".blif")
        try:
            if is_blif:
                dlg = show_schematic(target, self)
            else:
                dlg = show_schematic_from_hdl(target, self)
            if dlg:
                dlg.exec()
                self.status.showMessage(f"Schematic: {label}")
            else:
                self.status.showMessage("Could not generate schematic")
        except Exception as e:
            self.status.showMessage(f"Schematic error: {e}")

    def place_and_route_file(self, path=None):
        if path is None:
            if self._last_synthesis_json and os.path.isfile(self._last_synthesis_json):
                path = self._last_synthesis_json
            else:
                path, _ = QFileDialog.getOpenFileName(
                    self, "Select synthesized JSON for PnR",
                    self._default_dialog_dir(),
                    "JSON Files (*.json);;All Files (*)"
                )
                if not path:
                    return

        if not os.path.isfile(path):
            self.status.showMessage("No JSON file selected")
            return

        from core.pnr_system import run_pnr

        default_asc = os.path.splitext(os.path.basename(path))[0] + ".asc"
        asc_path, _ = QFileDialog.getSaveFileName(
            self, "Save PnR output",
            os.path.join(self._default_dialog_dir(), default_asc),
            "ASC (*.asc);;All Files (*)"
        )
        if not asc_path:
            return

        self.bottom_panel.clear_console()
        self.bottom_panel.tabs.setCurrentIndex(0)
        self.bottom_panel.write_header(f"PLACE & ROUTE: {os.path.basename(path)}")

        write = self.bottom_panel.write_raw
        self.status.showMessage("Running Place & Route...")

        try:
            asc_path_result, report_info = run_pnr(
                write, path, asc_path=asc_path or None,
                device="hx1k", package=None, frequency=12
            )
            if asc_path_result:
                self.bottom_panel.write_ok("Place & Route complete")
                self.status.showMessage("Place & Route complete")
                self.bottom_panel.append_history(f"Place & Route: {os.path.basename(path)}")
                if report_info:
                    self._show_pnr_report(report_info)
            else:
                self.bottom_panel.write_error("Place & Route failed")
                self.status.showMessage("Place & Route failed")
        except Exception as e:
            self.bottom_panel.write_error(f"PnR error: {e}")
            self.status.showMessage(f"PnR error: {e}")

    def _show_pnr_report(self, report_info):
        from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTableWidget,
                                     QTableWidgetItem, QHeaderView,
                                     QDialogButtonBox, QLabel)
        from PyQt6.QtGui import QFont

        dlg = QDialog(self)
        dlg.setWindowTitle("PnR Report")
        dlg.resize(520, 400)

        layout = QVBoxLayout(dlg)

        if not report_info:
            layout.addWidget(QLabel("No report data available."))
            btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
            btn_box.accepted.connect(dlg.accept)
            layout.addWidget(btn_box)
            dlg.exec()
            return

        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Metric", "Value"])
        table.horizontalHeader().setStretchLastSection(True)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.setFont(QFont("Consolas", 10))

        rows = []
        for key, label in [
            ("device", "Device"),
            ("worst_slack", "Worst Slack"),
            ("best_slack", "Best Slack"),
            ("fmax", "Fmax (MHz)"),
            ("total_negative_slack", "TNS"),
            ("logic_delay_ns", "Logic delay (ns)"),
            ("routing_delay_ns", "Routing delay (ns)"),
            ("total_delay_ns", "Total delay (ns)"),
            ("luts_used", "LCs used"),
            ("luts_total", "LCs total"),
            ("bram_used", "BRAM used"),
            ("bram_total", "BRAM total"),
            ("io_used", "IO used"),
            ("io_total", "IO total"),
            ("pll_used", "PLL used"),
            ("pll_total", "PLL total"),
            ("global_buffers_used", "Global buffers used"),
            ("global_buffers_total", "Global buffers total"),
            ("warmboot_used", "Warmboot used"),
            ("warmboot_total", "Warmboot total"),
            ("luts", "LUTs"),
            ("ffs", "FFs"),
            ("carry", "Carry"),
            ("bram", "BRAM blocks"),
            ("io", "IO pins"),
            ("pll", "PLLs"),
            ("warmboot", "Warmboot"),
            ("note", "Note"),
        ]:
            v = report_info.get(key)
            if v is not None:
                rows.append((label, str(v)))

        table.setRowCount(len(rows))
        for i, (label, val) in enumerate(rows):
            table.setItem(i, 0, QTableWidgetItem(label))
            table.setItem(i, 1, QTableWidgetItem(val))

        table.resizeColumnsToContents()
        layout.addWidget(table)

        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        btn_box.accepted.connect(dlg.accept)
        layout.addWidget(btn_box)

        dlg.exec()

    def _on_pnr_from_explorer(self, path):
        self.place_and_route_file(path)

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
            "hierarchy": self.activity_bar.hierarchy_btn,
            "connections": self.activity_bar.connections_btn,
            "templates": self.activity_bar.templates_btn,
            "git": self.activity_bar.git_btn,
            "settings": self.activity_bar.settings_btn,
            "help": self.activity_bar.about_btn,
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
            "debug": self.ide_actions.debug,
            "backward": self.ide_actions.step_back,
            "forward": self.ide_actions.step_forward,
            "stop": self.ide_actions.stop_debug,
            "synthesize": self.ide_actions.synthesize,
            "pnr": self.ide_actions.place_and_route,
            "wave": self.ide_actions.view_waves,
            "darklight": self.ide_actions.toggle_theme,
            "terminal": self.ide_actions.toggle_terminal,
        }
        for name, action in toolbar_icons.items():
            action.setIcon(QIcon(TM.icon(name)))

        for i in range(self.editor_tabs.count()):
            self.editor_tabs.setTabIcon(i, QIcon(TM.icon("file")))

    def _show_settings(self):
        from ui.settings_dialog import SettingsDialog
        dlg = SettingsDialog(self)
        dlg.exec()

    def toggle_theme(self):

        new_theme = "light" if ThemeManager.current_theme == "dark" else "dark"
        ThemeManager.set_theme(new_theme)
        colors = ThemeManager.colors()

        self.setStyleSheet(build_stylesheet())

        self.activity_bar.apply_theme(colors)
        self.toolbar.apply_theme(colors)
        self.bottom_panel.apply_theme(colors)
        self.signal_dock.apply_theme(colors)
        self.template_dock.apply_theme(colors)
        self.hierarchy_dock.apply_theme(colors)
        self.git_dock.apply_theme(colors)
        self.debug_dock.apply_theme(colors)

        self.editor_tabs._find_bar.apply_theme(colors)
        self.editor_tabs._style_tab_buttons()
        for tab in self.editor_tabs.tabs.values():
            tab.editor.apply_theme_from_colors(colors)

        self._refresh_icons()

        self.status.showMessage(f"Switched to {new_theme} theme")

    def apply_settings(self, settings):
        theme = settings.get("theme", ThemeManager.current_theme)
        if theme != ThemeManager.current_theme:
            ThemeManager.set_theme(theme)
            colors = ThemeManager.colors()
            self.setStyleSheet(build_stylesheet())
            self.activity_bar.apply_theme(colors)
            self.toolbar.apply_theme(colors)
            self.bottom_panel.apply_theme(colors)
            self.signal_dock.apply_theme(colors)
            self.template_dock.apply_theme(colors)
            self.hierarchy_dock.apply_theme(colors)
            self.git_dock.apply_theme(colors)
            self.debug_dock.apply_theme(colors)
            self.editor_tabs._find_bar.apply_theme(colors)
            self.editor_tabs._style_tab_buttons()
            for tab in self.editor_tabs.tabs.values():
                tab.editor.apply_theme_from_colors(colors)
            self._refresh_icons()

        family = settings.get("font_family", "Consolas")
        size = settings.get("font_size", 10)
        font = QFont(family, size)
        for tab in self.editor_tabs.tabs.values():
            tab.editor.setEditorFont(font)
            tab.editor.set_editor_tab_width(settings.get("tab_width", 4))
            tab.editor.set_editor_word_wrap(settings.get("word_wrap", False))

        self.status.showMessage("Settings applied", 3000)

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

        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox
        dlg = QDialog(self)
        dlg.setWindowTitle("About HDLStudio")
        dlg.resize(460, 380)
        layout = QVBoxLayout(dlg)

        text = (
            "<h2>HDLStudio</h2>"
            "<p><b>Version:</b> 0.1.0</p>"
            "<p><b>Author:</b> José Pedro Granado Olmo (<a href='https://github.com/josped385'>@josped385</a>)</p>"
            "<p><b>Docs:</b> <a href='https://josped385.github.io/HDLStudio/'>josped385.github.io/HDLStudio</a></p>"
            "<p><b>License:</b> GPL v3</p>"
            "<hr>"
            "<p>A modern IDE for digital hardware design.</p>"
            "<ul>"
            "<li>Verilog, SystemVerilog &amp; VHDL editing with syntax highlighting</li>"
            "<li>Icarus Verilog &amp; Verilator (WSL) compilation &amp; simulation</li>"
            "<li>GTKWave waveform viewer integration</li>"
            "<li>Yosys HDL synthesis</li>"
            "<li>nextpnr-ice40 place &amp; route</li>"
            "<li>Graphviz schematic viewer</li>"
            "<li>Automatic testbench generation</li>"
            "<li>Extensible via plugins</li>"
            "</ul>"
            "<hr>"
            "<p style='font-size:9pt; color:#888;'>"
            "Powered by PyQt6, QScintilla, Yosys, nextpnr, "
            "Icarus Verilog, GTKWave &amp; Graphviz.</p>"
        )
        label = QLabel(text)
        label.setWordWrap(True)
        label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(label)

        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        btn_box.accepted.connect(dlg.accept)
        layout.addWidget(btn_box)

        dlg.exec()