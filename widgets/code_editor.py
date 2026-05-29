import os
from PyQt6.QtGui import QColor, QFont
from PyQt6.Qsci import QsciScintilla
from PyQt6.QtCore import pyqtSignal

from widgets.lexers import VerilogLexer, VHDLLexer


class CodeEditor(QsciScintilla):

    cursor_position_changed = pyqtSignal(int, int)

    def __init__(self):
        super().__init__()

        self._lexer = None
        self._setup_editor()
        self._setup_autocompletion()

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

    def _setup_autocompletion(self):

        self.setAutoCompletionSource(
            QsciScintilla.AutoCompletionSource.AcsAll
        )
        self.setAutoCompletionThreshold(2)
        self.setAutoCompletionCaseSensitivity(False)
        self.setAutoCompletionReplaceWord(True)

    def set_lexer_for_file(self, filepath):

        self._remove_lexer()

        if not filepath:
            return

        _, ext = os.path.splitext(filepath)
        ext = ext.lower()

        if ext in (".v", ".sv"):
            self._lexer = VerilogLexer(self)
        elif ext == ".vhd":
            self._lexer = VHDLLexer(self)
        else:
            return

        self.setLexer(self._lexer)

    def update_lexer_styles(self):

        self.setPaper(QColor("#1e1e1e"))
        self.setColor(QColor("#dcdcdc"))

        if self._lexer:
            self.setLexer(self._lexer)

    def _remove_lexer(self):

        if self._lexer is not None:
            self.setLexer(None)
            self._lexer = None

    def _on_cursor_changed(self, line, index):

        self.cursor_position_changed.emit(line + 1, index + 1)
