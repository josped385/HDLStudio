from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon, QKeySequence


class IDEActions:

    def __init__(self, main_window):

        self.main = main_window
        self._custom_actions = {}

        # ---------------- FILE ----------------

        self.new_file = QAction(QIcon("assets/icons/new.svg"), "New File", main_window)
        self.new_file.setShortcut(QKeySequence("Ctrl+N"))

        self.open_file = QAction(QIcon("assets/icons/open.svg"), "Open File", main_window)
        self.open_file.setShortcut(QKeySequence("Ctrl+O"))

        self.open_project = QAction(QIcon("assets/icons/open_folder.svg"), "Open Project", main_window)
        self.open_project.setShortcut(QKeySequence("Ctrl+Shift+O"))

        self.save = QAction(QIcon("assets/icons/save.svg"), "Save", main_window)
        self.save.setShortcut(QKeySequence("Ctrl+S"))

        self.save_as = QAction(QIcon("assets/icons/save_as.svg"), "Save As", main_window)
        self.save_as.setShortcut(QKeySequence("Ctrl+Shift+S"))

        # ---------------- BUILD ----------------

        self.compile = QAction(QIcon("assets/icons/compile.svg"), "Compile", main_window)
        self.compile.setShortcut(QKeySequence("F5"))

        self.run = QAction(QIcon("assets/icons/play.svg"), "Run", main_window)
        self.run.setShortcut(QKeySequence("F6"))

        # ---------------- VIEW ----------------

        self.toggle_terminal = QAction(QIcon("assets/icons/terminal.svg"), "Toggle Terminal", main_window)
        self.toggle_terminal.setShortcut(QKeySequence("Ctrl+`"))

        self.toggle_explorer = QAction("Toggle Explorer", main_window)
        self.toggle_explorer.setShortcut(QKeySequence("Ctrl+B"))

        self.view_waves = QAction(QIcon("assets/icons/wave.svg"), "View Waves", main_window)
        self.view_waves.setShortcut(QKeySequence("F7"))

        # ---------------- TOOLS ----------------
        self.gen_tb = QAction("Generate Testbench", main_window)
        self.gen_tb.setShortcut(QKeySequence("Ctrl+Shift+G"))

        self.synthesize = QAction(QIcon("assets/icons/synthesize.svg"), "Synthesize", main_window)
        self.synthesize.setShortcut(QKeySequence("Ctrl+Shift+S"))

        self.show_schematic = QAction("Show Schematic", main_window)
        self.show_schematic.setShortcut(QKeySequence("Ctrl+Shift+D"))

        self.place_and_route = QAction(QIcon("assets/icons/pnr.svg"), "Place & Route", main_window)
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

        self.toggle_terminal.triggered.connect(self.main.toggle_terminal)
        self.toggle_explorer.triggered.connect(self.main.toggle_explorer)
        self.view_waves.triggered.connect(self.main.view_waves)

        self.gen_tb.triggered.connect(lambda checked: self.main.generate_testbench())
        self.synthesize.triggered.connect(lambda checked: self.main.synthesize_file())
        self.show_schematic.triggered.connect(lambda checked: self.main.show_schematic_current_file())
        self.place_and_route.triggered.connect(lambda checked: self.main.place_and_route_file())
        self.toggle_theme.triggered.connect(self.main.toggle_theme)

