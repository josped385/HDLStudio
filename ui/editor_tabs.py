import os
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QTabWidget

from ui.editor_tab import EditorTab


class EditorTabs(QTabWidget):

    def __init__(self):
        super().__init__()

        self.tabs = {}  # path -> EditorTab
        self.untitled_counter = 0

        self.currentChanged.connect(self._on_tab_changed)

        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)

        self.tabCloseRequested.connect(self.close_tab)

    def _on_tab_changed(self, index):

        widget = self.widget(index)
        tab = self.get_tab_by_editor(widget)

        if not tab:
            return

        # reconnect cursor signal safely
        try:
            tab.editor.cursor_position_changed.disconnect()
        except:
            pass

        tab.editor.cursor_position_changed.connect(
            self._emit_cursor_change
        )

    def _emit_cursor_change(self, line, col):

        # propagate to main window via central widget
        self.parent().status.file_label.setText(
            f"{self.current_tab().filename}"
        )

        self.parent().status.position_label.setText(
            f"Ln {line}, Col {col}"
        )

    # ---------------- OPEN FILE ----------------

    def open_file(self, path):

        # Already open
        if path in self.tabs:
            tab = self.tabs[path]
            self.setCurrentWidget(tab.editor)
            return

        try:
            tab = EditorTab(path)
            tab.load_file()

            tab.modified_changed.connect(self._on_tab_modified)

            self.tabs[path] = tab

            self.addTab(
                tab.editor,
                QIcon("assets/icons/file.svg"),
                tab.filename
            )

            self.setCurrentWidget(tab.editor)

        except Exception as e:
            print(f"Error opening file: {e}")

    # ---------------- CLOSE TAB ----------------

    def close_tab(self, index):

        widget = self.widget(index)
        tab = self.get_tab_by_editor(widget)

        if tab:

            if tab.path in self.tabs:
                del self.tabs[tab.path]

        self.removeTab(index)

    # ---------------- MODIFIED HANDLING ----------------

    def _on_tab_modified(self, modified):

        tab = self.sender()

        index = self._find_tab_index(tab.editor)

        if index == -1:
            return

        name = self.tabText(index)

        if modified:
            if not name.endswith("*"):
                self.setTabText(index, name + "*")
        else:
            if name.endswith("*"):
                self.setTabText(index, name[:-1])

    def _find_tab_index(self, widget):

        for i in range(self.count()):
            if self.widget(i) == widget:
                return i

        return -1

    # ---------------- UTIL ----------------

    def get_tab_by_editor(self, editor_widget):

        for tab in self.tabs.values():
            if tab.editor == editor_widget:
                return tab
        return None

    def current_tab(self):

        widget = self.currentWidget()
        return self.get_tab_by_editor(widget)

    def mark_saved(self, tab):

        index = self._find_tab_index(tab.editor)

        if index == -1:
            return

        name = self.tabText(index)

        if name.endswith("*"):
            self.setTabText(index, name[:-1])

    def new_file(self):

        self.untitled_counter += 1

        tab = EditorTab(None)

        tab.modified_changed.connect(self._on_tab_modified)

        self.tabs[id(tab.editor)] = tab

        self.addTab(
            tab.editor,
            QIcon("assets/icons/file.svg"),
            f"untitled-{self.untitled_counter}"
        )

        self.setCurrentWidget(tab.editor)

    def save_current_as(self, path):

        tab = self.current_tab()

        if not tab:
            return

        success = tab.save_as(path)

        if success:
            self._rename_tab(tab)

    def _rename_tab(self, tab):

        index = self._find_tab_index(tab.editor)

        if index != -1:
            self.setTabText(index, tab.filename)