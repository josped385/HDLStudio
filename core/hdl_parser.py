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