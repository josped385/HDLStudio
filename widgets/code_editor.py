import os
from PyQt6.QtGui import QColor, QFont
from PyQt6.Qsci import QsciScintilla, QsciLexerVerilog, QsciLexerVHDL
from PyQt6.QtCore import pyqtSignal


class CodeEditor(QsciScintilla):

    cursor_position_changed = pyqtSignal(int, int)

    def __init__(self, path=None):
        super().__init__()

        self._path = path
        self._setup_editor()

        self.cursorPositionChanged.connect(
            self._on_cursor_changed
        )

    def set_file_path(self, path):
        self._path = path
        self._apply_lexer()

    def _apply_lexer(self):

        if not self._path:
            return

        ext = os.path.splitext(self._path)[1].lower()

        if ext in (".v", ".sv", ".vh"):
            lexer = QsciLexerVerilog()
            lexer.setDefaultColor(QColor("#dcdcdc"))
            lexer.setDefaultPaper(QColor("#1e1e1e"))

            lexer.setColor(QColor("#569cd6"), QsciLexerVerilog.Keyword)
            lexer.setColor(QColor("#4ec9b0"), QsciLexerVerilog.Identifier)
            lexer.setColor(QColor("#dcdcaa"), QsciLexerVerilog.Number)
            lexer.setColor(QColor("#6a9955"), QsciLexerVerilog.Comment)
            lexer.setColor(QColor("#6a9955"), QsciLexerVerilog.CommentLine)
            lexer.setColor(QColor("#ce9178"), QsciLexerVerilog.String)
            lexer.setColor(QColor("#c586c0"), QsciLexerVerilog.SystemTask)
            lexer.setColor(QColor("#808080"), QsciLexerVerilog.Preprocessor)

            self.setLexer(lexer)

        elif ext in (".vhd", ".vhdl"):
            lexer = QsciLexerVHDL()
            lexer.setDefaultColor(QColor("#dcdcdc"))
            lexer.setDefaultPaper(QColor("#1e1e1e"))

            lexer.setColor(QColor("#569cd6"), QsciLexerVHDL.Keyword)
            lexer.setColor(QColor("#4ec9b0"), QsciLexerVHDL.Identifier)
            lexer.setColor(QColor("#dcdcaa"), QsciLexerVHDL.Number)
            lexer.setColor(QColor("#6a9955"), QsciLexerVHDL.Comment)
            lexer.setColor(QColor("#6a9955"), QsciLexerVHDL.CommentLine)
            lexer.setColor(QColor("#ce9178"), QsciLexerVHDL.String)
            lexer.setColor(QColor("#c586c0"), QsciLexerVHDL.Standard)
            lexer.setColor(QColor("#569cd6"), QsciLexerVHDL.Attribute)

            self.setLexer(lexer)

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

        self._apply_lexer()

    def _on_cursor_changed(self, line, index):

        self.cursor_position_changed.emit(line + 1, index + 1)