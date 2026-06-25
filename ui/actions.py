import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon, QKeySequence
from themes.theme_manager import ThemeManager


class IDEActions:

    def __init__(self, main_window):

        self.main = main_window
        self._custom_actions = {}

        # ---------------- FILE ----------------

        self.new_file = QAction(QIcon(ThemeManager.icon("new")), "New File", main_window)
        self.new_file.setShortcut(QKeySequence("Ctrl+N"))

        self.open_file = QAction(QIcon(ThemeManager.icon("open")), "Open File", main_window)
        self.open_file.setShortcut(QKeySequence("Ctrl+O"))

        self.open_project = QAction(QIcon(ThemeManager.icon("open_folder")), "Open Project", main_window)
        self.open_project.setShortcut(QKeySequence("Ctrl+Shift+O"))

        self.save = QAction(QIcon(ThemeManager.icon("save")), "Save", main_window)
        self.save.setShortcut(QKeySequence("Ctrl+S"))

        self.save_as = QAction(QIcon(ThemeManager.icon("save_as")), "Save As", main_window)
        self.save_as.setShortcut(QKeySequence("Ctrl+Shift+S"))

        # ---------------- EDIT ----------------
        self.undo = QAction("Undo", main_window)
        self.undo.setShortcut(QKeySequence("Ctrl+Z"))

        self.redo = QAction("Redo", main_window)
        self.redo.setShortcut(QKeySequence("Ctrl+Y"))

        # ---------------- BUILD ----------------

        self.compile = QAction(QIcon(ThemeManager.icon("compile")), "Compile", main_window)
        self.compile.setShortcut(QKeySequence("F5"))

        self.run = QAction(QIcon(ThemeManager.icon("play")), "Run", main_window)
        self.run.setShortcut(QKeySequence("F6"))

        self.debug = QAction(QIcon(ThemeManager.icon("debug")), "Debug", main_window)
        self.debug.setShortcut(QKeySequence("F8"))
        self.debug.setToolTip(
            "Debug (F8)\n"
            "Opens a dialog to configure debug mode:\n"
            "  • Complete — compile, run and open GTKWave\n"
            "  • Step — advance through time points with testbench line highlighting"
        )

        self.step_back = QAction("Step Back", main_window)
        self.step_back.setShortcut(QKeySequence("Ctrl+Shift+Left"))
        self.step_back.setToolTip("Step Back (Ctrl+Shift+Left)\nGo to previous time point")

        self.step_forward = QAction("Step Forward", main_window)
        self.step_forward.setShortcut(QKeySequence("Ctrl+Shift+Right"))
        self.step_forward.setToolTip("Step Forward (Ctrl+Shift+Right)\nGo to next time point")

        self.stop_debug = QAction("Stop Debug", main_window)
        self.stop_debug.setShortcut(QKeySequence("Shift+F5"))
        self.stop_debug.setToolTip("Stop Debug (Shift+F5)\nExit step debug mode and clear highlights")

        # ---------------- VIEW ----------------

        self.toggle_terminal = QAction(QIcon(ThemeManager.icon("terminal")), "Toggle Terminal", main_window)
        self.toggle_terminal.setShortcut(QKeySequence("Ctrl+`"))

        self.toggle_explorer = QAction("Toggle Explorer", main_window)
        self.toggle_explorer.setShortcut(QKeySequence("Ctrl+B"))

        self.view_waves = QAction(QIcon(ThemeManager.icon("wave")), "View Waves", main_window)
        self.view_waves.setShortcut(QKeySequence("F7"))

        # ---------------- TOOLS ----------------
        self.gen_tb = QAction("Generate Testbench", main_window)
        self.gen_tb.setShortcut(QKeySequence("Ctrl+Shift+G"))

        self.synthesize = QAction(QIcon(ThemeManager.icon("synthesize")), "Synthesize", main_window)
        self.synthesize.setShortcut(QKeySequence("Ctrl+Shift+S"))

        self.show_schematic = QAction("Show Schematic", main_window)
        self.show_schematic.setShortcut(QKeySequence("Ctrl+Shift+D"))

        self.formal_verify = QAction("Formal Verification", main_window)
        self.formal_verify.setShortcut(QKeySequence("Ctrl+Shift+F"))

        self.place_and_route = QAction(QIcon(ThemeManager.icon("pnr")), "Place && Route", main_window)
        self.place_and_route.setShortcut(QKeySequence("Ctrl+Shift+P"))

        # ---------------- THEME ----------------
        self.toggle_theme = QAction("Toggle Dark/Light Theme", main_window)
        self.toggle_theme.setShortcut(QKeySequence("Ctrl+Shift+T"))
        self.toggle_theme.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)

        # ---------------- CONNECTIONS ----------------

        self._connect()

    def _connect(self):

        self.new_file.triggered.connect(self.main.new_file)
        self.open_file.triggered.connect(self.main.open_file)
        self.open_project.triggered.connect(self.main.open_folder)

        self.save.triggered.connect(self.main.save_current_file)
        self.save_as.triggered.connect(self.main.save_as_file)

        self.compile.triggered.connect(self.main.compile_project)
        self.run.triggered.connect(self.main.run_project)
        self.debug.triggered.connect(self.main.debug_project)
        self.step_forward.triggered.connect(self.main._step_forward)
        self.step_back.triggered.connect(self.main._step_back)
        self.stop_debug.triggered.connect(self.main._stop_debug)

        self.undo.triggered.connect(self.main._undo)
        self.redo.triggered.connect(self.main._redo)

        self.toggle_terminal.triggered.connect(self.main.toggle_terminal)
        self.toggle_explorer.triggered.connect(self.main.toggle_explorer)
        self.view_waves.triggered.connect(self.main.view_waves)

        self.gen_tb.triggered.connect(lambda checked: self.main.generate_testbench())
        self.synthesize.triggered.connect(lambda checked: self.main.synthesize_file())
        self.show_schematic.triggered.connect(lambda checked: self.main.show_schematic_current_file())
        self.formal_verify.triggered.connect(lambda checked: self.main.formal_verify_file())
        self.place_and_route.triggered.connect(lambda checked: self.main.place_and_route_file())
        self.toggle_theme.triggered.connect(self.main.toggle_theme)

