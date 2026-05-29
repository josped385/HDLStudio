from PyQt6.QtGui import QColor, QFont
from PyQt6.Qsci import QsciScintilla
from PyQt6.QtCore import pyqtSignal


class CodeEditor(QsciScintilla):

    cursor_position_changed = pyqtSignal(int, int)

    def __init__(self):
        super().__init__()

        self._setup_editor()

        self.cursorPositionChanged.connect(
            self._on_cursor_changed
        )

    def _setup_editor(self):

        self.setUtf8(True)

        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        self.setMarginsFont(font)

        self.setMarginType(
            0,
            QsciScintilla.MarginType.NumberMargin
        )

        self.setMarginWidth(0, "00000")

        self.setMarginsBackgroundColor(QColor("#2b2b2b"))
        self.setMarginsForegroundColor(QColor("#aaaaaa"))

        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#2f2f2f"))

        self.setCaretForegroundColor(QColor("#ffffff"))

        self.setIndentationsUseTabs(False)
        self.setIndentationWidth(4)
        self.setAutoIndent(True)
        self.setTabWidth(4)

        self.setSelectionBackgroundColor(QColor("#264f78"))

        self.setPaper(QColor("#1e1e1e"))
        self.setColor(QColor("#dcdcdc"))

        self.setEdgeMode(QsciScintilla.EdgeMode.EdgeLine)
        self.setEdgeColumn(100)
        self.setEdgeColor(QColor("#333333"))

        self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)

    def _on_cursor_changed(self, line, index):

        self.cursor_position_changed.emit(line + 1, index + 1)