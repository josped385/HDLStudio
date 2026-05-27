from PyQt6.QtGui import QColor
from PyQt6.Qsci import QsciScintilla


class CodeEditor(QsciScintilla):

    def __init__(self):
        super().__init__()

        self._setup_editor()

    def _setup_editor(self):

        # UTF-8 support
        self.setUtf8(True)

        # Line numbers
        self.setMarginType(
            0,
            QsciScintilla.MarginType.NumberMargin
        )

        self.setMarginWidth(0, "00000")

        # Margin colors
        self.setMarginsBackgroundColor(
            QColor("#2b2b2b")
        )

        self.setMarginsForegroundColor(
            QColor("#aaaaaa")
        )

        # Current line highlight
        self.setCaretLineVisible(True)

        self.setCaretLineBackgroundColor(
            QColor("#2f2f2f")
        )

        # Cursor color
        self.setCaretForegroundColor(
            QColor("#ffffff")
        )

        # Indentation
        self.setIndentationsUseTabs(False)
        self.setIndentationWidth(4)

        # Disable automatic indentation
        self.setAutoIndent(False)

        # Tab width
        self.setTabWidth(4)

        # Selection color
        self.setSelectionBackgroundColor(
            QColor("#264f78")
        )

        # Editor background
        self.setPaper(QColor("#1e1e1e"))

        # Default text color
        self.setColor(QColor("#dcdcdc"))

        # Vertical edge line
        self.setEdgeMode(
            QsciScintilla.EdgeMode.EdgeLine
        )

        self.setEdgeColumn(100)

        self.setEdgeColor(
            QColor("#333333")
        )