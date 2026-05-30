import os
from PyQt6.QtGui import QColor, QFont
from PyQt6.Qsci import QsciScintilla, QsciScintillaBase
from PyQt6.QtCore import pyqtSignal, QTimer, Qt
from PyQt6.QtWidgets import QToolTip

from widgets.lexers import VerilogLexer, VHDLLexer


_IDENTIFIER_RE = None


def _get_identifier(text, pos):
    if not text or pos < 0 or pos >= len(text):
        return None
    ch = text[pos]
    if not (ch.isalnum() or ch in ("_", "$", "`")):
        return None
    start = pos
    while start > 0 and (text[start - 1].isalnum() or text[start - 1] in ("_", "$", "`")):
        start -= 1
    end = pos
    while end < len(text) and (text[end].isalnum() or text[end] in ("_", "$", "`")):
        end += 1
    return text[start:end]


class CodeEditor(QsciScintilla):

    cursor_position_changed = pyqtSignal(int, int)

    def __init__(self):
        super().__init__()

        self._lexer = None
        self._theme_applied = False
        self._hover_db = None
        self._hover_language = None
        self._hover_timer = QTimer(self)
        self._hover_timer.setSingleShot(True)
        self._hover_timer.timeout.connect(self._show_hover_tip)
        self._last_hover_word = None
        self._last_hover_pos = None

        self._setup_editor()
        self._setup_autocompletion()
        self._setup_hover()

        self.cursorPositionChanged.connect(
            self._on_cursor_changed
        )

    def set_hover_database(self, db):
        self._hover_db = db

    def _setup_hover(self):
        self.setMouseTracking(True)
        self.SendScintilla(QsciScintillaBase.SCI_SETMOUSEDWELLTIME, 400)

    def showEvent(self, event):
        super().showEvent(event)
        if not self._theme_applied:
            self._theme_applied = True
            self._force_apply_theme()

    def _force_apply_theme(self):
        from themes.theme_manager import ThemeManager
        self._apply_colors_direct(ThemeManager.colors())

    def _apply_colors_direct(self, colors):
        bg = QColor(colors["editor_bg"])
        fg = QColor(colors["editor_text"])
        sel = QColor(colors["editor_selection"])
        line_hl = QColor(colors["editor_line_highlight"])
        margin_bg = QColor(colors["editor_margin_bg"])
        margin_fg = QColor(colors["text_secondary"])
        edge = QColor(colors["editor_edge"])

        if self._lexer:
            self._lexer.apply_theme(colors)
            self.setLexer(self._lexer)

        for style_id in range(33):
            self.SendScintilla(QsciScintillaBase.SCI_STYLESETBACK, style_id, bg)
            self.SendScintilla(QsciScintillaBase.SCI_STYLESETFORE, style_id, fg)

        self.SendScintilla(QsciScintillaBase.SCI_SETSELFORE, 1, sel)
        self.SendScintilla(QsciScintillaBase.SCI_SETSELBACK, 1, sel)
        self.SendScintilla(QsciScintillaBase.SCI_SETCARETFORE, fg)
        self.SendScintilla(QsciScintillaBase.SCI_SETCARETLINEBACK, line_hl)
        self.SendScintilla(QsciScintillaBase.SCI_SETCARETLINEVISIBLE, 1)

        self.SendScintilla(QsciScintillaBase.SCI_STYLESETBACK, 33, margin_bg)
        self.SendScintilla(QsciScintillaBase.SCI_STYLESETFORE, 33, margin_fg)
        self.SendScintilla(QsciScintillaBase.SCI_SETEDGECOLOUR, edge)

        if self._lexer:
            self._lexer.apply_theme(colors)

    def _setup_editor(self):

        self.setUtf8(True)
        self.setFont(QFont("Consolas", 10))
        self.setMarginsFont(QFont("Consolas", 10))

        self.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.setMarginWidth(0, "00000")

        self.setIndentationsUseTabs(False)
        self.setIndentationWidth(4)
        self.setAutoIndent(True)
        self.setTabWidth(4)

        self.setEdgeMode(QsciScintilla.EdgeMode.EdgeLine)
        self.setEdgeColumn(100)
        self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)

        self._force_apply_theme()

    def _setup_autocompletion(self):

        self.setAutoCompletionSource(
            QsciScintilla.AutoCompletionSource.AcsAll
        )
        self.setAutoCompletionThreshold(2)
        self.setAutoCompletionCaseSensitivity(False)
        self.setAutoCompletionReplaceWord(True)

    def apply_theme_from_colors(self, colors=None):

        if colors is None:
            from themes.theme_manager import ThemeManager
            colors = ThemeManager.colors()

        self._apply_colors_direct(colors)

    def set_lexer_for_file(self, filepath):

        self._remove_lexer()

        if not filepath:
            self._hover_language = None
            return

        _, ext = os.path.splitext(filepath)
        ext = ext.lower()

        if ext in (".v", ".sv"):
            self._lexer = VerilogLexer(self)
            self._hover_language = "verilog"
        elif ext == ".vhd":
            self._lexer = VHDLLexer(self)
            self._hover_language = "vhdl"
        else:
            self._hover_language = None
            return

        self._force_apply_theme()

    def _remove_lexer(self):

        if self._lexer is not None:
            self.setLexer(None)
            self._lexer = None

    def _on_cursor_changed(self, line, index):

        self.cursor_position_changed.emit(line + 1, index + 1)

    def _word_at_screen_pos(self, x, y):
        pos = self.SendScintilla(QsciScintillaBase.SCI_POSITIONFROMPOINT, x, y)
        if pos < 0:
            return None, -1
        text = self.text()
        word = _get_identifier(text, pos)
        return word, pos

    def _show_hover_tip(self):
        if not self._hover_db or self._last_hover_word is None:
            return
        tip = self._hover_db.lookup(self._last_hover_word, language=self._hover_language)
        if tip:
            screen_pos = self.mapToGlobal(self._last_hover_pos)
            QToolTip.showText(screen_pos, tip, self)
        else:
            QToolTip.hideText()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if not self._hover_db:
            return
        word, pos = self._word_at_screen_pos(int(event.position().x()),
                                              int(event.position().y()))
        if word and word != self._last_hover_word:
            self._last_hover_word = word
            self._last_hover_pos = event.position().toPoint()
            if self._hover_db.lookup(word, language=self._hover_language):
                self._hover_timer.start(400)
            else:
                self._hover_timer.stop()
                QToolTip.hideText()
        elif not word:
            self._hover_timer.stop()
            self._last_hover_word = None
            QToolTip.hideText()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._hover_timer.stop()
        self._last_hover_word = None
        QToolTip.hideText()
