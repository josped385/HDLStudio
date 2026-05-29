import os
from PyQt6.QtCore import QProcess, Qt
from PyQt6.QtWidgets import (
    QDockWidget,
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QLineEdit
)


class TerminalDock(QDockWidget):

    def __init__(self, parent=None):
        super().__init__("Terminal", parent)

        self.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)

        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.output = QTextEdit()
        self.output.setReadOnly(True)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Enter command...")

        self.layout.addWidget(self.output)
        self.layout.addWidget(self.input)

        self.setWidget(self.container)

        self._process = None
        self.input.returnPressed.connect(self.execute_command)

        self.output.append("HDLStudio terminal initialized\n")

    def execute_command(self):

        cmd = self.input.text().strip()

        if not cmd:
            return

        self.output.append(f"> {cmd}\n")
        self.input.clear()

        if self._process and self._process.state() == QProcess.ProcessState.Running:
            self._process.kill()
            self._process.waitForFinished(1000)

        self._process = QProcess(self)
        self._process.readyReadStandardOutput.connect(self.read_stdout)
        self._process.readyReadStandardError.connect(self.read_stderr)
        self._process.finished.connect(self._on_finished)

        if os.name == "nt":
            self._process.start("cmd.exe", ["/C", cmd])
        else:
            self._process.start("bash", ["-c", cmd])

    def read_stdout(self):

        data = self._process.readAllStandardOutput().data().decode(errors="replace")
        self.output.append(data)

    def read_stderr(self):

        data = self._process.readAllStandardError().data().decode(errors="replace")
        self.output.append(f"[ERR] {data}")

    def _on_finished(self, exit_code, exit_status):

        if exit_code != 0:
            self.output.append(f"\nProcess exited with code {exit_code}\n")
        else:
            self.output.append("\n")

    def clear(self):

        self.output.clear()