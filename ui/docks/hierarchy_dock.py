import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import (
    QDockWidget, QVBoxLayout, QWidget, QLabel,
    QTreeWidget, QTreeWidgetItem, QHeaderView,
)

from core.hierarchy_parser import HierarchyParser


class HierarchyDock(QDockWidget):

    def __init__(self, parent=None):
        super().__init__("Hierarchy", parent)

        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
        )

        self._colors = None
        self._last_nodes = []

        self.container = QWidget()
        self.container.setObjectName("hierarchyDockContainer")
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Module", "Instance", "File"])
        self.tree.header().setStretchLastSection(True)
        self.tree.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tree.setRootIsDecorated(True)
        self.tree.setAnimated(True)
        self.tree.setIndentation(16)
        self.tree.setAlternatingRowColors(True)
        self.tree.setFont(QFont("Consolas", 9))
        self.tree.setHeaderHidden(False)
        layout.addWidget(self.tree)

        self.info_label = QLabel("No project open")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)
        self.info_label.hide()

        self.setWidget(self.container)

        from themes.theme_manager import ThemeManager
        self.apply_theme(ThemeManager.colors())

    def _is_dark(self, colors):
        text = colors.get("text", "#ffffff")
        r = int(text[1:3], 16)
        g = int(text[3:5], 16)
        b = int(text[5:7], 16)
        return (r + g + b) // 3 <= 128

    def apply_theme(self, colors):
        self._colors = colors
        bg = colors.get("main_bg", "#1e1e1e")
        panel_bg = colors.get("panel_bg", "#2b2b2b")
        fg = colors.get("text", "#dcdcdc")
        border = colors.get("border", "#555555")
        sel = colors.get("editor_selection", "#264f78")
        hover = colors.get("panel_hover", "#3c3f41")

        self.container.setStyleSheet(
            f"#hierarchyDockContainer {{ background-color: {bg}; }}"
        )
        self.tree.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {panel_bg};
                color: {fg};
                border: none;
                font-size: 9pt;
                font-family: Consolas, monospace;
            }}
            QTreeWidget::item {{
                padding: 3px 4px;
            }}
            QTreeWidget::item:selected {{
                background-color: {sel};
            }}
            QTreeWidget::item:hover {{
                background-color: {hover};
            }}
            QTreeWidget::item:alternate {{
                background-color: {colors.get("editor_line", "#2a2d2e")};
            }}
        """)
        self.info_label.setStyleSheet(
            f"color: {colors.get('text_secondary', '#aaaaaa')}; padding: 20px;"
        )

    def update_hierarchy(self, nodes):
        self._last_nodes = nodes
        self.tree.clear()
        self.tree.hide()
        self.info_label.hide()

        if not nodes:
            self.info_label.setText("No hierarchy detected")
            self.info_label.show()
            return

        hierarchy = HierarchyParser.build_hierarchy(nodes)
        if not hierarchy:
            self.info_label.setText("No top-level module found")
            self.info_label.show()
            return

        self.tree.show()
        self._populate_tree(hierarchy, None)

    def update_from_file(self, filepath):
        if not filepath or not os.path.isfile(filepath):
            self.tree.clear()
            self.tree.hide()
            self.info_label.setText("No hierarchy detected")
            self.info_label.show()
            return

        try:
            nodes = HierarchyParser.from_file(filepath)
        except Exception:
            self.tree.clear()
            self.tree.hide()
            self.info_label.setText("Error parsing hierarchy")
            self.info_label.show()
            return

        self.update_hierarchy(nodes)

    def update_from_project(self, project):
        if not project or not project.is_loaded():
            self.tree.clear()
            self.tree.hide()
            self.info_label.setText("No project open")
            self.info_label.show()
            return

        import glob
        root = project.root_path
        all_nodes = []
        for ext in ("*.v", "*.sv", "*.vhd", "*.vhdl"):
            for f in sorted(glob.glob(os.path.join(root, "**", ext), recursive=True)):
                try:
                    nodes = HierarchyParser.from_file(f)
                    all_nodes.extend(nodes)
                except Exception:
                    continue

        seen = set()
        merged = []
        for n in all_nodes:
            if n.module_name not in seen:
                seen.add(n.module_name)
                merged.append(n)

        all_instantiated = set()
        for n in merged:
            for inst in n.instantiations:
                all_instantiated.add(inst["module"])
        for n in merged:
            n.is_top = n.module_name not in all_instantiated

        self.update_hierarchy(merged)

    def _populate_tree(self, hierarchy, parent_item):
        c = getattr(self, "_colors", None)
        if c is None:
            from themes.theme_manager import ThemeManager
            c = ThemeManager.colors()

        for entry in hierarchy:
            mod = entry["module"]
            instance = entry.get("instance", "")
            filepath = entry.get("filepath", "")
            children = entry.get("children", [])
            is_top = parent_item is None

            basename = os.path.basename(filepath) if filepath else ""

            item = QTreeWidgetItem()

            # Column 0: module name (bold for top-level)
            item.setText(0, mod)
            color_str = self._color_for(is_top, c)
            item.setForeground(0, QColor(color_str))
            font = item.font(0)
            font.setBold(is_top)
            item.setFont(0, font)

            # Column 1: instance name (if not top-level)
            if instance:
                item.setText(1, instance)
                item.setForeground(1, QColor(c.get("text_secondary", "#888888")))

            # Column 2: file basename
            if basename:
                item.setText(2, basename)
                item.setForeground(2, QColor(c.get("text_secondary", "#888888")))

            # Tooltip
            tooltip_parts = [f"Module: {mod}"]
            if instance:
                tooltip_parts.append(f"Instance: {instance}")
            if filepath:
                tooltip_parts.append(f"File: {filepath}")
            item.setToolTip(0, "\n".join(tooltip_parts))

            if parent_item:
                parent_item.addChild(item)
            else:
                self.tree.addTopLevelItem(item)

            if children:
                self._populate_tree(children, item)

        if parent_item is None:
            self.tree.expandAll()

    @staticmethod
    def _color_for(is_top, colors):
        if is_top:
            return colors.get("accent", "#3d7eff")
        return colors.get("text", "#dcdcdc")
