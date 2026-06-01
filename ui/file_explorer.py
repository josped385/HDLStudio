import os

from PyQt6.QtCore import pyqtSignal, Qt, QFile
from PyQt6.QtGui import QFileSystemModel, QGuiApplication, QIcon
from PyQt6.QtWidgets import QTreeView, QMenu, QMessageBox


class FileExplorer(QTreeView):

    file_open_requested = pyqtSignal(str)
    compile_requested = pyqtSignal(str)
    run_requested = pyqtSignal(str)
    wave_requested = pyqtSignal(str)
    gen_tb_requested = pyqtSignal(str)
    synthesize_requested = pyqtSignal(str)
    show_schematic_requested = pyqtSignal(str)

    def __init__(self, root_path="."):
        super().__init__()

        self.model = QFileSystemModel()
        self.model.setRootPath(root_path)

        self.setModel(self.model)
        self.setRootIndex(self.model.index(root_path))

        self.doubleClicked.connect(self._on_double_click)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

        self._cut_source = None

        self.hideColumn(1)
        self.hideColumn(2)
        self.hideColumn(3)

    def _on_double_click(self, index):
        path = self.model.filePath(index)
        self.file_open_requested.emit(path)

    def _file_under_menu(self, pos):
        index = self.indexAt(pos)
        if not index or not index.isValid():
            return None
        path = self.model.filePath(index)
        if os.path.isfile(path):
            return path
        return None

    def _icon(self, name):
        from themes.theme_manager import ThemeManager
        return QIcon(ThemeManager.icon(name))

    def _show_context_menu(self, pos):
        path = self._file_under_menu(pos)
        if not path:
            return

        menu = QMenu(self)
        ext = os.path.splitext(path)[1].lower()

        open_action = menu.addAction(self._icon("file"), "Open")
        show_action = menu.addAction("Show in Explorer")
        menu.addSeparator()
        copy_action = menu.addAction(self._icon("copy"), "Copy")
        cut_action = menu.addAction(self._icon("cut"), "Cut")
        delete_action = menu.addAction(self._icon("delete"), "Delete")
        menu.addSeparator()

        if ext in (".v", ".sv", ".vhd", ".vhdl"):
            compile_action = menu.addAction(self._icon("compile"), "Compile")
            gen_tb_action = menu.addAction("Generate Testbench")
            synth_action = menu.addAction(self._icon("synthesize"), "Synthesize")
            show_sch_action = menu.addAction(self._icon("synthesize"), "Show Schematic")
        elif ext == ".vvp":
            run_action = menu.addAction(self._icon("play"), "Run")
        elif ext in (".vcd", ".fst", ".lxt", ".lxt2", ".ghw"):
            wave_action = menu.addAction(self._icon("wave"), "View Waves")

        chosen = menu.exec(self.viewport().mapToGlobal(pos))

        if chosen == open_action:
            self.file_open_requested.emit(path)
        elif chosen == show_action:
            self._show_in_explorer(path)
        elif chosen == copy_action:
            self._copy_path(path)
        elif chosen == cut_action:
            self._cut_path(path)
        elif chosen == delete_action:
            self._delete_path(path)
        elif chosen in menu.actions() and chosen.text() in ("Compile", "Run", "View Waves", "Generate Testbench", "Synthesize", "Show Schematic"):
            if chosen.text() == "Compile":
                self.compile_requested.emit(path)
            elif chosen.text() == "Run":
                self.run_requested.emit(path)
            elif chosen.text() == "View Waves":
                self.wave_requested.emit(path)
            elif chosen.text() == "Generate Testbench":
                self.gen_tb_requested.emit(path)
            elif chosen.text() == "Synthesize":
                self.synthesize_requested.emit(path)
            elif chosen.text() == "Show Schematic":
                self.show_schematic_requested.emit(path)

    def _show_in_explorer(self, path):
        folder = os.path.dirname(path)
        os.startfile(folder)

    def _copy_path(self, path):
        cb = QGuiApplication.clipboard()
        cb.setText(path)

    def _cut_path(self, path):
        cb = QGuiApplication.clipboard()
        cb.setText(path)
        self._cut_source = path

    def _delete_path(self, path):
        reply = QMessageBox.question(
            self, "Delete",
            f"Move '{os.path.basename(path)}' to trash?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            QFile.moveToTrash(path)
