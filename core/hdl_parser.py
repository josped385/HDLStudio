import re


class Signal:
    def __init__(self, name, direction, signal_type, width=None):
        self.name = name
        self.direction = direction
        self.signal_type = signal_type
        self.width = width

    def __repr__(self):
        w = f" [{self.width}]" if self.width else ""
        return f"{self.direction}: {self.name} ({self.signal_type}{w})"


class HDLParser:

    @staticmethod
    def parse(filepath):
        if not filepath:
            return {}
        if not isinstance(filepath, str):
            filepath = str(filepath)
        ext = "." + filepath.rsplit(".", 1)[-1].lower() if "." in filepath else ""

        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        if ext in (".v", ".sv", ".vh"):
            return HDLParser._parse_verilog(content)
        elif ext in (".vhd", ".vhdl"):
            return HDLParser._parse_vhdl(content)
        return {}

    @staticmethod
    def parse_text(content, language="verilog"):
        if language in ("verilog", "systemverilog"):
            return HDLParser._parse_verilog(content)
        elif language == "vhdl":
            return HDLParser._parse_vhdl(content)
        return {}

    @staticmethod
    def _parse_verilog(content):
        inputs = []
        outputs = []
        inouts = []
        wires = []
        regs = []

        text = re.sub(r"//.*", "", content)
        text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
        text = re.sub(r'"[^"]*"', "", text)

        # Match port declarations: input/output/inout [signed] [range] [type] name
        # Terminated by ; or , or ) or end of line
        port_pattern = re.compile(
            r"(input|output|inout)\s+"
            r"(?:signed\s+)?"
            r"(?:\[([^\]]+)\]\s+)?"
            r"(?:wire|reg|logic|integer|real|time)?\s*"
            r"(?:signed\s+)?"
            r"(?:\[([^\]]+)\]\s+)?"
            r"(\w+(?:\s*,\s*\w+)*)\s*"
            r"(?:[;,)]|(?=\s*\))|$)",
            re.IGNORECASE,
        )

        for match in port_pattern.finditer(text):
            direction = match.group(1).lower()
            width1 = match.group(2)
            width2 = match.group(3)
            names_text = match.group(4)
            width = width1 or width2
            names = [n.strip() for n in names_text.split(",")]

            target = (
                inputs if direction == "input"
                else outputs if direction == "output"
                else inouts
            )
            for name in names:
                target.append(Signal(name, direction, "port", width))

        all_port_names = {s.name for lst in [inputs, outputs, inouts] for s in lst}

        # Match internal wire/reg/logic declarations
        internal_pattern = re.compile(
            r"(wire|reg|logic|integer|real)\s+"
            r"(?:signed\s+)?"
            r"(?:\[([^\]]+)\]\s+)?"
            r"(\w+(?:\s*,\s*\w+)*)\s*;",
            re.IGNORECASE,
        )

        for match in internal_pattern.finditer(text):
            stype = match.group(1).lower()
            width = match.group(2)
            names_text = match.group(3)
            names = [n.strip() for n in names_text.split(",")]

            for name in names:
                if name not in all_port_names:
                    entry = Signal(name, "internal", stype, width)
                    if stype in ("wire", "logic", "integer", "real"):
                        wires.append(entry)
                    elif stype == "reg":
                        regs.append(entry)

        # Extract module name
        module_match = re.search(
            r"^\s*module\s+(\w+)", content, re.MULTILINE | re.IGNORECASE
        )
        module_name = module_match.group(1) if module_match else None

        return {
            "module": module_name,
            "inputs": inputs,
            "outputs": outputs,
            "inouts": inouts,
            "wires": wires,
            "regs": regs,
        }

    @staticmethod
    def parse_hover_data(content, language="verilog"):
        if language in ("verilog", "systemverilog"):
            return HDLParser._hover_verilog(content)
        elif language == "vhdl":
            return HDLParser._hover_vhdl(content)
        return {}

    @staticmethod
    def _hover_verilog(content):
        info = {}

        clean = content
        clean = re.sub(r"//.*", "", clean)
        clean = re.sub(r"/\*.*?\*/", "", clean, flags=re.DOTALL)
        clean = re.sub(r'"[^"]*"', "", clean)

        # Collect all port names from module declarations for exclusion
        port_names = set()
        for m in re.finditer(
            r"module\s+\w+\s*(?:#\s*\((.*?)\))?\s*\(([^)]*)\)\s*;",
            clean, re.DOTALL | re.IGNORECASE,
        ):
            ports_raw = m.group(2) or ""
            for p in re.finditer(
                r"(?:input|output|inout)\s+(?:\w+\s+)*(?:\[([^\]]+)\]\s+)?(\w+)",
                ports_raw, re.IGNORECASE,
            ):
                port_names.add(p.group(2))

        # --- module definitions ---
        for m in re.finditer(
            r"module\s+(\w+)\s*(?:#\s*\((.*?)\))?\s*\(([^)]*)\)\s*;",
            clean, re.DOTALL | re.IGNORECASE,
        ):
            name = m.group(1)
            params_raw = (m.group(2) or "").strip()
            ports_raw = m.group(3) or ""
            line_no = content[:m.start()].count("\n") + 1

            params = []
            for p in re.finditer(
                r"\b(?:parameter|localparam)\s+(?:integer\s+)?(?:signed\s+)?"
                r"(?:\[([^\]]+)\]\s+)?(\w+)\s*=\s*([^,;)\n]+)",
                params_raw, re.IGNORECASE,
            ):
                width = p.group(1) or ""
                pname = p.group(2)
                val = p.group(3).strip()
                param_str = f"    parameter [{width}] {pname} = {val}" if width else f"    parameter {pname} = {val}"
                params.append(param_str)

            ports = []
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
                w = f" [{width}]" if width else ""
                ports.append(f"  {direction} {w} {pname}")

            lines = [f"module {name}"]
            if params:
                lines.append("  # (")
                lines.extend(params)
                lines.append("  )")
            if ports:
                lines.append("  (")
                lines.extend(ports)
                lines.append("  );")
            lines.append(f"endmodule  // {name}")
            module_text = "\n".join(lines)
            info[name] = {"kind": "module", "detail": module_text, "line": line_no}

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
                pname = p.group(4)
                if pname not in info or info[pname]["kind"] == "module":
                    info[pname] = {"kind": "port",
                                    "detail": f"port {pname} of module {name}"}

        # --- parameters / localparams (body-level, not inside module #()) ---
        for m in re.finditer(
            r"\b(?:localparam|parameter)\s+(?:integer\s+)?(?:signed\s+)?"
            r"(?:\[([^\]]+)\]\s+)?(\w+)\s*=\s*([^,;)\n]+)",
            clean, re.IGNORECASE,
        ):
            width = m.group(1) or ""
            pname = m.group(2)
            val = m.group(3).strip()
            w = f" [{width}]" if width else ""
            info[pname] = {"kind": "parameter", "detail": f"parameter{w} {pname} = {val}"}

        # --- wire / reg / logic declarations (skip port names) ---
        declared = set()
        for m in re.finditer(
            r"\b(wire|reg|logic|integer)\s+"
            r"(?:signed\s+)?"
            r"(?:\[([^\]]+)\]\s+)?"
            r"(\w+)",
            clean, re.IGNORECASE,
        ):
            stype = m.group(1).lower()
            width = m.group(2) or ""
            wname = m.group(3)
            if wname in port_names:
                continue
            if wname in declared:
                continue
            declared.add(wname)
            if stype == "integer":
                decl = f"integer {wname}"
            else:
                w = f" [{width}]" if width else ""
                decl = f"{stype}{w} {wname}"
            if wname not in info:
                info[wname] = {"kind": stype, "detail": decl}

        # --- module instantiations ---
        _INST_SKIP = {
            "module", "endmodule", "if", "for", "while", "case",
            "begin", "end", "initial", "always", "assign",
            "input", "output", "inout", "wire", "reg", "logic",
            "integer", "real", "time", "tri", "tri0", "tri1",
            "wand", "wor", "triand", "trior", "trireg", "uwire",
            "localparam", "parameter", "function", "task",
            "generate", "endgenerate", "specify", "endspecify",
            "and", "or", "nand", "nor", "xor", "xnor", "not",
            "buf", "bufif0", "bufif1", "notif0", "notif1",
            "pullup", "pulldown", "cmos", "rcmos", "nmos",
            "pmos", "rnmos", "rpmos", "tran", "rtran",
            "tranif0", "tranif1", "rtranif0", "rtranif1",
        }
        for m in re.finditer(
            r"(\w+)\s+(?:#\s*\(((?:[^()]|\([^()]*\))*)\)\s+)?(\w+)\s*\(([^;]*?)\)\s*;",
            clean, re.DOTALL,
        ):
            mod = m.group(1)
            params_ov = (m.group(2) or "").strip()
            inst = m.group(3)
            if mod.lower() in _INST_SKIP:
                continue
            conns_raw = m.group(4)
            header = f"{mod}"
            if params_ov:
                header += f" #({params_ov})"
            header += f" {inst} ("
            lines = [header]
            for c in re.finditer(r"\.(\w+)\s*\(\s*([^;)]*?)\s*\)", conns_raw):
                port = c.group(1)
                sig = c.group(2).strip()
                lines.append(f"  .{port}( {sig} ),")
            if len(lines) > 1 and lines[-1].endswith(","):
                lines[-1] = lines[-1][:-1]
            lines.append(");")
            info[inst] = {"kind": "instance", "detail": "\n".join(lines)}

        return info

    @staticmethod
    def _hover_vhdl(content):
        info = {}
        clean = re.sub(r"--.*", "", content)
        clean = re.sub(r'"[^"]*"', "", clean)

        # --- entity definitions ---
        em = re.search(r"entity\s+(\w+)\s+is\s+port\s*\((.+?)\)\s*;", clean, re.DOTALL | re.IGNORECASE)
        if em:
            name = em.group(1)
            port_text = em.group(2)
            line_no = content[:em.start()].count("\n") + 1
            ports = []
            for p in re.finditer(
                r"(\w+)\s*:\s*(in|out|inout)\s+(\w+(?:_vector)?)\s*(?:\(([^)]*)\))?\s*;?",
                port_text, re.IGNORECASE,
            ):
                pname = p.group(1)
                direction = p.group(2)
                ptype = p.group(3)
                width = p.group(4) or ""
                w = f" ({width})" if width else ""
                ports.append(f"  {pname} : {direction} {ptype}{w}")
            if ports:
                lines = [f"entity {name} is", "  port (", *ports, "  );", f"end {name};"]
                info[name] = {"kind": "entity", "detail": "\n".join(lines), "line": line_no}

        # --- signal declarations ---
        for m in re.finditer(
            r"signal\s+(\w+)\s*:\s*(\w+(?:_vector)?)\s*(?:\(([^)]*)\))?\s*;",
            clean, re.IGNORECASE,
        ):
            sname = m.group(1)
            stype = m.group(2)
            width = m.group(3) or ""
            w = f" ({width})" if width else ""
            info[sname] = {"kind": "signal", "detail": f"signal {sname} : {stype}{w}"}

        # --- constant declarations ---
        for m in re.finditer(
            r"constant\s+(\w+)\s*:\s*(\w+(?:_vector)?)\s*(?:\(([^)]*)\))?\s*:=\s*([^;]+)",
            clean, re.IGNORECASE,
        ):
            cname = m.group(1)
            ctype = m.group(2)
            width = m.group(3) or ""
            val = m.group(4).strip()
            w = f" ({width})" if width else ""
            info[cname] = {"kind": "constant", "detail": f"constant {cname} : {ctype}{w} := {val}"}

        return info

    @staticmethod
    def _parse_vhdl(content):
        inputs = []
        outputs = []
        inouts = []
        signals = []

        text = re.sub(r"--.*", "", content)

        port_clause = re.search(
            r"port\s*\((.+?)\)\s*;", text, re.DOTALL | re.IGNORECASE
        )
        if port_clause:
            port_text = port_clause.group(1)
            port_pattern = re.compile(
                r"(\w+)\s*:\s*(in|out|inout)\s+"
                r"(?:std_logic(?:_vector)?|bit(?:_vector)?|"
                r"integer|boolean|real|time|signed|unsigned|"
                r"std_ulogic(?:_vector)?)\s*"
                r"(?:\(([^)]*)\))?",
                re.IGNORECASE,
            )
            for match in port_pattern.finditer(port_text):
                name = match.group(1)
                direction = match.group(2).lower()
                port_type = match.group(0).split()[2] if match.group(0) else "std_logic"
                width_info = match.group(3)

                target = (
                    inputs if direction == "in"
                    else outputs if direction == "out"
                    else inouts
                )
                target.append(Signal(name, "port", port_type, width_info))

        all_port_names = {s.name for lst in [inputs, outputs, inouts] for s in lst}

        signal_pattern = re.compile(
            r"signal\s+(\w+)\s*:\s*"
            r"(?:std_logic(?:_vector)?|bit(?:_vector)?|"
            r"integer|boolean|real|time|signed|unsigned|"
            r"std_ulogic(?:_vector)?)\s*"
            r"(?:\(([^)]*)\))?\s*;",
            re.IGNORECASE,
        )

        for match in signal_pattern.finditer(text):
            name = match.group(1)
            width_info = match.group(2)
            if name not in all_port_names:
                sig_type = match.group(0).split(":")[1].strip().split()[0].lower()
                signals.append(Signal(name, "internal", sig_type, width_info))

        entity_match = re.search(
            r"entity\s+(\w+)\s+is", content, re.IGNORECASE
        )
        entity_name = entity_match.group(1) if entity_match else None

        return {
            "module": entity_name,
            "inputs": inputs,
            "outputs": outputs,
            "inouts": inouts,
            "signals": signals,
        }