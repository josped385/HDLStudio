from PyQt6.QtWidgets import QStatusBar, QLabel


class IDEStatusBar(QStatusBar):

    def __init__(self):
        super().__init__()

        self.file_label = QLabel("No file opened")
        self.position_label = QLabel("Ln 1, Col 1")

        self.addWidget(self.file_label)
        self.addPermanentWidget(self.position_label)