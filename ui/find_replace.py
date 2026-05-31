import re
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QFrame, QWidget, QHBoxLayout, QVBoxLayout,
    QLineEdit, QPushButton, QLabel, QCheckBox,
    QToolButton,
)


class FindReplaceBar(QFrame):

    def __init__(self, editor_tabs):
        super().__init__()
        self._tabs = editor_tabs
        self._current_editor = None
        self._last_expr = ""
        self._match_count = 0
        self._current_index = 0

        self.setObjectName("findReplaceBar")
        self.setFixedHeight(62)
        self.hide()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 4, 8, 4)
        main_layout.setSpacing(4)

        # --- Find row ---
        find_row = QHBoxLayout()
        find_row.setSpacing(6)

        self._find_input = QLineEdit()
        self._find_input.setPlaceholderText("Find...")
        self._find_input.setMinimumWidth(200)
        self._find_input.textChanged.connect(self._on_text_changed)
        self._find_input.returnPressed.connect(self._find_next)

        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(250)
        self._debounce.timeout.connect(self._do_count)

        self._count_active = False

        self._match_label = QLabel()
        self._match_label.setFixedWidth(60)

        self._prev_btn = QToolButton()
        self._prev_btn.setText("\u25B2")
        self._prev_btn.setToolTip("Find Previous (Shift+F3)")
        self._prev_btn.clicked.connect(self._find_prev)
        self._prev_btn.setFixedWidth(28)

        self._next_btn = QToolButton()
        self._next_btn.setText("\u25BC")
        self._next_btn.setToolTip("Find Next (F3)")
        self._next_btn.clicked.connect(self._find_next)
        self._next_btn.setFixedWidth(28)

        self._close_btn = QToolButton()
        self._close_btn.setText("\u2715")
        self._close_btn.setToolTip("Close (Escape)")
        self._close_btn.clicked.connect(self.hide_bar)
        self._close_btn.setFixedWidth(28)

        find_row.addWidget(QLabel("Find:"))
        find_row.addWidget(self._find_input, 1)
        find_row.addWidget(self._match_label)
        find_row.addWidget(self._prev_btn)
        find_row.addWidget(self._next_btn)
        find_row.addWidget(self._close_btn)

        # --- Replace row ---
        replace_row = QHBoxLayout()
        replace_row.setSpacing(6)

        self._replace_input = QLineEdit()
        self._replace_input.setPlaceholderText("Replace with...")
        self._replace_input.setMinimumWidth(200)
        self._replace_input.returnPressed.connect(self._replace)

        self._replace_btn = QPushButton("Replace")
        self._replace_btn.setFixedWidth(80)
        self._replace_btn.clicked.connect(self._replace)

        self._replace_all_btn = QPushButton("Replace All")
        self._replace_all_btn.setFixedWidth(100)
        self._replace_all_btn.clicked.connect(self._replace_all)

        self._case_cb = QCheckBox("Aa")
        self._case_cb.setToolTip("Case sensitive")
        self._case_cb.toggled.connect(self._on_text_changed)

        self._word_cb = QCheckBox("W")
        self._word_cb.setToolTip("Whole word")
        self._word_cb.toggled.connect(self._on_text_changed)

        self._regex_cb = QCheckBox(".*")
        self._regex_cb.setToolTip("Regex")
        self._regex_cb.toggled.connect(self._on_text_changed)

        replace_row.addWidget(QLabel("Replace:"))
        replace_row.addWidget(self._replace_input, 1)
        replace_row.addWidget(self._replace_btn)
        replace_row.addWidget(self._replace_all_btn)
        replace_row.addSpacing(10)
        replace_row.addWidget(self._case_cb)
        replace_row.addWidget(self._word_cb)
        replace_row.addWidget(self._regex_cb)

        main_layout.addLayout(find_row)
        main_layout.addLayout(replace_row)

        # --- Shortcuts ---
        self._next_shortcut = QShortcut(QKeySequence("F3"), self)
        self._next_shortcut.activated.connect(self._find_next)

        self._prev_shortcut = QShortcut(QKeySequence("Shift+F3"), self)
        self._prev_shortcut.activated.connect(self._find_prev)

        from themes.theme_manager import ThemeManager
        self.apply_theme(ThemeManager.colors())

    def apply_theme(self, colors):
        bg = colors.get("editor_bg", "#1e1e1e")
        fg = colors.get("editor_text", "#dcdcdc")
        panel_bg = colors.get("panel_bg", "#2b2b2b")
        border = colors.get("border", "#555555")
        accent = colors.get("accent", "#3d7eff")
        text_sec = colors.get("text_secondary", "#aaaaaa")

        self.setStyleSheet(f"""
            #findReplaceBar {{
                background-color: {panel_bg};
                border-bottom: 1px solid {border};
            }}
            QLineEdit {{
                background-color: {bg};
                color: {fg};
                border: 1px solid {border};
                padding: 3px 6px;
                font-family: Consolas, monospace;
                font-size: 10pt;
            }}
            QToolButton, QPushButton {{
                background-color: {panel_bg};
                color: {fg};
                border: 1px solid {border};
                padding: 3px 8px;
                font-size: 10pt;
            }}
            QToolButton:hover, QPushButton:hover {{
                background-color: {text_sec};
            }}
            QToolButton:pressed, QPushButton:pressed {{
                background-color: {accent};
            }}
            QLabel {{
                color: {text_sec};
                font-size: 10pt;
            }}
            QCheckBox {{
                color: {text_sec};
                font-size: 10pt;
            }}
            QCheckBox::indicator {{
                width: 14px;
                height: 14px;
            }}
        """)

    def editor(self):
        tab = self._tabs.current_tab()
        if tab:
            return tab.editor
        return None

    def _search_flags(self):
        flags = 0
        if self._case_cb.isChecked():
            flags |= 4  # SCFIND_MATCHCASE
        if self._word_cb.isChecked():
            flags |= 2  # SCFIND_WHOLEWORD
        if self._regex_cb.isChecked():
            flags |= 2097152  # SCFIND_REGEXP
        return flags

    def show_bar(self, text=None):
        ed = self.editor()
        if not ed:
            return
        self._current_editor = ed

        if not text and ed.hasSelectedText():
            text = ed.selectedText()
            # Use only first line of selection
            text = text.split("\n")[0].strip()

        if text:
            self._find_input.setText(text)
            self._find_input.selectAll()

        self._find_input.setFocus()
        self._find_input.selectAll()
        self._on_text_changed()
        self.show()
        self.raise_()

    def hide_bar(self):
        self._find_input.clear()
        self._match_label.clear()
        self.hide()
        ed = self.editor()
        if ed:
            ed.cancelFind()
            ed.setFocus()

    def _find_from_start(self, forward=True):
        ed = self.editor()
        if not ed:
            return False
        expr = self._find_input.text()
        if not expr:
            return False
        self._last_expr = expr
        flags = self._search_flags()
        ed.cancelFind()
        return ed.findFirst(
            expr, bool(flags & 2097152), bool(flags & 4),
            bool(flags & 2), True, forward, 0, 0, True
        )

    def _find_next(self):
        ed = self.editor()
        if not ed:
            return
        expr = self._find_input.text()
        if expr != self._last_expr:
            self._find_from_start(True)
        else:
            if not ed.findNext():
                # Wrap around: start from beginning
                self._find_from_start(True)
        self._update_match_count()

    def _find_prev(self):
        ed = self.editor()
        if not ed:
            return
        expr = self._find_input.text()
        if expr != self._last_expr:
            self._find_from_start(False)
        else:
            ed.cancelFind()
            if not ed.findFirst(
                self._find_input.text(),
                self._regex_cb.isChecked(),
                self._case_cb.isChecked(),
                self._word_cb.isChecked(),
                True, False,  # wrap, forward=False
            ):
                # Wrap to end
                ed.cancelFind()
                doc = ed.text()
                ed.findFirst(
                    self._find_input.text(),
                    self._regex_cb.isChecked(),
                    self._case_cb.isChecked(),
                    self._word_cb.isChecked(),
                    True, False, 0, len(doc), True
                )
        self._update_match_count()

    def _replace(self):
        ed = self.editor()
        if not ed or not ed.hasSelectedText():
            self._find_next()
            return
        expr = self._find_input.text()
        if not expr:
            return
        replace_text = self._replace_input.text()
        ed.replace(replace_text)
        self._find_next()
        self._update_match_count()

    def _replace_all(self):
        ed = self.editor()
        if not ed:
            return
        expr = self._find_input.text()
        if not expr:
            return
        replace_text = self._replace_input.text()

        ed.cancelFind()
        flags = self._search_flags()

        # Start from beginning, no wrap — find+replace one at a time
        if not ed.findFirst(
            expr, bool(flags & 2097152), bool(flags & 4),
            bool(flags & 2), False, True, 0, 0, True
        ):
            self._match_label.setText("No results")
            return

        count = 0
        max_count = 100000
        while count < max_count:
            ed.replace(replace_text)
            count += 1
            if not ed.findFirst(
                expr, bool(flags & 2097152), bool(flags & 4),
                bool(flags & 2), False, True, -1, -1, True
            ):
                break

        if count >= max_count:
            self._match_label.setText(f"Replaced {count}+ (limit)")
        else:
            self._match_label.setText(f"Replaced {count}")
        self._debounce.start()

    def _on_text_changed(self):
        self._last_expr = ""
        self._match_label.setText("...")
        self._debounce.start()

    def _do_count(self):
        self._update_match_count()

    def _update_match_count(self):
        if self._count_active:
            return
        self._count_active = True
        ed = self.editor()
        if not ed:
            self._match_label.clear()
            self._count_active = False
            return
        expr = self._find_input.text()
        if not expr:
            self._match_label.clear()
            self._count_active = False
            return

        try:
            flags = self._search_flags()
            pattern = re.escape(expr) if not (flags & 2097152) else expr
            if flags & 2:
                pattern = r'\b' + pattern + r'\b'
            re_flags = 0 if (flags & 4) else re.IGNORECASE
            count = len(re.findall(pattern, ed.text(), re_flags))
            if count > 0:
                self._match_label.setText(f"1/{count}")
            else:
                self._match_label.setText("No results")
        except Exception:
            self._match_label.setText("Error")
        self._count_active = False
