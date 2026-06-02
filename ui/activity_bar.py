from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QToolBar, QWidget, QSizePolicy


class ActivityBar(QToolBar):

    def __init__(self, parent=None):
        super().__init__("Activity Bar", parent)

        self.setMovable(False)
        self.setOrientation(Qt.Orientation.Vertical)
        self.setIconSize(QSize(22, 22))
        self.setFixedWidth(44)

        self.main = parent
        self._build()

        from themes.theme_manager import ThemeManager
        self.apply_theme(ThemeManager.colors())

        self._populate_end()
        # Start with explorer checked
        self.explorer_btn.setChecked(True)

    def apply_theme(self, colors):
        self.setStyleSheet(f"""
            QToolBar {{
                background-color: {colors["panel_bg"]};
                border: none;
                spacing: 0px;
                padding: 0px;
            }}
            QToolButton {{
                border: none;
                border-radius: 0px;
                padding: 10px 8px;
                margin: 0px;
                icon-size: 22px;
                color: {colors["text"]};
            }}
            QToolButton:hover {{
                background-color: {colors["panel_hover"]};
            }}
            QToolButton:checked {{
                background-color: {colors["editor_bg"]};
                border-left: 2px solid {colors["accent"]};
            }}
        """)

    def _build(self):

        self.explorer_btn = self.addAction(
            QIcon("assets/icons/file_explorer.svg"),
            "File Explorer"
        )
        self.explorer_btn.setCheckable(True)
        self.explorer_btn.setChecked(True)
        self.explorer_btn.triggered.connect(self._on_explorer)

        self.hierarchy_btn = self.addAction(
            QIcon("assets/icons/hierarchy.svg"),
            "Hierarchy"
        )
        self.hierarchy_btn.setCheckable(True)
        self.hierarchy_btn.triggered.connect(self._on_hierarchy)

        self.connections_btn = self.addAction(
            QIcon("assets/icons/connections.svg"),
            "Connections"
        )
        self.connections_btn.setCheckable(True)
        self.connections_btn.triggered.connect(self._on_connections)

        self.templates_btn = self.addAction(
            QIcon("assets/icons/templates.svg"),
            "Templates"
        )
        self.templates_btn.setCheckable(True)
        self.templates_btn.triggered.connect(self._on_templates)

        self.git_btn = self.addAction(
            QIcon("assets/icons/git.svg"),
            "Git"
        )
        self.git_btn.setCheckable(True)
        self.git_btn.triggered.connect(self._on_git)

    def _uncheck_all(self):
        self.explorer_btn.setChecked(False)
        self.hierarchy_btn.setChecked(False)
        self.connections_btn.setChecked(False)
        self.templates_btn.setChecked(False)
        self.git_btn.setChecked(False)

    def _on_hierarchy(self):
        self._uncheck_all()
        self.hierarchy_btn.setChecked(True)
        self.main._show_activity_panel("hierarchy")

    def _on_explorer(self):
        self._uncheck_all()
        self.explorer_btn.setChecked(True)
        self.main._show_activity_panel("explorer")

    def _on_connections(self):
        self._uncheck_all()
        self.connections_btn.setChecked(True)
        self.main._show_activity_panel("connections")

    def _on_templates(self):
        self._uncheck_all()
        self.templates_btn.setChecked(True)
        self.main._show_activity_panel("templates")

    def _on_git(self):
        self._uncheck_all()
        self.git_btn.setChecked(True)
        self.main._show_activity_panel("git")

    def _populate_end(self):
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.addWidget(spacer)

        self.settings_btn = self.addAction(
            QIcon("assets/icons/settings.svg"),
            "Settings"
        )
        self.settings_btn.triggered.connect(self._on_settings)

    def _on_settings(self):
        from ui.settings_dialog import SettingsDialog
        dlg = SettingsDialog(self.main)
        dlg.exec()
