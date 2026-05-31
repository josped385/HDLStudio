import os

from PyQt6.QtCore import pyqtSignal, Qt, QFile
from PyQt6.QtGui import QFileSystemModel, QGuiApplication, QIcon
from PyQt6.QtWidgets import QTreeView, QMenu, QMessageBox


class FileExplorer(QTreeView):

    file_open_requested = pyqtSignal(str)
    compile_requested = pyqtSignal(str)
    run_requested = pyqtSignal(str)
    wave_requested = pyqtSignal(str)

    _icons_loaded = False
    _icon_open = None
    _icon_copy = None
    _icon_cut = None
    _icon_delete = None
    _icon_compile = None
    _icon_run = None
    _icon_wave = None

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

    def _ensure_icons(self):
        if self._icons_loaded:
            return
        self._load_icons()
        self._icons_loaded = True

    def _load_icons(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        base = os.path.join(root, "assets", "icons")
        self._icon_open = QIcon(os.path.join(base, "file.svg"))
        self._icon_copy = QIcon(os.path.join(base, "file.svg"))
        self._icon_cut = QIcon(os.path.join(base, "file.svg"))
        self._icon_delete = QIcon(os.path.join(base, "delete.svg"))
        self._icon_compile = QIcon(os.path.join(base, "compile.svg"))
        self._icon_run = QIcon(os.path.join(base, "play.svg"))
        self._icon_wave = QIcon(os.path.join(base, "wave.svg"))

    def _show_context_menu(self, pos):
        path = self._file_under_menu(pos)
        if not path:
            return

        self._ensure_icons()

        menu = QMenu(self)
        ext = os.path.splitext(path)[1].lower()

        open_action = menu.addAction(self._icon_open, "Open")
        show_action = menu.addAction("Show in Explorer")
        menu.addSeparator()
        copy_action = menu.addAction(self._icon_copy, "Copy")
        cut_action = menu.addAction(self._icon_cut, "Cut")
        delete_action = menu.addAction(self._icon_delete, "Delete")
        menu.addSeparator()

        if ext in (".v", ".sv", ".vhd", ".vhdl"):
            compile_action = menu.addAction(self._icon_compile, "Compile")
        elif ext == ".vvp":
            run_action = menu.addAction(self._icon_run, "Run")
        elif ext in (".vcd", ".fst", ".lxt", ".lxt2", ".ghw"):
            wave_action = menu.addAction(self._icon_wave, "View Waves")

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
        elif chosen in menu.actions() and chosen.text() in ("Compile", "Run", "View Waves"):
            if chosen.text() == "Compile":
                self.compile_requested.emit(path)
            elif chosen.text() == "Run":
                self.run_requested.emit(path)
            elif chosen.text() == "View Waves":
                self.wave_requested.emit(path)

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
