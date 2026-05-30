from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QTreeWidget, QTreeWidgetItem, QTextEdit, QComboBox,
    QPushButton, QSplitter, QLabel,
)

from core.template_manager import TemplateManager


_LANG_NAMES = {
    "verilog": "Verilog",
    "systemverilog": "SystemVerilog",
    "vhdl": "VHDL",
}


class TemplateDock(QDockWidget):

    new_file_requested = pyqtSignal(str, str)  # filename, code

    def __init__(self, parent=None):
        super().__init__("Templates", parent)

        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
        )

        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
        )

        self._current_cat = None
        self._current_tpl = None

        container = QWidget()
        container.setObjectName("templateDockContainer")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Tree: categories -> templates
        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setIndentation(16)
        self._tree.setAnimated(True)
        self._tree.setExpandsOnDoubleClick(False)
        self._tree.currentItemChanged.connect(self._on_item_changed)
        self._tree.setMinimumHeight(120)

        # Populate tree
        for cat in TemplateManager.get_categories():
            cat_item = QTreeWidgetItem([cat["name"]])
            cat_item.setData(0, Qt.ItemDataRole.UserRole, ("cat", cat["id"]))
            cat_item.setFlags(cat_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            for tpl in cat["templates"]:
                tpl_item = QTreeWidgetItem([tpl["name"]])
                tpl_item.setData(0, Qt.ItemDataRole.UserRole, ("tpl", cat["id"], tpl["id"]))
                tpl_item.setToolTip(0, tpl.get("description", ""))
                cat_item.addChild(tpl_item)
            self._tree.addTopLevelItem(cat_item)

        # Description
        self._desc = QLabel()
        self._desc.setWordWrap(True)
        self._desc.setContentsMargins(8, 4, 8, 4)

        # Preview
        self._preview = QTextEdit()
        self._preview.setReadOnly(True)
        self._preview.setFont(QFont("Consolas", 9))
        self._preview.setMinimumHeight(100)
        self._preview.setPlaceholderText("Select a template to preview")

        # Format selector
        fmt_layout = QHBoxLayout()
        fmt_layout.setContentsMargins(8, 4, 8, 4)
        fmt_layout.addWidget(QLabel("Format:"))
        self._format_combo = QComboBox()
        self._format_combo.currentIndexChanged.connect(self._show_preview)
        fmt_layout.addWidget(self._format_combo, 1)

        # New file button
        self._new_btn = QPushButton("New File with Template")
        self._new_btn.clicked.connect(self._on_new_file)

        # Splitter: tree top, preview bottom
        splitter = QSplitter(Qt.Orientation.Vertical)
        tree_container = QWidget()
        tree_layout = QVBoxLayout(tree_container)
        tree_layout.setContentsMargins(0, 0, 0, 0)
        tree_layout.setSpacing(0)
        tree_layout.addWidget(self._tree)
        tree_layout.addWidget(self._desc)
        tree_container.setMinimumHeight(150)

        preview_container = QWidget()
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.setSpacing(0)
        preview_layout.addWidget(self._preview)
        preview_layout.addLayout(fmt_layout)
        preview_layout.addWidget(self._new_btn)

        splitter.addWidget(tree_container)
        splitter.addWidget(preview_container)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter)
        self.setWidget(container)

        from themes.theme_manager import ThemeManager
        self.apply_theme(ThemeManager.colors())

    def apply_theme(self, colors):
        bg = colors.get("editor_bg", "#1e1e1e")
        fg = colors.get("editor_text", "#dcdcdc")
        panel_bg = colors.get("panel_bg", "#2b2b2b")
        border = colors.get("border", "#555555")
        text_sec = colors.get("text_secondary", "#aaaaaa")

        self.setStyleSheet(f"""
            #templateDockContainer {{
                background-color: {panel_bg};
            }}
        """)

        self._preview.setStyleSheet(f"""
            QTextEdit {{
                background-color: {bg};
                color: {fg};
                border: 1px solid {border};
                font-family: Consolas, monospace;
                font-size: 9pt;
            }}
        """)

        self._desc.setStyleSheet(f"""
            QLabel {{
                color: {text_sec};
                font-size: 9pt;
                background-color: {panel_bg};
                padding: 4px 8px;
            }}
        """)

        self._tree.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {panel_bg};
                color: {fg};
                border: none;
                font-size: 10pt;
            }}
            QTreeWidget::item {{
                padding: 4px 4px;
            }}
            QTreeWidget::item:selected {{
                background-color: {colors.get("editor_selection", "#264f78")};
            }}
            QTreeWidget::item:hover {{
                background-color: {colors.get("panel_hover", "#3c3f41")};
            }}
        """)

        self._format_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {bg};
                color: {fg};
                border: 1px solid {border};
                padding: 4px 8px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
        """)

        self._new_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors.get("accent", "#3d7eff")};
                color: #ffffff;
                border: none;
                padding: 8px;
                font-size: 10pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {colors.get("accent_light", "#5a9eff")};
            }}
            QPushButton:disabled {{
                background-color: {border};
                color: {text_sec};
            }}
        """)

    def _on_item_changed(self, current, previous):
        if not current:
            return
        data = current.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return
        kind = data[0]
        if kind == "tpl":
            cat_id, tpl_id = data[1], data[2]
            self._current_cat = cat_id
            self._current_tpl = tpl_id
            tmpl = TemplateManager.get_template(cat_id, tpl_id)
            if tmpl:
                self._desc.setText(tmpl.get("description", ""))
            self._update_format_combo(cat_id, tpl_id)
            self._new_btn.setEnabled(True)
        else:
            self._current_cat = None
            self._current_tpl = None
            self._format_combo.clear()
            self._preview.clear()
            self._desc.clear()
            self._new_btn.setEnabled(False)

    def _update_format_combo(self, cat_id, tpl_id):
        self._format_combo.blockSignals(True)
        self._format_combo.clear()
        langs = TemplateManager.available_languages(cat_id, tpl_id)
        for lang in langs:
            self._format_combo.addItem(_LANG_NAMES.get(lang, lang), lang)
        # Prefer systemverilog, then verilog, then first available
        preferred = "systemverilog"
        if preferred not in langs:
            preferred = "verilog"
        if preferred not in langs:
            preferred = langs[0] if langs else ""
        idx = self._format_combo.findData(preferred)
        if idx >= 0:
            self._format_combo.setCurrentIndex(idx)
        self._format_combo.blockSignals(False)
        self._show_preview()

    def _show_preview(self):
        if not self._current_cat or not self._current_tpl:
            self._preview.clear()
            return
        lang = self._format_combo.currentData()
        code = TemplateManager.get_code(self._current_cat, self._current_tpl, lang)
        if code:
            self._preview.setPlainText(code)

    def _on_new_file(self):
        if not self._current_cat or not self._current_tpl:
            return
        lang = self._format_combo.currentData()
        code = TemplateManager.get_code(self._current_cat, self._current_tpl, lang)
        if not code:
            return
        ext_map = {"verilog": ".v", "systemverilog": ".sv", "vhdl": ".vhd"}
        ext = ext_map.get(lang, ".v")
        tmpl = TemplateManager.get_template(self._current_cat, self._current_tpl)
        filename = f"{tmpl['id']}{ext}"
        self.new_file_requested.emit(filename, code)
