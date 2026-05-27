from PyQt6.QtGui import QAction, QIcon


class IDEActions:

    def __init__(self, main_window):

        self.main = main_window

        # ---------------- FILE ----------------

        self.new_file = QAction(QIcon("assets/icons/new.svg"), "New File", main_window)
        self.open_file = QAction(QIcon("assets/icons/open.svg"), "Open File", main_window)
        self.open_project = QAction(QIcon("assets/icons/open_folder.svg"), "Open Project", main_window)

        self.save = QAction(QIcon("assets/icons/save.svg"), "Save", main_window)
        self.save_as = QAction(QIcon("assets/icons/save_as.svg"), "Save As", main_window)

        # ---------------- BUILD ----------------

        self.compile = QAction(QIcon("assets/icons/compile.svg"), "Compile", main_window)
        self.run = QAction(QIcon("assets/icons/play.svg"), "Run", main_window)

        # ---------------- VIEW ----------------

        self.toggle_terminal = QAction("Toggle Terminal", main_window)
        self.toggle_explorer = QAction("Toggle Explorer", main_window)

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