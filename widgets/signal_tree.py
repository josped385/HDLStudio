from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor


_SECTION_COLORS_DARK = {
    "module":       "#569cd6",
    "inputs":       "#4ec9b0",
    "outputs":      "#c586c0",
    "inouts":       "#dcdcaa",
    "wires":        "#6a9955",
    "regs":         "#ce9178",
    "signals":      "#6a9955",
    "internal":     "#aaaaaa",
}

_SECTION_COLORS_LIGHT = {
    "module":       "#0057a0",
    "inputs":       "#008060",
    "outputs":      "#7030a0",
    "inouts":       "#606000",
    "wires":        "#306030",
    "regs":         "#a05020",
    "signals":      "#306030",
    "internal":     "#606060",
}


class SignalTree(QTreeWidget):

    COL_NAME = 0
    COL_TYPE = 1
    COL_WIDTH = 2

    def __init__(self):
        super().__init__()

        self.setHeaderLabels(["Signal", "Type", "Width"])
        self.header().setStretchLastSection(True)
        self.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.setRootIsDecorated(True)
        self.setAnimated(True)
        self.setIndentation(16)
        self.setAlternatingRowColors(True)

        font = QFont("Consolas", 9)
        self.setFont(font)

        self.setStyleSheet("""
            QTreeWidget {
                border: none;
            }
            QTreeWidget::item {
                padding: 2px 4px;
            }
        """)

        self._section_palette = _SECTION_COLORS_DARK

    def _is_dark(self, colors):
        text = colors.get("text", "#ffffff")
        r = int(text[1:3], 16)
        g = int(text[3:5], 16)
        b = int(text[5:7], 16)
        return (r + g + b) // 3 > 128

    def apply_theme(self, colors):
        self._colors = colors
        self._section_palette = (
            _SECTION_COLORS_DARK if self._is_dark(colors)
            else _SECTION_COLORS_LIGHT
        )
        if hasattr(self, '_last_data') and self._last_data is not None:
            self.display_signals(self._last_data)

    def display_signals(self, data):
        self._last_data = data
        self.clear()
        c = getattr(self, "_colors", None)
        if c is None:
            from themes.theme_manager import ThemeManager
            c = ThemeManager.colors()
            self._colors = c

        text_fg = QColor(c["text"])
        dim_fg = QColor(c["text_secondary"])
        dimmer_fg = QColor(c.get("text_secondary", "#aaaaaa"))

        if not data:
            item = QTreeWidgetItem(self, ["No signals found"])
            item.setForeground(0, dim_fg)
            return

        module_name = data.get("module") or "design"
        root_item = QTreeWidgetItem(self, [module_name])
        root_font = self.font()
        root_font.setBold(True)
        root_item.setFont(0, root_font)
        root_item.setForeground(0, QColor(self._section_palette["module"]))
        root_item.setExpanded(True)

        sections = [
            ("inputs", "Inputs", self._section_palette["inputs"], "in"),
            ("outputs", "Outputs", self._section_palette["outputs"], "out"),
            ("inouts", "Inouts", self._section_palette["inouts"], "inout"),
        ]

        for key, label, color_hex, direction in sections:
            items = data.get(key, [])
            section_item = QTreeWidgetItem(root_item, [label])
            section_item.setForeground(0, QColor(color_hex))
            section_font = self.font()
            section_font.setBold(True)
            section_item.setFont(0, section_font)
            section_item.setExpanded(True)

            for sig in items:
                sig_item = QTreeWidgetItem(section_item)
                sig_item.setText(0, sig.name)
                sig_item.setText(1, sig.signal_type)
                sig_item.setText(2, sig.width or "")
                sig_item.setToolTip(0, f"{sig.direction}: {sig.name}")
                sig_item.setForeground(0, text_fg)
                sig_item.setForeground(1, dim_fg)
                sig_item.setForeground(2, dimmer_fg)

        internal_sections = []
        if "wires" in data and data["wires"]:
            internal_sections.append(("wires", "Wires", self._section_palette["wires"]))
        if "regs" in data and data["regs"]:
            internal_sections.append(("regs", "Registers", self._section_palette["regs"]))
        if "signals" in data and data["signals"]:
            internal_sections.append(("signals", "Signals", self._section_palette["signals"]))

        if internal_sections:
            internal_root = QTreeWidgetItem(root_item, ["Internal"])
            internal_root.setForeground(0, QColor(self._section_palette["internal"]))
            ir_font = self.font()
            ir_font.setBold(True)
            internal_root.setFont(0, ir_font)
            internal_root.setExpanded(True)

            for key, label, color_hex in internal_sections:
                items = data.get(key, [])
                for sig in items:
                    sig_item = QTreeWidgetItem(internal_root)
                    sig_item.setText(0, sig.name)
                    sig_item.setText(1, sig.signal_type)
                    sig_item.setText(2, sig.width or "")
                    sig_item.setToolTip(0, f"{sig.direction}: {sig.name}")
                    sig_item.setForeground(0, QColor(color_hex))
                    sig_item.setForeground(1, dim_fg)
                    sig_item.setForeground(2, dimmer_fg)
