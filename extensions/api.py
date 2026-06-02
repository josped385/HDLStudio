import os
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QWidget


class ExtensionAPI:
    """Public API exposed to extensions."""

    def __init__(self, main_window, ext_id):
        self._main = main_window
        self._ext_id = ext_id
        self._registered_actions = {}
        self._owned_widgets = []

    # ── Actions ───────────────────────────────────────────

    def register_action(self, action_id, text, callback,
                        icon_path=None, shortcut=None):
        a = QAction(text, self._main)
        if icon_path:
            a.setIcon(QIcon(icon_path))
        if shortcut:
            a.setShortcut(shortcut)
        a.triggered.connect(callback)
        self._registered_actions[action_id] = a
        self._main.ide_actions._custom_actions[action_id] = a
        return a

    # ── Toolbar ───────────────────────────────────────────

    def add_toolbar_button(self, action_id):
        a = self._registered_actions.get(action_id)
        if a:
            self._main.toolbar.addAction(a)

    # ── Menu ──────────────────────────────────────────────

    def add_menu_item(self, menu_path, action_id):
        """menu_path: 'Tools/My Submenu'"""
        a = self._registered_actions.get(action_id)
        if not a:
            return
        parts = menu_path.split("/")
        menu = self._main.menuBar()
        for part in parts:
            found = None
            for existing in menu.actions():
                if existing.text().replace("&", "") == part:
                    if existing.menu():
                        found = existing.menu()
                        break
            if found is None:
                found = menu.addMenu(part)
            menu = found
        menu.addAction(a)

    # ── Activity bar ──────────────────────────────────────

    def add_activity_bar_button(self, action_id):
        a = self._registered_actions.get(action_id)
        if a:
            self._main.activity_bar._add_extension_action(action_id, a)

    def remove_activity_bar_button(self, action_id):
        self._main.activity_bar._remove_extension_action(action_id)

    # ── File explorer context menu ───────────────────────

    def add_explorer_context_action(self, action_id, text, file_pattern="*"):
        entry = {
            "text": text,
            "action_id": action_id,
            "file_pattern": file_pattern,
            "action": self._registered_actions.get(action_id),
        }
        self._main.file_explorer_dock.explorer._extension_actions.append(entry)

    # ── Bottom panel ──────────────────────────────────────

    def add_bottom_panel(self, panel_id, title, widget):
        self._owned_widgets.append(widget)
        self._main.bottom_panel.add_extension_tab(panel_id, title, widget)

    def remove_bottom_panel(self, panel_id):
        self._main.bottom_panel.remove_extension_tab(panel_id)

    # ── Console output ───────────────────────────────────

    def write_console(self, text, color=None):
        if color:
            self._main.bottom_panel.write_line(text, color=color)
        else:
            self._main.bottom_panel.write_info(text)

    def write_ok(self, text):
        self._main.bottom_panel.write_ok(text)

    def write_error(self, text):
        self._main.bottom_panel.write_error(text)

    # ── Settings persistence ──────────────────────────────

    def get_setting(self, key, default=None):
        from PyQt6.QtCore import QSettings
        s = QSettings("HDLStudio", "HDLStudio")
        s.beginGroup(f"extensions/{self._ext_id}")
        v = s.value(key, default)
        s.endGroup()
        return v

    def set_setting(self, key, value):
        from PyQt6.QtCore import QSettings
        s = QSettings("HDLStudio", "HDLStudio")
        s.beginGroup(f"extensions/{self._ext_id}")
        s.setValue(key, value)
        s.endGroup()

    # ── File dialogs ─────────────────────────────────────

    def get_open_filename(self, caption, filter_str):
        from PyQt6.QtWidgets import QFileDialog
        f, _ = QFileDialog.getOpenFileName(self._main, caption, "", filter_str)
        return f

    def get_save_filename(self, caption, filter_str):
        from PyQt6.QtWidgets import QFileDialog
        f, _ = QFileDialog.getSaveFileName(self._main, caption, "", filter_str)
        return f

    # ── Extension info ───────────────────────────────────

    def extension_dir(self):
        return os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "extensions", self._ext_id
        )

    # ── Cleanup ──────────────────────────────────────────

    def unregister_all(self):
        for aid, a in self._registered_actions.items():
            self._main.ide_actions._custom_actions.pop(aid, None)
        self._registered_actions.clear()
        for w in self._owned_widgets:
            w.setParent(None)
        self._owned_widgets.clear()
