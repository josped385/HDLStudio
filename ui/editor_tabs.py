import os
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QFont, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QTabWidget, QTabBar, QMessageBox, QPushButton,
    QWidget, QVBoxLayout,
)

from ui.editor_tab import EditorTab
from ui.find_replace import FindReplaceBar
from themes.theme_manager import ThemeManager


class PlusTabBar(QTabBar):
    plusClicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._plus_btn = QPushButton("+", self)
        f = QFont("Consolas", 14)
        f.setBold(True)
        self._plus_btn.setFont(f)
        self._plus_btn.setFixedSize(28, 26)
        self._plus_btn.setFlat(True)
        self._plus_btn.setCursor(Qt.CursorShape.ArrowCursor)
        self._plus_btn.clicked.connect(self.plusClicked.emit)
        self._plus_btn.show()

    def _reposition_plus(self):
        if self.count() == 0:
            x = 2
        else:
            last_rect = self.tabRect(self.count() - 1)
            x = last_rect.right() + 2
        y = (self.height() - self._plus_btn.height()) // 2
        self._plus_btn.move(x, y)
        self._plus_btn.raise_()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._reposition_plus()

    def tabLayoutChange(self):
        super().tabLayoutChange()
        self._reposition_plus()

    def style_plus_btn(self, colors):
        self._plus_btn.setStyleSheet(f"""
            QPushButton {{
                color: {colors["text"]};
                background: transparent;
                border: none;
                padding: 0px 4px;
            }}
            QPushButton:hover {{
                color: {colors["accent"]};
                background: {colors["panel_hover"]};
            }}
        """)


class EditorTabs(QWidget):

    currentChanged = pyqtSignal(int)

    def __init__(self, hover_db=None):
        super().__init__()

        self._hover_db = hover_db

        # editor_tab -> EditorTab
        self.tabs = {}

        self.project = None

        self.untitled_counter = 0

        # Tab widget
        self._tab = QTabWidget()
        self._tab.tabCloseRequested.connect(self.close_tab)
        self._tab.currentChanged.connect(self._on_tab_changed)
        self._tab.currentChanged.connect(self.currentChanged.emit)
        self._tab.setTabsClosable(True)
        self._tab.setMovable(True)
        self._tab.setDocumentMode(True)

        self._setup_plus_tab_bar()

        # Find/Replace bar
        self._find_bar = FindReplaceBar(self)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._find_bar)
        layout.addWidget(self._tab, 1)

        # Shortcuts
        self._find_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        self._find_shortcut.activated.connect(self._show_find)

        self._replace_shortcut = QShortcut(QKeySequence("Ctrl+H"), self)
        self._replace_shortcut.activated.connect(self._show_replace)

    def _setup_plus_tab_bar(self):
        bar = PlusTabBar(self._tab)
        bar.plusClicked.connect(self._on_new_tab)
        self._tab.setTabBar(bar)
        self._plus_bar = bar

    def _show_find(self):
        self._find_bar.show_bar()

    def _show_replace(self):
        self._find_bar.show_bar()
        self._find_bar._replace_input.setFocus()

    def _style_plus_tab_bar(self):
        c = ThemeManager.colors()
        self._plus_bar.style_plus_btn(c)

    def _on_new_tab(self):
        from ui.main_window import MainWindow
        parent = self.window()
        if isinstance(parent, MainWindow):
            parent.new_file()

    # ---------------- CURRENT TAB ----------------

    def current_tab(self):

        widget = self._tab.currentWidget()

        for tab in self.tabs.values():
            if tab.editor == widget:
                return tab

        return None

    def set_project(self, project):

        self.project = project

    # ---------------- OPEN FILE ----------------

    def open_file(self, path):

        # normalize path
        path = os.path.abspath(path)

        # already open
        if path in self.tabs:
            tab = self.tabs[path]
            self.setCurrentWidget(tab.editor)
            return

        # create tab
        tab = EditorTab(path)
        tab.load_file()
        tab.editor.set_hover_database(self._hover_db)

        tab.modified_changed.connect(
            lambda modified, t=tab: self._on_tab_modified(t, modified)
        )

        self.tabs[path] = tab

        if self._hover_db:
            self._hover_db.add_file(path)

        # ---------------- DISPLAY NAME ----------------
        if self.project and self.project.is_inside(path):
            display_name = self.project.to_relative(path)
        else:
            display_name = os.path.basename(path)

        # ---------------- ADD TAB ----------------
        self._tab.addTab(
            tab.editor,
            QIcon(ThemeManager.icon("file")),
            display_name
        )
        self._tab.setCurrentWidget(tab.editor)

        tab.editor.apply_theme_from_colors()

    # ---------------- NEW FILE ----------------

    def new_file(self, content=None, suggested_name=None):

        self.untitled_counter += 1

        tab = EditorTab(None)
        tab.editor.set_hover_database(self._hover_db)

        tab.modified_changed.connect(
            lambda modified, t=tab: self._on_tab_modified(t, modified)
        )

        self.tabs[id(tab.editor)] = tab

        name = suggested_name or f"untitled-{self.untitled_counter}"
        self._tab.addTab(
            tab.editor,
            QIcon(ThemeManager.icon("file")),
            name
        )

        self._tab.setCurrentWidget(tab.editor)

        if content:
            tab.editor.setText(content)
            if suggested_name:
                ext = os.path.splitext(suggested_name)[1].lower()
                if ext in (".v", ".sv", ".vhd"):
                    tab.editor.set_lexer_for_file(suggested_name)
                    tab.editor.apply_theme_from_colors()

        tab.editor.apply_theme_from_colors()

    # ---------------- CLOSE TAB (SAFE) ----------------

    def close_tab(self, index):

        widget = self._tab.widget(index)

        tab = None
        for t in self.tabs.values():
            if t.editor == widget:
                tab = t
                break

        if not tab:
            self._tab.removeTab(index)
            return

        # 🔥 CHECK MODIFIED STATE
        if tab.modified:

            result = QMessageBox.question(
                self,
                "Unsaved Changes",
                f"Save changes to {tab.filename}?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )

            if result == QMessageBox.StandardButton.Cancel:
                return

            if result == QMessageBox.StandardButton.Save:
                tab.save()

        # remove from registry
        key_to_remove = None

        for k, v in self.tabs.items():
            if v == tab:
                key_to_remove = k
                break

        if key_to_remove:
            if self._hover_db and isinstance(key_to_remove, str):
                self._hover_db.remove_file(key_to_remove)
            del self.tabs[key_to_remove]

        self._tab.removeTab(index)

    # ---------------- MODIFIED HANDLING ----------------

    def _on_tab_modified(self, tab, modified):

        index = self._find_tab_index(tab.editor)

        if index == -1:
            return

        name = self._tab.tabText(index)

        if modified:
            if not name.endswith("*"):
                self._tab.setTabText(index, name + "*")
        else:
            if name.endswith("*"):
                self._tab.setTabText(index, name[:-1])

    # ---------------- TAB CHANGE ----------------

    def _on_tab_changed(self, index):

        tab = self.current_tab()

        if not tab:
            return

        # status bar update
        self.parent().status.file_label.setText(tab.filename)

        # disconnect previous editor's cursor signal to avoid leaks
        if hasattr(self, '_prev_cursor_tab') and self._prev_cursor_tab is not None:
            try:
                self._prev_cursor_tab.editor.cursor_position_changed.disconnect(
                    self._emit_cursor_change
                )
            except TypeError:
                pass

        # connect current editor's cursor signal
        tab.editor.cursor_position_changed.connect(
            self._emit_cursor_change
        )
        self._prev_cursor_tab = tab

        # emit initial cursor position
        line, col = tab.editor.getCursorPosition()
        self._emit_cursor_change(line + 1, col + 1)

    def _emit_cursor_change(self, line, col):

        tab = self.current_tab()

        if not tab:
            return

        self.parent().status.position_label.setText(
            f"Ln {line}, Col {col}"
        )

    # ---------------- SAVE AS ----------------

    def save_current_as(self, path):

        tab = self.current_tab()

        if not tab:
            return

        if tab.save_as(path):
            self._rename_tab(tab)
            self._rekey_tab(tab, path)
            if self._hover_db:
                self._hover_db.add_file(path)

    def _rename_tab(self, tab):

        index = self._find_tab_index(tab.editor)

        if index != -1:
            self._tab.setTabText(index, tab.filename)

    def _rekey_tab(self, tab, new_key):

        old_key = None
        for k, v in list(self.tabs.items()):
            if v == tab:
                old_key = k
                break

        if old_key is not None and old_key != new_key:
            del self.tabs[old_key]
            self.tabs[new_key] = tab

    # ---------------- TAB ICON / COUNT HELPERS ----------------

    def count(self):
        return self._tab.count()

    def setTabIcon(self, index, icon):
        self._tab.setTabIcon(index, icon)

    def setCurrentWidget(self, widget):
        self._tab.setCurrentWidget(widget)

    # ---------------- UTIL ----------------

    def _find_tab_index(self, widget):

        for i in range(self._tab.count()):
            if self._tab.widget(i) == widget:
                return i
        return -1