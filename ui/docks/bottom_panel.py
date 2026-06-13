import os
import re
import datetime
from PyQt6.QtCore import QProcess, Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QTextCursor, QColor, QFont
from PyQt6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QTextEdit, QTextBrowser,
    QLineEdit, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView
)


class BottomPanel(QDockWidget):

    error_clicked = pyqtSignal(str, int)  # filepath, lineno

    def __init__(self, parent=None):
        super().__init__("Output", parent)
        self.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)

        self._process = None
        self._history = []
        self._log_path = None
        self._extension_tabs = {}

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tabs = QTabWidget()

        # ── Console tab ──────────────────────────────────
        self.console = QTextBrowser()
        self.console.setReadOnly(True)
        self.console.setOpenExternalLinks(False)
        self.console.setOpenLinks(False)
        self.console.anchorClicked.connect(self._on_console_link)
        self.tabs.addTab(self.console, "Console")

        # ── Terminal tab ─────────────────────────────────
        self.terminal_out = QTextEdit()
        self.terminal_out.setReadOnly(True)
        self.terminal_in = QLineEdit()
        self.terminal_in.setPlaceholderText("Enter command...")
        self.terminal_in.returnPressed.connect(self._execute_command)

        term_widget = QWidget()
        term_layout = QVBoxLayout(term_widget)
        term_layout.setContentsMargins(0, 0, 0, 0)
        term_layout.addWidget(self.terminal_out)
        term_layout.addWidget(self.terminal_in)
        self.tabs.addTab(term_widget, "Terminal")

        # ── Problems tab ─────────────────────────────────
        self.problems_table = QTableWidget(0, 4)
        self.problems_table.setHorizontalHeaderLabels(["Type", "File", "Line", "Message"])
        self.problems_table.horizontalHeader().setStretchLastSection(True)
        self.problems_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.problems_table.verticalHeader().setVisible(False)
        self.problems_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.problems_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.problems_table.setAlternatingRowColors(True)
        self.problems_table.setFont(QFont("Consolas", 10))
        self.problems_table.cellClicked.connect(self._on_problem_clicked)
        self.tabs.addTab(self.problems_table, "Problems")

        # ── Log tab ──────────────────────────────────────
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.tabs.addTab(self.log_output, "Log")

        # ── History tab ──────────────────────────────────
        self.history_output = QTextEdit()
        self.history_output.setReadOnly(True)
        self.tabs.addTab(self.history_output, "History")

        layout.addWidget(self.tabs)
        self.setWidget(container)

        self.terminal_out.append("HDLStudio terminal initialized")

    # ══════════════════════════════════════════════════════
    #  Professional console helpers
    # ══════════════════════════════════════════════════════

    def _html(self, text, color="", bold=False, mono=False):
        parts = []
        if color:
            parts.append(f'<span style="color:{color}">')
        if bold:
            parts.append("<b>")
        if mono:
            parts.append('<span style="font-family:Consolas,monospace">')
        parts.append(text)
        if mono:
            parts.append("</span>")
        if bold:
            parts.append("</b>")
        if color:
            parts.append("</span>")
        return "".join(parts)

    def _append_html(self, html):
        try:
            cursor = self.console.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            cursor.insertHtml(html)
            self.console.setTextCursor(cursor)
            sb = self.console.verticalScrollBar()
            sb.setValue(sb.maximum())
        except Exception as e:
            self.console.append(f"[display error: {e}]")

    def _write_both(self, text):
        """Write plain text to both Console and Log tabs."""
        self._append_html(f"{_escape(text)}<br>")
        self.append_log(text + "\n")

    def write_header(self, title):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        safe_title = _escape(title)
        safe_ts = _escape(ts)
        h = (
            f'<br><span style="color:#888;">{"═" * 50}</span><br>'
            f'<b style="font-size:11pt;">  {safe_title}</b><br>'
            f'<span style="color:#888;">  {safe_ts}</span><br>'
            f'<span style="color:#888;">{"═" * 50}</span><br><br>'
        )
        self._append_html(h)
        self.append_log(f"\n{'=' * 50}\n{title}\n{ts}\n{'=' * 50}\n")

    def write_cmd(self, text):
        self._append_html(
            f'<div style="color:#888;font-family:Consolas,monospace;margin:1px 0;">'
            f'$ {_escape(text)}</div>'
        )
        self.append_log(f"$ {text}\n")

    def write_error(self, text):
        self._append_html(
            f'<div style="color:#f44747;font-weight:bold;margin:2px 0;">'
            f'⏵ {_escape(text)}</div>'
        )
        self.append_log(f"[ERROR] {text}\n")

    def write_warning(self, text):
        self._append_html(
            f'<div style="color:#dcdcaa;font-weight:bold;margin:2px 0;">'
            f'⏵ {_escape(text)}</div>'
        )
        self.append_log(f"[WARN] {text}\n")

    def write_ok(self, text):
        self._append_html(
            f'<div style="color:#4ec9b0;font-weight:bold;margin:2px 0;">'
            f'⏵ {_escape(text)}</div>'
        )
        self.append_log(f"[OK] {text}\n")

    def write_info(self, text):
        self._append_html(
            f'<div style="color:#569cd6;margin:2px 0;">'
            f'⏵ {_escape(text)}</div>'
        )
        self.append_log(f"{text}\n")

    def write_line(self, text, color=None):
        if color:
            self._append_html(
                f'<div style="color:{color};margin:2px 0;">{_escape(text)}</div>'
            )
        else:
            self._append_html(f'<div style="margin:2px 0;">{_escape(text)}</div>')
        self.append_log(f"{text}\n")

    # Pattern: file:line: (error|warning|syntax) [:] message
    _ISSUE_LINE = re.compile(
        r'^(.+?):(\d+):\s+(error|warning|syntax)(?::\s*|\s+)(.*)',
        re.IGNORECASE
    )

    def _add_problem(self, file_path, lineno, issue_type, message):
        """Add a row to the Problems table."""
        row = self.problems_table.rowCount()
        self.problems_table.insertRow(row)

        t = issue_type.lower()
        if t == "syntax":
            t = "error"
            message = "syntax " + message.strip()
        label = "Error" if t == "error" else "Warning"
        color = QColor("#f44747") if t == "error" else QColor("#dcdcaa")

        items = [
            QTableWidgetItem(label),
            QTableWidgetItem(os.path.basename(file_path)),
            QTableWidgetItem(str(lineno)),
            QTableWidgetItem(message.strip()),
        ]
        fg = QColor("#ffffff") if t == "error" else QColor("#000000")
        for item in items:
            item.setForeground(color)

        self.problems_table.setItem(row, 0, items[0])
        self.problems_table.setItem(row, 1, items[1])
        self.problems_table.setItem(row, 2, items[2])
        self.problems_table.setItem(row, 3, items[3])

        # Store file path and line number as hidden data
        self.problems_table.item(row, 1).setData(Qt.ItemDataRole.UserRole, file_path)
        self.problems_table.item(row, 2).setData(Qt.ItemDataRole.UserRole, lineno)

        self.problems_table.resizeColumnsToContents()
        self.tabs.setCurrentWidget(self.problems_table)

    def _on_problem_clicked(self, row, col):
        """Handle click on a problem row."""
        file_item = self.problems_table.item(row, 1)
        line_item = self.problems_table.item(row, 2)
        if file_item and line_item:
            fpath = file_item.data(Qt.ItemDataRole.UserRole)
            lineno = line_item.data(Qt.ItemDataRole.UserRole)
            if fpath and lineno is not None:
                self.error_clicked.emit(fpath, lineno)

    def write_raw(self, text):
        try:
            for line in text.split("\n"):
                if not line:
                    self._append_html("<br>")
                    continue

                m = self._ISSUE_LINE.match(line)
                if m:
                    fpath, lno, typ, msg = m.groups()
                    self._add_problem(fpath, int(lno), typ, msg)
                    self.append_log(f"[{typ.upper()}] {fpath}:{lno} — {msg.strip()}\n")
                else:
                    escaped = _escape(line)
                    self._append_html(
                        f'<div style="font-family:Consolas,monospace;'
                        f'margin:1px 0;">{escaped}</div>'
                    )
        except Exception as e:
            self.console.append(f"[write error: {e}]")

    def clear_console(self):
        self.console.clear()
        self.problems_table.setRowCount(0)

    # ── Error link handling ──────────────────────────────

    def _on_console_link(self, url):
        try:
            path = url.path()
            lineno_str = url.fragment()
            if path and lineno_str:
                lineno = int(lineno_str)
                # Strip leading slash from Windows paths like /C:/...
                if path.startswith("/") and len(path) > 2 and path[2] == ":":
                    path = path[1:]
                self.error_clicked.emit(path, lineno)
        except (ValueError, TypeError):
            pass

    # ── Generic helpers ────────────────────────────────

    def clear(self):
        self.console.clear()
        self.terminal_out.clear()

    def append_history(self, action):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {action}"
        self._history.append(line)
        self.history_output.append(line)

    def _ensure_log_path(self):
        if self._log_path is not None:
            return self._log_path
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
        d = os.path.join(base, ".hdlstudio")
        os.makedirs(d, exist_ok=True)
        self._log_path = os.path.join(d, "project.log")
        return self._log_path

    def append_log(self, text):
        path = self._ensure_log_path()
        try:
            with open(path, "a", encoding="utf-8") as f:
                f.write(text)
        except Exception:
            pass
        self.log_output.append(text)

    def reload_log(self):
        path = self._ensure_log_path()
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.log_output.setPlainText(f.read())
        except Exception:
            pass

    # ── Extension tabs ──────────────────────────────

    def add_extension_tab(self, panel_id, title, widget):
        self._extension_tabs[panel_id] = (title, widget)
        self.tabs.addTab(widget, title)

    def remove_extension_tab(self, panel_id):
        entry = self._extension_tabs.pop(panel_id, None)
        if entry:
            _, widget = entry
            idx = self.tabs.indexOf(widget)
            if idx >= 0:
                self.tabs.removeTab(idx)
            widget.setParent(None)

    # ── theme ─────────────────────────────────────────

    def apply_theme(self, colors):
        css_console = f"""
            background-color: {colors["terminal_bg"]};
            color: {colors["terminal_text"]};
            border: none;
            font-family: Consolas, monospace;
            font-size: 10pt;
            white-space: pre;
        """
        self.console.setStyleSheet(css_console)
        self.terminal_out.setStyleSheet(css_console)
        self.log_output.setStyleSheet(css_console)
        self.history_output.setStyleSheet(css_console)
        self.problems_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {colors["input_bg"]};
                color: {colors["text_primary"]};
                gridline-color: {colors["border"]};
                alternate-background-color: {colors["hover_bg"]};
                font-family: Consolas, monospace;
                font-size: 10pt;
            }}
            QHeaderView::section {{
                background-color: {colors["sidebar_bg"]};
                color: {colors["text_primary"]};
                border: 1px solid {colors["border"]};
                font-weight: bold;
            }}
        """)
        self.terminal_in.setStyleSheet(f"""
            background-color: {colors["panel_bg"]};
            color: {colors["text"]};
            border: 1px solid {colors["panel_hover"]};
            padding: 4px;
            font-family: Consolas, monospace;
        """)

    # ── terminal command execution ────────────────────

    def _execute_command(self):
        cmd = self.terminal_in.text().strip()
        if not cmd:
            return
        self.terminal_out.append(f"> {cmd}")
        self.terminal_in.clear()

        if self._process and self._process.state() == QProcess.ProcessState.Running:
            self._process.kill()
            self._process.waitForFinished(1000)

        self._process = QProcess(self)
        self._process.readyReadStandardOutput.connect(self._read_stdout)
        self._process.readyReadStandardError.connect(self._read_stderr)
        self._process.finished.connect(self._on_finished)

        if os.name == "nt":
            self._process.start("cmd.exe", ["/C", cmd])
        else:
            self._process.start("bash", ["-c", cmd])

    def _read_stdout(self):
        data = self._process.readAllStandardOutput().data().decode(errors="replace")
        self.terminal_out.append(data.rstrip())

    def _read_stderr(self):
        data = self._process.readAllStandardError().data().decode(errors="replace")
        self.terminal_out.append(f"[ERR] {data}".rstrip())

    def _on_finished(self, exit_code, exit_status):
        if exit_code != 0:
            self.terminal_out.append(f"\nProcess exited with code {exit_code}")
        else:
            self.terminal_out.append("")


def _escape(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
