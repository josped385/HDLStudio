import os
import re


class HierarchyNode:

    def __init__(self, module_name, filepath=None, line_no=None):
        self.module_name = module_name
        self.filepath = filepath
        self.line_no = line_no
        self.ports = []
        self.params = []
        self.instantiations = []
        self.is_top = False

    def add_port(self, direction, name, width="", port_type=""):
        self.ports.append({
            "direction": direction,
            "name": name,
            "width": width,
            "type": port_type,
        })

    def add_param(self, name, value="", width=""):
        self.params.append({"name": name, "value": value, "width": width})

    def add_instantiation(self, module_name, instance_name, line_no=None):
        self.instantiations.append({
            "module": module_name,
            "instance": instance_name,
            "line": line_no,
        })


_INST_SKIP = frozenset({
    "module", "endmodule", "if", "for", "while", "case", "endcase",
    "begin", "end", "initial", "always", "assign",
    "input", "output", "inout", "wire", "reg", "logic",
    "integer", "real", "time", "tri", "tri0", "tri1",
    "wand", "wor", "triand", "trior", "trireg", "uwire",
    "localparam", "parameter", "function", "endfunction",
    "task", "endtask",
    "generate", "endgenerate", "specify", "endspecify",
    "and", "or", "nand", "nor", "xor", "xnor", "not",
    "buf", "bufif0", "bufif1", "notif0", "notif1",
    "pullup", "pulldown", "cmos", "rcmos", "nmos",
    "pmos", "rnmos", "rpmos", "tran", "rtran",
    "tranif0", "tranif1", "rtranif0", "rtranif1",
    "always_comb", "always_ff", "always_latch",
    "assert", "assume", "cover", "property", "sequence",
    "interface", "modport", "clocking",
})


class HierarchyParser:

    @staticmethod
    def from_file(filepath):
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        ext = os.path.splitext(filepath)[1].lower()
        if ext in (".v", ".sv", ".vh"):
            return HierarchyParser.from_verilog(content, filepath)
        elif ext in (".vhd", ".vhdl"):
            return HierarchyParser.from_vhdl(content, filepath)
        return []

    @staticmethod
    def from_verilog(content, filepath=None):
        clean = content
        clean = re.sub(r"//.*", "", clean)
        clean = re.sub(r"/\*.*?\*/", "", clean, flags=re.DOTALL)
        clean = re.sub(r'"[^"]*"', "", clean)

        nodes = {}
        lines = content.split("\n")

        def get_line_no(pos):
            return 1 + content[:pos].count("\n")

        # Find module definitions
        for m in re.finditer(
            r"module\s+(\w+)\s*(?:#\s*\((.*?)\))?\s*\(([^)]*)\)\s*;",
            clean, re.DOTALL | re.IGNORECASE,
        ):
            name = m.group(1)
            params_raw = (m.group(2) or "").strip()
            ports_raw = m.group(3) or ""
            line_no = get_line_no(m.start())

            node = HierarchyNode(name, filepath, line_no)
            nodes[name] = node

            # Parameters
            for p in re.finditer(
                r"\b(?:parameter|localparam)\s+(?:integer\s+)?(?:signed\s+)?"
                r"(?:\[([^\]]+)\]\s+)?(\w+)\s*=\s*([^,;)\n]+)",
                params_raw, re.IGNORECASE,
            ):
                w = p.group(1) or ""
                node.add_param(p.group(2), p.group(3).strip(), w)

            # Ports
            port_names_in_block = set()
            for p in re.finditer(
                r"(input|output|inout)\s+"
                r"(?:wire|reg|logic|integer)?\s*"
                r"(?:signed\s+)?"
                r"(?:\[([^\]]+)\]\s+)?"
                r"(?:wire|reg|logic|integer)?\s*"
                r"(?:signed\s+)?"
                r"(?:\[([^\]]+)\]\s+)?"
                r"(\w+)",
                ports_raw, re.IGNORECASE,
            ):
                direction = p.group(1).lower()
                width = p.group(2) or p.group(3) or ""
                pname = p.group(4)
                port_names_in_block.add(pname)
                node.add_port(direction, pname, width)

            # Detect port direction from compact module style:
            # module name (a, b, y); followed by input/output declarations
            for p in re.finditer(
                r"(input|output|inout)\s+"
                r"(?:wire|reg|logic|integer)?\s*"
                r"(?:signed\s+)?"
                r"(?:\[([^\]]+)\]\s+)?"
                r"(?:wire|reg|logic|integer)?\s*"
                r"(?:signed\s+)?"
                r"(?:\[([^\]]+)\]\s+)?"
                r"(\w+)",
                clean[m.end():m.end()+2000], re.IGNORECASE,
            ):
                direction = p.group(1).lower()
                width = p.group(2) or p.group(3) or ""
                pname = p.group(4)
                if pname not in port_names_in_block:
                    node.add_port(direction, pname, width)

        # Find instantiations within each module
        module_positions = []
        for m in re.finditer(
            r"module\s+\w+", clean, re.IGNORECASE,
        ):
            module_positions.append(m.start())
        module_positions.append(len(clean))

        module_names = list(nodes.keys())
        for idx, mod_name in enumerate(module_names):
            start = module_positions[idx]
            end = module_positions[idx + 1] if idx + 1 < len(module_positions) else len(clean)
            body = clean[start:end]
            node = nodes[mod_name]

            for m2 in re.finditer(
                r"(\w+)\s+(?:#\s*\(((?:[^()]|\([^()]*\))*)\)\s+)?(\w+)\s*\(([^;]*?)\)\s*;",
                body, re.DOTALL,
            ):
                inst_mod = m2.group(1)
                inst_name = m2.group(3)
                if inst_mod.lower() in _INST_SKIP:
                    continue
                if inst_mod == mod_name:
                    continue
                node.add_instantiation(inst_mod, inst_name, get_line_no(m2.start()))

        # Determine top-level: a module that is never instantiated by any other module
        all_instantiated = set()
        for node in nodes.values():
            for inst in node.instantiations:
                all_instantiated.add(inst["module"])
        for name in nodes:
            if name not in all_instantiated:
                nodes[name].is_top = True

        return list(nodes.values())

    @staticmethod
    def from_vhdl(content, filepath=None):
        clean = re.sub(r"--.*", "", content)
        clean = re.sub(r'"[^"]*"', "", clean)

        nodes = {}
        lines = content.split("\n")

        def get_line_no(pos):
            return 1 + content[:pos].count("\n")

        # Entity definitions
        for m in re.finditer(
            r"entity\s+(\w+)\s+is\s+port\s*\((.+?)\)\s*;",
            clean, re.DOTALL | re.IGNORECASE,
        ):
            name = m.group(1)
            port_text = m.group(2)
            line_no = get_line_no(m.start())
            node = HierarchyNode(name, filepath, line_no)
            nodes[name] = node

            for p in re.finditer(
                r"(\w+)\s*:\s*(in|out|inout)\s+(\w+(?:_vector)?)\s*(?:\(([^)]*)\))?\s*;?",
                port_text, re.IGNORECASE,
            ):
                node.add_port(p.group(2).lower(), p.group(1), p.group(4) or "", p.group(3))

        # Architecture bodies
        for m in re.finditer(
            r"architecture\s+\w+\s+of\s+(\w+)\s+is\s*(.*?)\s*begin\s*(.*?)\s*end\s+(?:architecture)?\s*;?",
            clean, re.DOTALL | re.IGNORECASE,
        ):
            arch_entity = m.group(1)
            decl_part = m.group(2) or ""
            body_part = m.group(3) or ""

            # Component instantiations
            for c in re.finditer(
                r"(\w+)\s*:\s*(?:entity\s+\w+\.)?(\w+)\s*(?:generic\s+map\s*\([^)]*\))?\s*port\s*map\s*\(([^)]*)\)\s*;",
                body_part + decl_part, re.DOTALL | re.IGNORECASE,
            ):
                inst_name = c.group(1)
                comp_name = c.group(2)
                if arch_entity in nodes:
                    nodes[arch_entity].add_instantiation(
                        comp_name, inst_name, get_line_no(c.start())
                    )

        # Determine top-level
        all_instantiated = set()
        for node in nodes.values():
            for inst in node.instantiations:
                all_instantiated.add(inst["module"])
        for name in nodes:
            if name not in all_instantiated:
                nodes[name].is_top = True

        return list(nodes.values())

    @staticmethod
    def build_hierarchy(nodes):
        node_map = {n.module_name: n for n in nodes}

        def children_of(name):
            node = node_map.get(name)
            if not node:
                return []
            result = []
            for inst in node.instantiations:
                child = node_map.get(inst["module"])
                result.append({
                    "module": inst["module"],
                    "instance": inst["instance"],
                    "line": inst["line"],
                    "filepath": child.filepath if child else None,
                    "children": children_of(inst["module"]),
                })
            return result

        top_modules = []
        for node in nodes:
            if node.is_top:
                top_modules.append({
                    "module": node.module_name,
                    "instance": "",
                    "line": node.line_no,
                    "filepath": node.filepath,
                    "children": children_of(node.module_name),
                })

        return top_modules

    @staticmethod
    def format_hierarchy(hierarchy, indent=0):
        lines = []
        for entry in hierarchy:
            prefix = "  " * indent
            label = entry["module"]
            if entry["instance"]:
                label += f"  // {entry['instance']}"
            if entry["filepath"]:
                label += f"  [{os.path.basename(entry['filepath'])}]"
            lines.append(prefix + label)
            if entry["children"]:
                lines.extend(HierarchyParser.format_hierarchy(entry["children"], indent + 1))
        return "\n".join(lines)
