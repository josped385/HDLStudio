import re
from PyQt6.QtGui import QColor, QFont
from PyQt6.Qsci import QsciLexerCustom, QsciAPIs


class Style:
    Default      = 0
    Keyword      = 1
    Type         = 2
    Number       = 3
    Comment      = 4
    CommentBlock = 5
    String       = 6
    Directive    = 7
    Identifier   = 8
    Operator     = 9
    Control      = 10
    Event        = 11


_COLORS_DARK = {
    "default":       "#d4d4d4",
    "keyword":       "#569cd6",
    "type":          "#4ec9b0",
    "number":        "#b5cea8",
    "comment":       "#6a9955",
    "comment_block": "#6a9955",
    "string":        "#ce9178",
    "directive":     "#c586c0",
    "identifier":    "#dcdcaa",
    "operator":      "#d4d4d4",
    "control":       "#c586c0",
    "event":         "#d7ba7d",
}

_COLORS_LIGHT = {
    "default":       "#202020",
    "keyword":       "#0057a0",
    "type":          "#008060",
    "number":        "#098658",
    "comment":       "#408040",
    "comment_block": "#408040",
    "string":        "#a04030",
    "directive":     "#7030a0",
    "identifier":    "#606000",
    "operator":      "#202020",
    "control":       "#7030a0",
    "event":         "#806020",
}


class BaseHDLLexer(QsciLexerCustom):

    STYLE_MAP = {}
    _REGEX = None
    _CTRL   = set()
    _EVENT  = set()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_palette = _COLORS_DARK
        self._setup_styles()
        self._setup_autocompletion()

    def _setup_styles(self):
        mono = QFont("Consolas", 10)

        for style_id, name in self.STYLE_MAP.items():
            self.setColor(QColor(self._current_palette.get(name, "#d4d4d4")), style_id)
            self.setFont(mono, style_id)

        bold = QFont("Consolas", 10)
        bold.setBold(True)
        self.setFont(bold, Style.Keyword)

    def _setup_autocompletion(self):
        api = QsciAPIs(self)
        for word in self._completion_words():
            api.add(word)
        api.prepare()

    def _completion_words(self):
        return []

    def apply_theme(self, colors):
        text = colors.get("text", "#ffffff")
        r = int(text[1:3], 16)
        g = int(text[3:5], 16)
        b = int(text[5:7], 16)
        is_dark = (r + g + b) // 3 > 128
        self._current_palette = _COLORS_DARK if is_dark else _COLORS_LIGHT
        self._setup_styles()

    def language(self):
        return "HDL"

    def description(self, style):
        names = {v: k for k, v in self.STYLE_MAP.items()}
        return names.get(style, f"Style {style}")

    def _token_style(self, kind, word):
        return Style.Default

    def styleText(self, start, end):
        editor = self.editor()
        if not editor:
            return
        text = editor.text()
        n = len(text)
        start = max(0, min(start, n))
        end = max(start, min(end, n))
        if start >= end:
            return

        line_start = text.rfind("\n", 0, start)
        line_start = 0 if line_start == -1 else line_start + 1

        line_end = text.find("\n", end)
        if line_end == -1:
            line_end = n

        full_line = text[line_start:line_end]

        # Build character-level style array for full line context
        char_styles = [Style.Default] * (line_end - line_start)
        if self._REGEX:
            for m in self._REGEX.finditer(full_line):
                kind = m.lastgroup
                token = m.group()
                sid = self._token_style(kind, token)
                for i in range(m.start(), min(m.end(), line_end - line_start)):
                    char_styles[i] = sid

        # Apply contiguous styles for exact range [start, end)
        self.startStyling(start, 0x1f)
        rel_start = start - line_start
        rel_end = min(end, line_end) - line_start
        i = rel_start
        while i < rel_end:
            sid = char_styles[i]
            j = i + 1
            while j < rel_end and char_styles[j] == sid:
                j += 1
            self.setStyling(j - i, sid)
            i = j

    def _tokenize(self, text):
        raise NotImplementedError


# ── Verilog / SystemVerilog ────────────────────────────────

_VLOG_KW = {
    "module", "endmodule", "macromodule",
    "input", "output", "inout",
    "assign", "always", "always_comb", "always_ff", "always_latch",
    "initial", "final",
    "task", "endtask", "function", "endfunction",
    "parameter", "localparam",
    "genvar", "generate", "endgenerate",
    "signed", "unsigned",
    "defparam",
    "automatic", "static",
    "config", "endconfig", "design", "incdir", "instance",
    "libext", "liblist", "library", "libmap",
    "options", "cell", "use",
    "specify", "endspecify",
    "primitive", "endprimitive",
    "pulsestyle_onevent", "pulsestyle_ondetect",
    "showcancelled", "noshowcancelled",
    "assert", "assume", "cover", "property", "endproperty",
    "sequence", "endsequence",
    "rand", "randc", "randcase", "randsequence",
    "constraint", "solve",
    "class", "endclass", "extends", "implements",
    "virtual", "interface", "endinterface", "modport",
    "clocking", "endclocking", "global",
    "program", "endprogram",
    "package", "endpackage",
    "import", "export",
    "this", "super", "new", "null",
    "typedef", "enum", "struct", "union",
    "packed", "tagged",
    "unique", "priority",
    "foreach",
    "inside", "dist",
    "with", "matches",
    "soft",
    "wait_order",
    "default",
}
_VLOG_CTRL = {
    "if", "else", "case", "casex", "casez", "endcase",
    "begin", "end",
    "for", "while", "repeat", "forever",
    "fork", "join", "join_any", "join_none",
    "do", "return", "break", "continue",
    "disable", "force", "release",
    "wait",
}
_VLOG_EVENT = {
    "posedge", "negedge", "edge",
}

_VLOG_TYPES = {
    "wire", "reg", "logic", "integer", "real", "realtime", "time",
    "supply0", "supply1", "tri", "tri0", "tri1",
    "triand", "trior", "trireg",
    "wand", "wor",
    "uwire",
    "bit", "byte", "shortint", "int", "longint",
    "shortreal",
    "string",
    "event",
    "chandle",
    "void",
}

_VLOG_DIRECTIVES = {
    "define", "undef", "include", "ifdef", "ifndef",
    "elsif", "else", "endif", "timescale",
    "default_nettype", "celldefine", "endcelldefine",
    "unconnected_drive", "nounconnected_drive",
    "pragma", "line",
    "begin_keywords", "end_keywords",
    "resetall",
}

_VLOG_OPS = {
    "or", "and", "nand", "nor", "xor", "xnor", "not",
}

_VERILOG_RE = re.compile(
    r'(?P<comment_single>//[^\n]*)'
    r'|(?P<comment_block>/\*[\s\S]*?\*/)'
    r'|(?P<string>"(?:[^"\\]|\\.)*")'
    r'|(?P<directive>`\w+)'
    r'|(?P<number>(?:\d+)?\'[sS]?[dDhHoObB][0-9a-fA-F_xXzZ?]+|\d+\.?\d*)'
    r'|(?P<operator><=|>=|==|!=|===|!==|->|=>|\+\+|--|::|[+\-*/%&|~^<>=!?:;,.()\[\]{}@#$])'
    r'|(?P<identifier>[A-Za-z_]\w*)'
    r'|(?P<whitespace>\s+)'
)


class VerilogLexer(BaseHDLLexer):

    _REGEX = _VERILOG_RE
    _CTRL  = _VLOG_CTRL
    _EVENT = _VLOG_EVENT

    STYLE_MAP = {
        Style.Default:      "default",
        Style.Keyword:      "keyword",
        Style.Type:         "type",
        Style.Number:       "number",
        Style.Comment:      "comment",
        Style.CommentBlock: "comment_block",
        Style.String:       "string",
        Style.Directive:    "directive",
        Style.Identifier:   "identifier",
        Style.Operator:     "operator",
        Style.Control:      "control",
        Style.Event:        "event",
    }

    def language(self):
        return "Verilog"

    def _completion_words(self):
        ws = set(_VLOG_KW) | set(_VLOG_CTRL) | set(_VLOG_TYPES) | _VLOG_OPS
        ws.update(f"`{d}" for d in _VLOG_DIRECTIVES)
        return sorted(ws)

    def _token_style(self, kind, word):
        if kind == "whitespace":
            return Style.Default
        if kind == "comment_single":
            return Style.Comment
        if kind == "comment_block":
            return Style.CommentBlock
        if kind == "string":
            return Style.String
        if kind == "directive":
            return Style.Directive
        if kind == "number":
            return Style.Number
        if kind == "identifier":
            if word in _VLOG_CTRL:
                return Style.Control
            if word in _VLOG_EVENT:
                return Style.Event
            if word in _VLOG_KW:
                return Style.Keyword
            if word in _VLOG_TYPES:
                return Style.Type
            if word in _VLOG_OPS:
                return Style.Operator
            return Style.Identifier
        if kind == "operator":
            return Style.Operator
        return Style.Default


# ── VHDL ───────────────────────────────────────────────────

_VHDL_KW = {
    "entity", "end", "architecture", "of", "is",
    "with",
    "begin", "port", "map", "generic",
    "signal", "variable", "constant",
    "type", "subtype", "function", "procedure",
    "process", "postponed",
    "generate", "block",
    "component", "configuration",
    "package", "body",
    "use", "library",
    "in", "out", "inout", "buffer", "linkage",
    "disconnect", "group",
    "impure", "pure",
    "literal", "new", "null",
    "range", "record", "register", "reject", "report",
    "rol", "ror", "sla", "sli", "sra", "srl",
    "select", "severity", "shared",
    "to", "transport",
    "unaffected", "units", "until",
    "access", "alias", "attribute",
    "delta", "energy", "file", "guarded", "linkage",
    "noise", "procedural", "quantity", "reference",
    "spectrum", "tolerance",
}
_VHDL_CTRL = {
    "if", "then", "else", "elsif",
    "when", "for", "loop", "while",
    "case", "others",
    "return",
    "wait", "until", "on",
    "exit", "next",
    "after", "abs", "mod", "rem",
}
_VHDL_OPS = {
    "and", "or", "nand", "nor", "not", "xnor", "xor",
}

_VHDL_TYPES = {
    "std_logic", "std_ulogic",
    "std_logic_vector", "std_ulogic_vector",
    "signed", "unsigned",
    "bit", "bit_vector",
    "boolean", "integer", "natural", "positive",
    "real",
    "time",
    "character", "string",
    "severity_level",
    "file_open_kind", "file_open_status",
    "line", "text",
    "std_logic_table",
    "boolean_vector", "integer_vector", "real_vector", "time_vector",
}

_VHDL_RE = re.compile(
    r'(?P<comment>--[^\n]*)'
    r'|(?P<string>"(?:[^"\\]|\\.)*")'
    r'|(?P<char_literal>\'\w\')'
    r'|(?P<number>\d+#[0-9a-fA-F_]+#|\d+\.?\d*)'
    r'|(?P<operator><=|>=|==|/=|=>|:=|\*\*|-[+>]|\+\+|--|::|[+\-*/&|~^<>=!?:;,.()\[\]{}@#])'
    r'|(?P<identifier>[A-Za-z_]\w*)'
    r'|(?P<whitespace>\s+)'
)


class VHDLLexer(BaseHDLLexer):

    _REGEX = _VHDL_RE
    _CTRL  = _VHDL_CTRL
    _EVENT = set()

    STYLE_MAP = {
        Style.Default:      "default",
        Style.Keyword:      "keyword",
        Style.Type:         "type",
        Style.Number:       "number",
        Style.String:       "string",
        Style.Identifier:   "identifier",
        Style.Operator:     "operator",
        Style.Control:      "control",
    }

    def language(self):
        return "VHDL"

    def _completion_words(self):
        return sorted(set(_VHDL_KW) | set(_VHDL_CTRL) | set(_VHDL_TYPES) | _VHDL_OPS)

    def _token_style(self, kind, word):
        if kind == "whitespace":
            return Style.Default
        if kind == "comment":
            return Style.Comment
        if kind == "string":
            return Style.String
        if kind == "char_literal":
            return Style.String
        if kind == "number":
            return Style.Number
        if kind == "identifier":
            low = word.lower()
            if low in _VHDL_CTRL:
                return Style.Control
            if low in _VHDL_KW:
                return Style.Keyword
            if low in _VHDL_TYPES:
                return Style.Type
            if low in _VHDL_OPS:
                return Style.Operator
            return Style.Identifier
        if kind == "operator":
            return Style.Operator
        return Style.Default
