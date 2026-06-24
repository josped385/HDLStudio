import json
import os
import re
import sys
import tempfile
import shutil


# ──────────────────────────────────────────────
# Family definitions
# ──────────────────────────────────────────────

FAMILIES = {
    "ice40": {
        "label": "Lattice iCE40",
        "module": "yowasp_nextpnr_ice40",
        "runner": "run_nextpnr_ice40",
        "output_flag": "--asc",
        "output_ext": ".asc",
        "packer": {
            "module": "yowasp_nextpnr_ice40",
            "runner": "run_icepack",
            "input_flag": None,
            "input_ext": ".asc",
            "output_ext": ".bin",
        },
    },
    "ecp5": {
        "label": "Lattice ECP5",
        "module": "yowasp_nextpnr_ecp5",
        "runner": "run_nextpnr_ecp5",
        "output_flag": "--textcfg",
        "output_ext": ".config",
        "packer": {
            "module": "yowasp_nextpnr_ecp5",
            "runner": "run_ecppack",
            "input_flag": None,
            "input_ext": ".config",
            "output_ext": ".bit",
        },
    },
    "nexus": {
        "label": "Lattice Nexus",
        "module": "yowasp_nextpnr_nexus",
        "runner": "run_nextpnr_nexus",
        "output_flag": "--bit",
        "output_ext": ".bit",
        "packer": None,
    },
    "machxo2": {
        "label": "Lattice MachXO2",
        "module": "yowasp_nextpnr_machxo2",
        "runner": "run_nextpnr_machxo2",
        "output_flag": "--textcfg",
        "output_ext": ".config",
        "packer": {
            "module": "yowasp_nextpnr_machxo2",
            "runner": "run_ecppack",
            "input_flag": None,
            "input_ext": ".config",
            "output_ext": ".bit",
        },
    },
    "gowin": {
        "label": "Gowin (himbaechel)",
        "module": "yowasp_nextpnr_himbaechel_gowin",
        "runner": "run_nextpnr_himbaechel_gowin",
        "output_flag": "--fasm",
        "output_ext": ".fasm",
        "packer": {
            "module": None,
            "runner": "gowin_pack",
            "input_flag": None,
            "input_ext": ".fasm",
            "output_ext": ".fs",
        },
    },
}

# ── iCE40/ECP5 have per-device flags; the rest use --device <name>
_DEVICE_FLAGS = {
    "lp384": "--lp384", "lp1k": "--lp1k", "lp4k": "--lp4k",
    "lp8k": "--lp8k", "hx1k": "--hx1k", "hx4k": "--hx4k",
    "hx8k": "--hx8k", "up3k": "--up3k", "up5k": "--up5k",
    "u1k": "--u1k", "u2k": "--u2k", "u4k": "--u4k",
    "12k": "--12k", "25k": "--25k", "45k": "--45k", "85k": "--85k",
}


# ──────────────────────────────────────────────
# Availability checks
# ──────────────────────────────────────────────

def family_available(family_key):
    info = FAMILIES.get(family_key)
    if not info:
        return False
    try:
        __import__(info["module"])
        return True
    except ImportError:
        return False


def nextpnr_available():
    return family_available("ice40")


def icepack_available():
    try:
        from yowasp_nextpnr_ice40 import run_icepack
        return True
    except ImportError:
        return False


# ──────────────────────────────────────────────
# Report parsing (shared across families)
# ──────────────────────────────────────────────

def _parse_pnr_report(report_path):
    try:
        with open(report_path) as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return None

    info = {}
    if "device" in data:
        info["device"] = str(data["device"])
    if "timing" in data:
        t = data["timing"]
        for k in ("worst_slack", "best_slack", "fmax", "total_negative_slack"):
            if k in t and t[k] is not None:
                info[k] = t[k]
    if "utilization" in data:
        u = data["utilization"]
        for key in ("LUT", "DFF", "CARRY", "BRAM", "IO", "PLL", "WARMBOOT"):
            if key in u and u[key] is not None:
                info[key.lower()] = u[key]
    return info if info else {"note": "Report empty"}


def _parse_pnr_log(log_text):
    info = {}
    for line in log_text.splitlines():
        m = re.search(r'Info: Device utilisation:\s*$', line)
        if m:
            continue
        # Generic resource usage: "TYPE: used/total  pct%"
        m = re.search(r'(\w[\w_]*)\s*:\s+(\d+)\s*/\s*(\d+)', line)
        if m:
            name, used, total = m.group(1), int(m.group(2)), int(m.group(3))
            key = name.lower().replace(" ", "_")
            info[f"{key}_used"] = used
            info[f"{key}_total"] = total
        # iCE40-specific delay line
        m = re.search(r'([\d.]+)\s*ns\s+logic,\s*([\d.]+)\s*ns\s+routing', line)
        if m:
            info["logic_delay_ns"] = float(m.group(1))
            info["routing_delay_ns"] = float(m.group(2))
            info["total_delay_ns"] = round(float(m.group(1)) + float(m.group(2)), 2)
        if "No Fmax available" in line:
            info["fmax"] = "N/A"
    return info if info else {"note": "Could not parse log"}


def _format_pnr_summary(info):
    if not info:
        return []
    lines = []
    if "device" in info:
        lines.append(f"Device: {info['device']}")
    lines.append("")
    timing_block = False
    for key, label in [("worst_slack", "Worst slack"),
                        ("best_slack", "Best slack"),
                        ("fmax", "Fmax (MHz)"),
                        ("total_negative_slack", "TNS"),
                        ("logic_delay_ns", "Logic delay (ns)"),
                        ("routing_delay_ns", "Routing delay (ns)"),
                        ("total_delay_ns", "Total delay (ns)")]:
        v = info.get(key)
        if v is not None and v != "N/A":
            if not timing_block:
                lines.append("── Timing ──")
                timing_block = True
            lines.append(f"  {label}: {v}")
        elif v == "N/A" and key == "fmax":
            if not timing_block:
                lines.append("── Timing ──")
                timing_block = True
            lines.append("  Fmax: N/A (no interior timing paths)")
    lines.append("")
    res_block = False
    for key, label in [("luts", "LUTs"),
                        ("bram", "BRAM blocks"),
                        ("io", "IO pins"),
                        ("pll", "PLLs"),
                        ("warmboot", "Warmboot"),
                        ("global_buffers", "Global buffers"),
                        ("ffs", "FFs")]:
        v = info.get(key)
        used = info.get(f"{key}_used")
        total = info.get(f"{key}_total")
        if v is not None:
            if not res_block:
                lines.append("── Resource Usage ──")
                res_block = True
            lines.append(f"  {label}: {v}")
        elif used is not None:
            if not res_block:
                lines.append("── Resource Usage ──")
                res_block = True
            total_str = f"/{total}" if total is not None else ""
            lines.append(f"  {label}: {used}{total_str}")
    if "note" in info:
        lines.append(f"\n  Note: {info['note']}")
    return lines


# ──────────────────────────────────────────────
# Tool runner helpers
# ──────────────────────────────────────────────

def _import_runner(family_key):
    info = FAMILIES[family_key]
    mod = __import__(info["module"], fromlist=[info["runner"]])
    return getattr(mod, info["runner"])


def _build_args(family_key, src_name, output_name, log_name, report_name,
                device, package, frequency):
    info = FAMILIES[family_key]
    args = ["--json", src_name, info["output_flag"], output_name,
            "--log", log_name, "--report", report_name]

    dev_lower = device.lower()
    if dev_lower in _DEVICE_FLAGS:
        args.append(_DEVICE_FLAGS[dev_lower])
    else:
        args.extend(["--device", device])

    if package:
        args.extend(["--package", package])
    if frequency:
        args.extend(["--freq", str(frequency)])
    return args


def _run_packer(packer_info, terminal_callback, input_path, output_path,
                device=None):
    """Run the bitstream packer (icepack, ecppack, gowin_pack, etc.)."""
    runner = packer_info["runner"]
    module_name = packer_info["module"]

    if runner == "gowin_pack":
        from apycula import gowin_pack
        if device is None:
            device = "auto"
        tmp = tempfile.mkdtemp(prefix="gowinpack_")
        try:
            in_copy = os.path.join(tmp, "input.fasm")
            out_name = os.path.basename(output_path)
            shutil.copy2(input_path, in_copy)
            old_argv = sys.argv
            sys.argv = ["gowin_pack", "-d", device, "-o", out_name, in_copy]
            try:
                gowin_pack.main()
            except SystemExit:
                pass
            sys.argv = old_argv
            out_file = os.path.join(tmp, out_name)
            if os.path.isfile(out_file):
                os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
                shutil.copy2(out_file, output_path)
                terminal_callback(f"Bitstream generated -> {output_path}\n")
                return output_path
            terminal_callback("gowin_pack did not produce output.\n")
            return None
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    else:
        # Standard yowasp packer (icepack, ecppack, etc.)
        try:
            mod = __import__(module_name, fromlist=[runner])
            run_fn = getattr(mod, runner)
        except ImportError:
            terminal_callback(f"{runner} not available.\n")
            return None

        work_dir = tempfile.mkdtemp(prefix="pack_")
        try:
            in_name = "input" + packer_info["input_ext"]
            out_name = os.path.basename(output_path)
            shutil.copy2(input_path, os.path.join(work_dir, in_name))
            orig_cwd = os.getcwd()
            os.chdir(work_dir)
            try:
                run_fn([in_name, out_name])
            except SystemExit:
                pass
            except Exception as e:
                terminal_callback(f"{runner} error: {e}\n")
                os.chdir(orig_cwd)
                return None
            os.chdir(orig_cwd)
            out_file = os.path.join(work_dir, out_name)
            if os.path.isfile(out_file):
                os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
                shutil.copy2(out_file, output_path)
                terminal_callback(f"Bitstream generated -> {output_path}\n")
                return output_path
            terminal_callback(f"{runner} did not produce output.\n")
            return None
        finally:
            os.chdir(orig_cwd)
            shutil.rmtree(work_dir, ignore_errors=True)


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────

def run_pnr(terminal_callback, family_key, json_path, output_path=None,
            device="hx1k", package=None, frequency=None):
    info = FAMILIES.get(family_key)
    if not info:
        terminal_callback(f"Unknown FPGA family: {family_key}\n")
        return None, None

    if not family_available(family_key):
        terminal_callback(
            f"{info['label']} package ({info['module']}) not installed.\n"
            f"Run: pip install {info['module']}\n"
        )
        return None, None

    if not os.path.isfile(json_path):
        terminal_callback(f"JSON file not found: {json_path}\n")
        return None, None

    run_fn = _import_runner(family_key)

    src_name = os.path.basename(json_path)
    base = os.path.splitext(src_name)[0]

    if output_path is None:
        output_path = os.path.join(os.path.dirname(json_path),
                                   f"{base}{info['output_ext']}")

    work_dir = tempfile.mkdtemp(prefix="pnr_")
    try:
        shutil.copy2(json_path, os.path.join(work_dir, src_name))
        orig_cwd = os.getcwd()
        os.chdir(work_dir)

        out_name = os.path.basename(output_path)
        log_name = f"{base}.log"
        report_name = f"{base}_report.json"

        args = _build_args(family_key, src_name, out_name, log_name,
                           report_name, device, package, frequency)

        terminal_callback(
            f"Running {info['module']} on {src_name}...\n"
            f"  Device: {device}"
        )
        if package:
            terminal_callback(f", Package: {package}")
        if frequency:
            terminal_callback(f", Freq: {frequency} MHz")
        terminal_callback("\n\n")

        try:
            run_fn(args)
        except SystemExit:
            pass
        except Exception as e:
            terminal_callback(f"nextpnr error: {e}\n")
            os.chdir(orig_cwd)
            return None, None

        os.chdir(orig_cwd)

        # Read and forward the log
        log_path = os.path.join(work_dir, log_name)
        log_text = ""
        if os.path.isfile(log_path):
            with open(log_path, encoding="utf-8", errors="replace") as f:
                log_text = f.read()
            terminal_callback(log_text)
        else:
            terminal_callback("(no log file produced)\n")

        # Parse JSON report
        report_info = None
        report_path = os.path.join(work_dir, report_name)
        if os.path.isfile(report_path):
            report_info = _parse_pnr_report(report_path)

        if not report_info or "note" in report_info:
            if log_text:
                log_info = _parse_pnr_log(log_text)
                if log_info and "note" not in log_info:
                    report_info = log_info

        # Show summary
        summary = _format_pnr_summary(report_info)
        if summary:
            terminal_callback("\n" + "─" * 40 + "\n")
            for line in summary:
                terminal_callback(line + "\n")
            terminal_callback("─" * 40 + "\n")

        # Copy result
        out_file = os.path.join(work_dir, out_name)
        if os.path.isfile(out_file):
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            shutil.copy2(out_file, output_path)
            terminal_callback(f"\nPlace & Route complete -> {output_path}\n")
            return output_path, report_info
        else:
            terminal_callback(f"\nnextpnr did not produce an output file.\n")
            for f in os.listdir(work_dir):
                if f not in (src_name, log_name):
                    terminal_callback(f"  Output: {f}\n")
            return None, None
    finally:
        os.chdir(orig_cwd)
        shutil.rmtree(work_dir, ignore_errors=True)


def pack_bitstream(terminal_callback, family_key, input_path, output_path=None,
                   device=None):
    info = FAMILIES.get(family_key)
    if not info:
        terminal_callback(f"Unknown FPGA family: {family_key}\n")
        return None

    packer = info.get("packer")
    if not packer:
        terminal_callback(f"{info['label']} has no separate bitstream pack step.\n")
        return None

    if not os.path.isfile(input_path):
        terminal_callback(f"Input file not found: {input_path}\n")
        return None

    if output_path is None:
        base = os.path.splitext(input_path)[0]
        output_path = f"{base}{packer['output_ext']}"

    terminal_callback(f"Packing bitstream...\n")
    return _run_packer(packer, terminal_callback, input_path, output_path, device)


# ── Backward compatibility shims ──

def run_pnr_legacy(terminal_callback, json_path, asc_path=None,
                   device="hx1k", package=None, frequency=None):
    return run_pnr(terminal_callback, "ice40", json_path, asc_path,
                   device, package, frequency)


def run_icepack(terminal_callback, asc_path, bin_path=None):
    return pack_bitstream(terminal_callback, "ice40", asc_path, bin_path)
