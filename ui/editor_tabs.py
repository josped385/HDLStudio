import os
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QTabWidget, QMessageBox

from ui.editor_tab import EditorTab


class EditorTabs(QTabWidget):

    def __init__(self):
        super().__init__()

        # editor_tab -> EditorTab
        self.tabs = {}

        self.project = None

        self.untitled_counter = 0

        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)

        self.tabCloseRequested.connect(self.close_tab)
        self.currentChanged.connect(self._on_tab_changed)

    # ---------------- CURRENT TAB ----------------

    def current_tab(self):

        widget = self.currentWidget()

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

        tab.modified_changed.connect(self._on_tab_modified)

        self.tabs[path] = tab

        # ---------------- DISPLAY NAME ----------------
        if self.project and self.project.is_inside(path):
            display_name = self.project.to_relative(path)
        else:
            display_name = os.path.basename(path)

        # ---------------- ADD TAB ----------------
        self.addTab(
            tab.editor,
            QIcon("assets/icons/file.svg"),
            display_name
        )

        self.setCurrentWidget(tab.editor)

    # ---------------- NEW FILE ----------------

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

    # ---------------- CLOSE TAB (SAFE) ----------------

    def close_tab(self, index):

        widget = self.widget(index)

        tab = None
        for t in self.tabs.values():
            if t.editor == widget:
                tab = t
                break

        if not tab:
            self.removeTab(index)
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
            del self.tabs[key_to_remove]

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

    # ---------------- TAB CHANGE ----------------

    def _on_tab_changed(self, index):

        tab = self.current_tab()

        if not tab:
            return

        # status bar update
        self.parent().status.file_label.setText(tab.filename)

        # cursor tracking connect (safe, no disconnect hack)
        tab.editor.cursor_position_changed.connect(
            self._emit_cursor_change
        )

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

    def _rename_tab(self, tab):

        index = self._find_tab_index(tab.editor)

        if index != -1:
            self.setTabText(index, tab.filename)

    # ---------------- UTIL ----------------

    def _find_tab_index(self, widget):

        for i in range(self.count()):
            if self.widget(i) == widget:
                return i
        return -1