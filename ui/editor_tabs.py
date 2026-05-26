import os

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QTabWidget

from widgets.code_editor import CodeEditor


class EditorTabs(QTabWidget):

    def __init__(self):
        super().__init__()

        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)

        self.tabCloseRequested.connect(
            self.close_tab
        )

        self.open_welcome_tab()

    def open_welcome_tab(self):

        editor = CodeEditor()

        editor.setText(
            "// HDLStudio\n"
            "// Welcome\n"
        )

        self.addTab(
            editor,
            QIcon("assets/icons/file.svg"),
            "welcome.sv"
        )

    def open_file(self, path):

        try:
            with open(path, "r") as file:
                content = file.read()

            editor = CodeEditor()
            editor.setText(content)

            filename = os.path.basename(path)

            self.addTab(
                editor,
                QIcon("assets/icons/file.svg"),
                filename
            )

            self.setCurrentWidget(editor)

        except Exception as error:
            print(error)

    def close_tab(self, index):

        if self.count() > 1:
            self.removeTab(index)