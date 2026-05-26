from PyQt6.QtGui import QColor
from PyQt6.Qsci import (
    QsciLexerCPP,
    QsciScintilla,
)
from PyQt6.QtWidgets import QApplication


class CodeEditor(QsciScintilla):

    def __init__(self):
        super().__init__()

        self._setup_editor()
        self._setup_lexer()

    def _setup_editor(self):

        # Font
        #font = QFont("Courier New", 12)

        #self.setFont(font)

        # UTF8
        self.setUtf8(True)

        # Line numbers
        self.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.setMarginWidth(0, "00000")

        # Colores
        self.setMarginsBackgroundColor(QColor("#2b2b2b"))
        self.setMarginsForegroundColor(QColor("#aaaaaa"))

        # Current line
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#2f2f2f"))

        # Cursor
        self.setCaretForegroundColor(QColor("#ffffff"))

        # Indentation
        self.setIndentationsUseTabs(False)
        self.setIndentationWidth(4)
        self.setAutoIndent(True)

        # Folding
        self.setFolding(
            QsciScintilla.FoldStyle.BoxedTreeFoldStyle
        )

        # Brace matching
        self.setBraceMatching(
            QsciScintilla.BraceMatch.StrictBraceMatch
        )

        # Tabs
        self.setTabWidth(4)

        # Selection colors
        self.setSelectionBackgroundColor(
            QColor("#264f78")
        )

        # Background
        self.setPaper(QColor("#1e1e1e"))

        # Text color
        self.setColor(QColor("#dcdcdc"))

        # Autocomplete
        self.setAutoCompletionSource(
            QsciScintilla.AutoCompletionSource.AcsAll
        )

        self.setAutoCompletionThreshold(1)

        self.setEdgeMode(
            QsciScintilla.EdgeMode.EdgeLine
        )

        self.setEdgeColumn(100)

        self.setEdgeColor(QColor("#333333"))

    def _setup_lexer(self):
        lexer = QsciLexerCPP()

        # Fuente del sistema
        font = QApplication.font()

        # FORZAR fuente global del lexer
        lexer.setDefaultFont(font)

        # IMPORTANTÍSIMO: forzar todos los estilos
        for i in range(128):
            lexer.setFont(font, i)

        lexer.setDefaultPaper(QColor("#1e1e1e"))
        lexer.setDefaultColor(QColor("#dcdcdc"))

        self.setLexer(lexer)