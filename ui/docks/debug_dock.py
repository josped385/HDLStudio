import os
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDockWidget, QVBoxLayout, QWidget, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QHBoxLayout,
)
from PyQt6.QtGui import QColor, QFont


class DebugDock(QDockWidget):

    def __init__(self, parent=None):
        super().__init__("Debug", parent)

        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
        )

        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
        )

        self.container = QWidget()
        self.container.setObjectName("debugDockContainer")
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(4, 4, 4, 4)

        header_layout = QHBoxLayout()
        self._time_label = QLabel("Time: --")
        self._time_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        self._index_label = QLabel("(0/0)")
        self._index_label.setStyleSheet("color: #888;")
        header_layout.addWidget(self._time_label)
        header_layout.addStretch()
        header_layout.addWidget(self._index_label)
        layout.addLayout(header_layout)

        self._table = QTableWidget(0, 2)
        self._table.setHorizontalHeaderLabels(["Signal", "Value"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.setFont(QFont("Consolas", 10))
        layout.addWidget(self._table)

        self._info_label = QLabel("No debug session")
        self._info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._info_label.setStyleSheet("color: #888; padding: 20px;")
        layout.addWidget(self._info_label)

        self.setWidget(self.container)

    def update_from_step(self, parser, current_time, time_idx, total_times):
        if not parser or not parser.time_values:
            self.clear_display()
            return

        self._info_label.hide()
        self._table.show()

        self._time_label.setText(f"Time: {current_time} {parser.timescale}")
        self._index_label.setText(f"({time_idx + 1}/{total_times})")

        snaps = parser.snapshots.get(current_time, {})
        code_to_name = parser.var_codes

        signals = []
        for code in sorted(snaps.keys(), key=lambda c: code_to_name.get(c, c)):
            name = code_to_name.get(code, code)
            val = snaps[code]
            signals.append((name, val))

        self._table.setRowCount(len(signals))
        for row, (name, val) in enumerate(signals):
            self._table.setItem(row, 0, QTableWidgetItem(name))
            item = QTableWidgetItem(str(val))
            if val in ("1", "0", "x", "z"):
                if val == "1":
                    item.setForeground(QColor("#4CAF50"))
                elif val == "0":
                    item.setForeground(QColor("#9E9E9E"))
                else:
                    item.setForeground(QColor("#FF9800"))
            self._table.setItem(row, 1, item)

        self._table.resizeColumnsToContents()

    def clear_display(self):
        self._table.setRowCount(0)
        self._table.hide()
        self._info_label.setText("No debug session")
        self._info_label.show()

    def apply_theme(self, colors):
        self.container.setStyleSheet(
            f"#debugDockContainer {{ background-color: {colors['main_bg']}; }}"
        )
        self._table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {colors['input_bg']};
                color: {colors['text_primary']};
                gridline-color: {colors['border']};
                alternate-background-color: {colors['hover_bg']};
            }}
            QHeaderView::section {{
                background-color: {colors['sidebar_bg']};
                color: {colors['text_primary']};
                border: 1px solid {colors['border']};
            }}
        """)
