import os
from PyQt6.QtGui import QColor, QFont
from PyQt6.Qsci import QsciScintilla, QsciScintillaBase
from PyQt6.QtCore import pyqtSignal, Qt, QPoint, QTimer
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout

from widgets.lexers import VerilogLexer, VHDLLexer

_VERILOG_KW = frozenset({
    "module", "endmodule", "input", "output", "inout", "wire", "reg", "logic",
    "integer", "real", "time", "parameter", "localparam", "assign", "always",
    "initial", "begin", "end", "if", "else", "case", "endcase", "casex",
    "casez", "for", "while", "repeat", "forever", "function", "endfunction",
    "task", "endtask", "generate", "endgenerate", "genvar", "posedge",
    "negedge", "or", "and", "nand", "nor", "xor", "xnor", "not", "buf",
    "bufif0", "bufif1", "notif0", "notif1", "supply0", "supply1", "tri",
    "tri0", "tri1", "triand", "trior", "trireg", "uwire", "wand", "wor",
    "always_comb", "always_ff", "always_latch", "typedef", "enum", "struct",
    "union", "package", "endpackage", "interface", "endinterface",
    "modport", "clocking", "endclocking", "program", "endprogram",
    "assert", "assume", "cover", "property", "endproperty", "sequence",
    "endsequence", "specify", "endspecify", "pulsestyle_onevent",
    "pulsestyle_ondetect", "showcancelled", "signed", "unsigned",
    "automatic", "fork", "join", "join_any", "join_none",
    "disable", "wait", "event", "deassign", "force", "release",
})

_VHDL_KW = frozenset({
    "entity", "is", "port", "in", "out", "inout", "end", "architecture",
    "of", "begin", "signal", "variable", "constant", "type", "subtype",
    "function", "procedure", "process", "if", "then", "else", "elsif",
    "when", "others", "case", "loop", "for", "while", "generate",
    "component", "map", "generic", "all", "use", "library", "work",
    "ieee", "std", "rising_edge", "falling_edge", "to", "downto",
    "range", "open", "bus", "register", "file", "attribute", "group",
    "impure", "pure", "return", "null", "report", "severity", "note",
    "warning", "error", "failure", "body", "protected", "unprotected",
})

_HDL_TYPES = frozenset({
    "wire", "reg", "logic", "integer", "real", "time", "tri", "tri0",
    "tri1", "triand", "trior", "trireg", "uwire", "wand", "wor",
    "supply0", "supply1", "bit", "byte", "shortint", "int", "longint",
    "shortreal", "string", "chandle", "void", "signed", "unsigned",
    "std_logic", "std_logic_vector", "std_ulogic", "std_ulogic_vector",
    "bit_vector", "boolean", "natural", "positive", "character",
    "signed", "unsigned",
})


def _get_palette():
    from themes.theme_manager import ThemeManager
    colors = ThemeManager.colors()
    text = colors.get("text", "#ffffff")
    r = int(text[1:3], 16)
    g = int(text[3:5], 16)
    b = int(text[5:7], 16)
    is_dark = (r + g + b) // 3 > 128
    from widgets.lexers import _COLORS_DARK, _COLORS_LIGHT
    return _COLORS_DARK if is_dark else _COLORS_LIGHT


def _hover_to_html(text):
    pal = _get_palette()
    kw_color = pal["keyword"]
    type_color = pal["type"]
    num_color = pal["number"]
    str_color = pal["string"]
    url_color = "#6cb6ff"
    comment_color = pal["comment"]

    lines = text.split("\n")
    out_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("http://") or stripped.startswith("https://"):
            out_lines.append(f'<span style="color:{url_color};">{_escape(line)}</span>')
            continue
        tokens = _tokenize_line(line)
        parts = []
        for kind, val in tokens:
            if kind == "keyword":
                parts.append(f'<span style="color:{kw_color};font-weight:bold;">{_escape(val)}</span>')
            elif kind == "type":
                parts.append(f'<span style="color:{type_color};">{_escape(val)}</span>')
            elif kind == "number":
                parts.append(f'<span style="color:{num_color};">{_escape(val)}</span>')
            elif kind == "string":
                parts.append(f'<span style="color:{str_color};">{_escape(val)}</span>')
            elif kind == "comment":
                parts.append(f'<span style="color:{comment_color};">{_escape(val)}</span>')
            else:
                parts.append(_escape(val))
        out_lines.append("".join(parts))
    return "<br>".join(out_lines)


def _escape(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


_TOKEN_RE = None


def _tokenize_line(line):
    global _TOKEN_RE
    if _TOKEN_RE is None:
        _TOKEN_RE = __import__("re").compile(
            r'//[^\n]*|"[^"]*"|'
            r"\b\d+(?:'[ bodh]\s*[0-9a-fxz_?]+)?\b|"
            r"\b[0-9a-fxz_]*'[ bodh]\s*[0-9a-fxz_?]+\b|"
            r"\b[a-zA-Z_`$][\w$]*\b|"
            r"\S"
        )
    pos = 0
    tokens = []
    for m in _TOKEN_RE.finditer(line):
        val = m.group(0)
        start, end = m.start(), m.end()
        if pos < start:
            tokens.append(("text", line[pos:start]))
        lower = val.lower()
        if val.startswith("//"):
            tokens.append(("comment", val))
        elif val.startswith('"'):
            tokens.append(("string", val))
        elif val[0].isdigit() or (len(val) > 1 and val[0] in "xz?" and val[1] in "'bodh"):
            tokens.append(("number", val))
        elif val.startswith("`"):
            tokens.append(("directive", val))
        elif lower in _VERILOG_KW or lower in _VHDL_KW or lower in (
            "and", "or", "nand", "nor", "xor", "xnor", "not",
        ):
            tokens.append(("keyword", val))
        elif lower in _HDL_TYPES:
            tokens.append(("type", val))
        else:
            tokens.append(("text", val))
        pos = end
    if pos < len(line):
        tokens.append(("text", line[pos:]))
    return tokens


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


class _TooltipPopup(QFrame):

    def __init__(self, parent=None):
        super().__init__(
            parent,
            Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self._label = QLabel(self)
        self._label.setWordWrap(False)
        self._label.setTextFormat(Qt.TextFormat.RichText)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(0)
        layout.addWidget(self._label)
        self.setLayout(layout)

        self._auto_hide = QTimer(self)
        self._auto_hide.setSingleShot(True)
        self._auto_hide.setInterval(8000)
        self._auto_hide.timeout.connect(self.hide)

    def show_tip(self, html, gpos, colors):
        bg = colors.get("editor_bg", "#1e1e1e")
        fg = colors.get("editor_text", "#dcdcdc")
        border = colors.get("border", "#555555")
        font_family = colors.get("font_family", "Consolas")
        font_size = colors.get("font_size", "10pt")
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 4px;
            }}
            QLabel {{
                background-color: transparent;
                color: {fg};
                font-family: {font_family}, Consolas, monospace;
                font-size: {font_size};
            }}
        """)
        self._label.setText(html)
        self.adjustSize()
        screen = self.screen()
        if screen:
            sg = screen.availableGeometry()
            w = self.width()
            h = self.height()
            x = gpos.x() + 12
            y = gpos.y() + 12
            if x + w > sg.right():
                x = gpos.x() - w - 12
            if y + h > sg.bottom():
                y = gpos.y() - h - 12
            self.move(x, y)
        else:
            self.move(gpos.x() + 12, gpos.y() + 12)
        self.show()
        self.raise_()
        self._auto_hide.start()

    def hide_tip(self):
        self._auto_hide.stop()
        self.hide()


class CodeEditor(QsciScintilla):

    cursor_position_changed = pyqtSignal(int, int)

    def __init__(self):
        super().__init__()

        self._lexer = None
        self._theme_applied = False
        self._hover_db = None
        self._hover_language = None
        self._cached_lines = []
        self._cached_margin_w = 0
        self._last_tip_word = None
        self._tip_popup = None

        self._setup_editor()
        self._setup_autocompletion()

        self.setMouseTracking(True)

        self.cursorPositionChanged.connect(
            self._on_cursor_changed
        )
        self.textChanged.connect(self._cache_doc_lines)

    def setText(self, text):
        super().setText(text)
        self._cache_doc_lines()

    def _cache_doc_lines(self):
        self._cached_lines = self.text().split("\n")
        self._cached_margin_w = self.marginWidth(0)

    def set_hover_database(self, db):
        self._hover_db = db

    def _word_at_global(self, gx, gy):
        fm = self.fontMetrics()
        lx = self.mapFromGlobal(QPoint(gx, gy)).x()
        ly = self.mapFromGlobal(QPoint(gx, gy)).y()
        fh = fm.height()
        cw = fm.horizontalAdvance("n")
        margin_w = self._cached_margin_w
        line = ly // fh
        if line < 0 or line >= len(self._cached_lines):
            return None
        col = max(0, (lx - margin_w) // cw)
        text_line = self._cached_lines[line]
        if col >= len(text_line):
            col = len(text_line) - 1
        ident = _get_identifier(text_line, col)
        if ident:
            return ident
        if col > 0:
            ident = _get_identifier(text_line, col - 1)
            if ident:
                return ident
        if col + 1 < len(text_line):
            ident = _get_identifier(text_line, col + 1)
            if ident:
                return ident
        return None

    def _get_or_create_popup(self):
        if self._tip_popup is None:
            self._tip_popup = _TooltipPopup(self)
        return self._tip_popup

    def _show_popup(self, gpos, tip):
        popup = self._get_or_create_popup()
        from themes.theme_manager import ThemeManager
        colors = ThemeManager.colors()
        html = _hover_to_html(tip)
        popup.show_tip(html, gpos, colors)

    def _hide_popup(self):
        if self._tip_popup is not None:
            self._tip_popup.hide_tip()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if not self._hover_db:
            return
        gpos = self.viewport().mapToGlobal(event.position().toPoint())
        word = self._word_at_global(gpos.x(), gpos.y())
        if not word:
            self._last_tip_word = None
            self._hide_popup()
            return
        if word == self._last_tip_word:
            return
        self._last_tip_word = word
        tip = self._hover_db.lookup(word, language=self._hover_language)
        if tip:
            self._show_popup(gpos, tip)
        else:
            self._hide_popup()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._last_tip_word = None
        self._hide_popup()

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
