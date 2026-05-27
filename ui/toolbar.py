from PyQt6.QtWidgets import QToolBar


class MainToolBar(QToolBar):

    def __init__(self, parent=None):
        super().__init__("Main Toolbar", parent)

        self.setMovable(False)
        self.setIconSize(parent.iconSize())

        self.main = parent
        self._build()

    def _build(self):

        a = self.main.ide_actions

        self.addAction(a.open_project)
        self.addAction(a.new_file)
        self.addAction(a.open_file)

        self.addSeparator()

        self.addAction(a.save)
        self.addAction(a.save_as)

        self.addSeparator()

        self.addAction(a.compile)
        self.addAction(a.run)