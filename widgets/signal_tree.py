from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QIcon


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

    def display_signals(self, data):
        self.clear()

        if not data:
            item = QTreeWidgetItem(self, ["No signals found"])
            item.setForeground(0, QColor("#888888"))
            return

        module_name = data.get("module") or "design"
        root_item = QTreeWidgetItem(self, [module_name])
        root_font = self.font()
        root_font.setBold(True)
        root_item.setFont(0, root_font)
        root_item.setForeground(0, QColor("#569cd6"))
        root_item.setExpanded(True)

        sections = [
            ("inputs", "Inputs", QColor("#4ec9b0"), "in"),
            ("outputs", "Outputs", QColor("#c586c0"), "out"),
            ("inouts", "Inouts", QColor("#dcdcaa"), "inout"),
        ]

        for key, label, color, direction in sections:
            items = data.get(key, [])
            section_item = QTreeWidgetItem(root_item, [label])
            section_item.setForeground(0, color)
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
                sig_item.setForeground(0, QColor("#dcdcdc"))
                sig_item.setForeground(1, QColor("#aaaaaa"))
                sig_item.setForeground(2, QColor("#808080"))

        # Internal signals
        internal_sections = []
        if "wires" in data and data["wires"]:
            internal_sections.append(("wires", "Wires", QColor("#6a9955")))
        if "regs" in data and data["regs"]:
            internal_sections.append(("regs", "Registers", QColor("#ce9178")))
        if "signals" in data and data["signals"]:
            internal_sections.append(("signals", "Signals", QColor("#6a9955")))

        if internal_sections:
            internal_root = QTreeWidgetItem(root_item, ["Internal"])
            internal_root.setForeground(0, QColor("#888888"))
            ir_font = self.font()
            ir_font.setBold(True)
            internal_root.setFont(0, ir_font)
            internal_root.setExpanded(True)

            for key, label, color in internal_sections:
                items = data.get(key, [])
                for sig in items:
                    sig_item = QTreeWidgetItem(internal_root)
                    sig_item.setText(0, sig.name)
                    sig_item.setText(1, sig.signal_type)
                    sig_item.setText(2, sig.width or "")
                    sig_item.setToolTip(0, f"{sig.direction}: {sig.name}")
                    sig_item.setForeground(0, color)
                    sig_item.setForeground(1, QColor("#aaaaaa"))
                    sig_item.setForeground(2, QColor("#808080"))