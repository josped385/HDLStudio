import os
import datetime
from PyQt6.QtCore import QProcess, Qt, QTimer
from PyQt6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QTabWidget
)


class BottomPanel(QDockWidget):

    def __init__(self, parent=None):
        super().__init__("Output", parent)
        self.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)

        self._process = None
        self._history = []
        self._log_path = None

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tabs = QTabWidget()

        # ── Console tab ──────────────────────────────────
        self.console = QTextEdit()
        self.console.setReadOnly(True)
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

        self.terminal_out.append("HDLStudio terminal initialized\n")

    # ── public helpers ────────────────────────────────

    def clear(self):
        self.console.clear()
        self.terminal_out.clear()

    def clear_console(self):
        self.console.clear()

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

    # ── theme ─────────────────────────────────────────

    def apply_theme(self, colors):
        css_console = f"""
            background-color: {colors["terminal_bg"]};
            color: {colors["terminal_text"]};
            border: none;
        """
        self.console.setStyleSheet(css_console)
        self.terminal_out.setStyleSheet(css_console)
        self.log_output.setStyleSheet(css_console)
        self.history_output.setStyleSheet(css_console)
        self.terminal_in.setStyleSheet(f"""
            background-color: {colors["panel_bg"]};
            color: {colors["text"]};
            border: 1px solid {colors["panel_hover"]};
            padding: 4px;
        """)

    # ── terminal command execution ────────────────────

    def _execute_command(self):
        cmd = self.terminal_in.text().strip()
        if not cmd:
            return
        self.terminal_out.append(f"> {cmd}\n")
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
        self.terminal_out.append(data)

    def _read_stderr(self):
        data = self._process.readAllStandardError().data().decode(errors="replace")
        self.terminal_out.append(f"[ERR] {data}")

    def _on_finished(self, exit_code, exit_status):
        if exit_code != 0:
            self.terminal_out.append(f"\nProcess exited with code {exit_code}\n")
        else:
            self.terminal_out.append("\n")
