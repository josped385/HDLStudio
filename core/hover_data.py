import os

from core.hdl_parser import HDLParser
from core.keyword_docs import get_doc


def _file_lang(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext in (".v", ".sv", ".vh"):
        return "verilog"
    if ext in (".vhd", ".vhdl"):
        return "vhdl"
    return None


class HoverDatabase:

    def __init__(self):
        self._entries = {}

    def add_file(self, filepath):
        try:
            lang = _file_lang(filepath)
            if not lang:
                return

            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            data = HDLParser.parse_hover_data(content, lang)
            entry = {"file": filepath, "items": data}
            self._entries[filepath] = entry
        except Exception:
            pass

    def remove_file(self, filepath):
        self._entries.pop(filepath, None)

    def clear(self):
        self._entries.clear()

    def find_definition(self, name):
        for entry in self._entries.values():
            item = entry["items"].get(name)
            if item and item.get("kind") in ("module", "entity"):
                return entry["file"], item.get("line", 1)
        return None

    def lookup(self, name, language=None):
        results = []

        for entry in self._entries.values():
            item = entry["items"].get(name)
            if item:
                line = item.get("line")
                loc = f"  -- {os.path.basename(entry['file'])}" + (f":{line}" if line else "")
                results.append((item["kind"], item["detail"], loc))

        if not results and language:
            doc = get_doc(name, language)
            if doc:
                kind, description, url = doc
                results.append((kind, description, f"  {url}"))

        if not results:
            return None

        if len(results) == 1:
            kind, desc, loc = results[0]
            if kind in ("keyword", "directive", "sysfunc", "function", "type", "attribute"):
                return f"{desc}\n{loc}"
            return f"{desc}\n{loc}"

        parts = []
        for kind, d, l in results:
            parts.append(f"{d}\n{l}")
        return "\n\n".join(parts)
