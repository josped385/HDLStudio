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

        # UI
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)

        self.output = QTextEdit()
        self.output.setReadOnly(True)

        self.input = QLineEdit()

        self.layout.addWidget(self.output)
        self.layout.addWidget(self.input)

        self.setWidget(self.container)

        # process (SAFE MODE)
        self.process = QProcess(self)

        self.process.readyReadStandardOutput.connect(self.read_stdout)
        self.process.readyReadStandardError.connect(self.read_stderr)

        self.input.returnPressed.connect(self.execute_command)

        self.output.append("HDLStudio terminal initialized (safe mode)\n")

    # ---------------- EXECUTION ----------------

    def execute_command(self):

        cmd = self.input.text().strip()

        if not cmd:
            return

        self.output.append(f"> {cmd}")

        self.input.clear()

        # safer: run detached process per command
        if os.name == "nt":
            self.process.start("cmd.exe", ["/C", cmd])
        else:
            self.process.start("bash", ["-c", cmd])

    # ---------------- OUTPUT ----------------

    def read_stdout(self):

        data = self.process.readAllStandardOutput().data().decode()
        self.output.append(data)

    def read_stderr(self):

        data = self.process.readAllStandardError().data().decode()
        self.output.append(f"[ERR] {data}")