import os
import re


def _strip_comments(text):
    # Remove line comments (//), block comments (/* */), and VHDL comments (--)
    text = re.sub(r'//.*', '', text)
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    text = re.sub(r'--.*', '', text)
    return text


def parse_verilog_ports(text):
    text = _strip_comments(text)
    m = re.search(
        r'\bmodule\s+(\w+)\s*(?:#\s*\((.*?)\))?\s*\((.*?)\)\s*;',
        text, re.DOTALL | re.IGNORECASE
    )
    if not m:
        return None
    name = m.group(1)
    params_str = m.group(2)
    ports_str = m.group(3)

    parameters = []
    if params_str:
        for p in re.finditer(
            r'(?:parameter\s+)?(\w+)\s*=\s*([^,)]+)',
            params_str
        ):
            parameters.append((p.group(1), p.group(2).strip()))

    ports = []
    # Remove port-to-port connections if any (e.g., .clk(clk))
    ports_str = re.sub(r'\.\w+\s*\(', '', ports_str)
    ports_str = ports_str.replace(')', '')

    # Match individual port declarations
    decl_re = re.compile(
        r'(input|output|inout)\s+'                      # direction
        r'(?:wire|reg|logic|tri|wand|wor|supply0|supply1)?\s*'  # type (opt)
        r'(?:\[([^\]]+)\])?\s*'                           # range (opt)
        r'(\w+)',                                          # name
        re.IGNORECASE
    )
    for dm in decl_re.finditer(ports_str):
        direction = dm.group(1).lower()
        width = dm.group(2) or ""
        port_name = dm.group(3)
        ports.append({
            "name": port_name,
            "direction": direction,
            "width": width,
        })

    # Fallback: parse simple port list if no ANSI declarations
    if not ports:
        for pn in re.finditer(r'(\w+)', ports_str):
            ports.append({
                "name": pn.group(1),
                "direction": "",
                "width": "",
            })

    return {
        "name": name,
        "parameters": parameters,
        "ports": ports,
        "language": "verilog",
    }


def parse_vhdl_ports(text):
    text = _strip_comments(text)
    m = re.search(
        r'\bentity\s+(\w+)\s+is\s+port\s*\((.*?)\)\s*;',
        text, re.DOTALL | re.IGNORECASE
    )
    if not m:
        return None
    name = m.group(1)
    ports_str = m.group(2)

    # Also try generics
    g = re.search(
        r'\bentity\s+(\w+)\s+is\s+generic\s*\((.*?)\)\s*;',
        text, re.DOTALL | re.IGNORECASE
    )
    generics = []
    if g:
        for gen in re.finditer(r'(\w+)\s*:\s*(\w+(?:\s*\([^)]*\))?)\s*(?::=\s*([^;]+))?', g.group(2)):
            generics.append((
                gen.group(1),
                gen.group(2),
                (gen.group(3) or "").strip(),
            ))

    ports = []
    for line in ports_str.split(";"):
        line = line.strip()
        if not line:
            continue
        pm = re.match(
            r'(\w+)\s*:\s*(in|out|inout)\s+(\w+(?:\s*\([^)]*\))?)',
            line, re.IGNORECASE
        )
        if pm:
            direction_map = {"in": "input", "out": "output", "inout": "inout"}
            ports.append({
                "name": pm.group(1),
                "direction": direction_map.get(pm.group(2).lower(), pm.group(2).lower()),
                "width": "",
                "vhdl_type": pm.group(3),
            })

    return {
        "name": name,
        "parameters": generics,
        "ports": ports,
        "language": "vhdl",
    }


def parse_hdl_file(filepath):
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()
    _, ext = os.path.splitext(filepath)
    ext = ext.lower()
    if ext in (".v", ".sv"):
        return parse_verilog_ports(text)
    elif ext in (".vhd", ".vhdl"):
        return parse_vhdl_ports(text)
    return None


# ── Generator ──────────────────────────────────────────────

def _verilog_type_for(direction, width, vhdl_type=None):
    if direction == "output":
        dtype = "reg"
    else:
        dtype = "wire"
    return dtype


def _default_value_for(direction, width):
    if direction == "input":
        if width:
            return f"{{{width.replace('WIDTH','8').split('-')[0]}{'{0}'}}}" if "'" not in width else "{0}"
        return "0"
    return None


def generate_verilog_tb(info):
    name = info["name"]
    ports = info["ports"]
    params = info["parameters"]
    tb_name = f"tb_{name}"

    lines = []
    lines.append(f"`timescale 1ns/1ps")
    lines.append(f"")
    lines.append(f"module {tb_name}();")
    lines.append(f"")

    # Clock signal
    has_clk = any("clk" in p["name"].lower() for p in ports)
    if has_clk:
        lines.append(f"    reg clk;")
    lines.append(f"")

    # Port declarations
    for p in ports:
        dtype = _verilog_type_for(p["direction"], p["width"])
        width = f" [{p['width']}]" if p["width"] else ""
        lines.append(f"    {dtype}{width} {p['name']};")

    lines.append(f"")

    # DUT instantiation
    if params:
        lines.append(f"    {name} #(")
        for i, (pn, pv) in enumerate(params):
            comma = "," if i < len(params) - 1 else ""
            lines.append(f"        .{pn}({pn}){comma}")
        lines.append(f"    ) uut (")
    else:
        lines.append(f"    {name} uut (")

    for i, p in enumerate(ports):
        comma = "," if i < len(ports) - 1 else ""
        lines.append(f"        .{p['name']}({p['name']}){comma}")
    lines.append(f"    );")
    lines.append(f"")

    # Clock generation
    if has_clk:
        lines.append(f"    always #5 clk = ~clk;")
        lines.append(f"")

    # Stimulus
    lines.append(f"    initial begin")
    lines.append(f"        $dumpfile(\"waves.vcd\");")
    lines.append(f"        $dumpvars(0, {tb_name});")
    lines.append(f"")

    # Initialize inputs
    for p in ports:
        if p["direction"] == "input" or p["direction"] == "inout":
            dv = _default_value_for(p["direction"], p["width"])
            if dv is not None:
                lines.append(f"        {p['name']} = {dv};")
    if has_clk:
        lines.append(f"        clk = 0;")

    lines.append(f"        #10;")
    lines.append(f"")

    # Parameterized wait count
    lines.append(f"        // -----------------------------")
    lines.append(f"        //  Insert your test stimuli here")
    lines.append(f"        // -----------------------------")
    lines.append(f"")

    lines.append(f"        #100;")
    lines.append(f"        $finish;")
    lines.append(f"    end")
    lines.append(f"")

    lines.append(f"endmodule")
    return "\n".join(lines)


def generate_vhdl_tb(info):
    name = info["name"]
    ports = info["ports"]
    generics = info["parameters"]
    tb_name = f"tb_{name}"

    has_clk = any("clk" in p["name"].lower() for p in ports)
    clk_period = "10 ns"

    lines = []
    lines.append(f"library ieee;")
    lines.append(f"use ieee.std_logic_1164.all;")
    lines.append(f"")
    lines.append(f"entity {tb_name} is")
    lines.append(f"end entity;")
    lines.append(f"")
    lines.append(f"architecture sim of {tb_name} is")
    lines.append(f"")

    # Component declaration
    lines.append(f"    component {name} is")
    if generics:
        lines.append(f"        generic (")
        for i, (gn, gt, gv) in enumerate(generics):
            comma = "," if i < len(generics) - 1 else ""
            gv_str = f" := {gv}" if gv else ""
            lines.append(f"            {gn} : {gt}{gv_str}{comma}")
        lines.append(f"        );")
    lines.append(f"        port (")
    for i, p in enumerate(ports):
        comma = ";" if i < len(ports) - 1 else ""
        dir_up = p["direction"].upper() if p["direction"] == "inout" else p["direction"].upper()
        lines.append(f"            {p['name']} : {dir_up} {p.get('vhdl_type', 'std_logic')}{comma}")
    lines.append(f"        );")
    lines.append(f"    end component;")
    lines.append(f"")

    # Internal signals
    if has_clk:
        lines.append(f"    signal clk : std_logic := '0';")
    for p in ports:
        sig_type = p.get('vhdl_type', 'std_logic')
        if p["direction"] in ("output", "inout"):
            # signal is driven by DUT → declared as signal in testbench
            lines.append(f"    signal {p['name']} : {sig_type};")
        else:
            lines.append(f"    signal {p['name']} : {sig_type};")
    lines.append(f"")

    # Clock
    if has_clk:
        lines.append(f"    clk <= not clk after {clk_period} / 2;")
        lines.append(f"")

    lines.append(f"begin")
    lines.append(f"")

    # DUT instance
    lines.append(f"    uut : {name}")
    if generics:
        lines.append(f"        generic map (")
        for i, (gn, gt, gv) in enumerate(generics):
            comma = "," if i < len(generics) - 1 else ""
            lines.append(f"            {gn} => {gn}{comma}")
        lines.append(f"        )")
    lines.append(f"        port map (")
    for i, p in enumerate(ports):
        comma = "," if i < len(ports) - 1 else ""
        lines.append(f"            {p['name']} => {p['name']}{comma}")
    lines.append(f"        );")
    lines.append(f"")

    # Stimulus
    lines.append(f"    process begin")
    lines.append(f"        -- Initialize inputs")
    for p in ports:
        if p["direction"] == "input" or p["direction"] == "inout":
            lines.append(f"        {p['name']} <= '0';")
    lines.append(f"        wait for {clk_period};")
    lines.append(f"")
    lines.append(f"        -- -----------------------------")
    lines.append(f"        --  Insert your test stimuli here")
    lines.append(f"        -- -----------------------------")
    lines.append(f"")
    lines.append(f"        wait for 100 ns;")
    lines.append(f"        std.env.finish;")
    lines.append(f"    end process;")
    lines.append(f"")
    lines.append(f"end architecture;")

    return "\n".join(lines)


def generate_testbench(filepath):
    info = parse_hdl_file(filepath)
    if not info:
        return None

    if info["language"] == "verilog":
        code = generate_verilog_tb(info)
    else:
        code = generate_vhdl_tb(info)

    dst_name = f"tb_{info['name']}"
    dst_ext = ".v" if info["language"] == "verilog" else ".vhd"
    dst_file = f"{dst_name}{dst_ext}"

    return dst_file, code
