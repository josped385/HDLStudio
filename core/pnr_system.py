import json
import os
import re
import tempfile
import shutil


def nextpnr_available():
    try:
        from yowasp_nextpnr_ice40 import run_nextpnr_ice40
        return True
    except ImportError:
        return False


def icepack_available():
    try:
        from yowasp_nextpnr_ice40 import run_icepack
        return True
    except ImportError:
        return False


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
        # "ICESTORM_LC: 3/ 1280 0%"
        m = re.search(r'(ICESTORM_LC|ICESTORM_RAM|SB_IO|SB_GB|ICESTORM_PLL|SB_WARMBOOT):\s+(\d+)\s*/\s*(\d+)', line)
        if m:
            name, used, total = m.group(1), int(m.group(2)), int(m.group(3))
            label_map = {
                "ICESTORM_LC": "luts",
                "ICESTORM_RAM": "bram",
                "SB_IO": "io",
                "SB_GB": "global_buffers",
                "ICESTORM_PLL": "pll",
                "SB_WARMBOOT": "warmboot",
            }
            key = label_map.get(name, name.lower())
            info[f"{key}_used"] = used
            info[f"{key}_total"] = total

        # "0.38 ns logic, 1.18 ns routing"
        m = re.search(r'([\d.]+)\s*ns\s+logic,\s*([\d.]+)\s*ns\s+routing', line)
        if m:
            info["logic_delay_ns"] = float(m.group(1))
            info["routing_delay_ns"] = float(m.group(2))
            info["total_delay_ns"] = round(float(m.group(1)) + float(m.group(2)), 2)

        # "No Fmax available; no interior timing paths found"
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
    for key, label in [("luts", "LUTs (LCs)"),
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


def run_pnr(terminal_callback, json_path, asc_path=None,
            device="hx1k", package=None, frequency=None):
    if not nextpnr_available():
        terminal_callback(
            "yowasp-nextpnr-ice40 not installed.\n"
            "Run: pip install yowasp-nextpnr-ice40\n"
        )
        return None, None

    if not os.path.isfile(json_path):
        terminal_callback(f"JSON file not found: {json_path}\n")
        return None, None

    from yowasp_nextpnr_ice40 import run_nextpnr_ice40

    src_name = os.path.basename(json_path)
    base = os.path.splitext(src_name)[0]

    if asc_path is None:
        asc_path = os.path.join(os.path.dirname(json_path), f"{base}.asc")

    work_dir = tempfile.mkdtemp(prefix="pnr_")
    try:
        shutil.copy2(json_path, os.path.join(work_dir, src_name))
        orig_cwd = os.getcwd()
        os.chdir(work_dir)

        asc_name = os.path.basename(asc_path)
        log_name = f"{base}.log"
        report_name = f"{base}_report.json"

        args = [
            "--json", src_name,
            "--asc", asc_name,
            "--log", log_name,
            "--report", report_name,
        ]

        device_args = {
            "lp384": "--lp384", "lp1k": "--lp1k", "lp4k": "--lp4k",
            "lp8k": "--lp8k", "hx1k": "--hx1k", "hx4k": "--hx4k",
            "hx8k": "--hx8k", "up3k": "--up3k", "up5k": "--up5k",
            "u1k": "--u1k", "u2k": "--u2k", "u4k": "--u4k",
        }
        dev = device.lower()
        if dev in device_args:
            args.append(device_args[dev])
        else:
            args.append(f"--{dev}")

        if package:
            args.extend(["--package", package])
        if frequency:
            args.extend(["--freq", str(frequency)])

        terminal_callback(
            f"Running nextpnr-ice40 on {src_name}...\n"
            f"  Device: {device}"
        )
        if package:
            terminal_callback(f", Package: {package}")
        if frequency:
            terminal_callback(f", Freq: {frequency} MHz")
        terminal_callback("\n\n")

        try:
            run_nextpnr_ice40(args)
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

        # Best-effort report: try JSON report, fallback to log parsing
        report_info = None
        report_path = os.path.join(work_dir, report_name)
        if os.path.isfile(report_path):
            report_info = _parse_pnr_report(report_path)

        if not report_info or "note" in report_info:
            if log_text:
                log_info = _parse_pnr_log(log_text)
                if log_info and "note" not in log_info:
                    report_info = log_info

        # Show summary block in console
        summary = _format_pnr_summary(report_info)
        if summary:
            terminal_callback("\n" + "─" * 40 + "\n")
            for line in summary:
                terminal_callback(line + "\n")
            terminal_callback("─" * 40 + "\n")

        # Copy result
        out_file = os.path.join(work_dir, asc_name)
        if os.path.isfile(out_file):
            os.makedirs(os.path.dirname(asc_path) or ".", exist_ok=True)
            shutil.copy2(out_file, asc_path)
            terminal_callback(f"\nPlace & Route complete -> {asc_path}\n")
            return asc_path, report_info
        else:
            terminal_callback("\nnextpnr did not produce an ASC file.\n")
            for f in os.listdir(work_dir):
                if f not in (src_name, log_name):
                    terminal_callback(f"  Output: {f}\n")
            return None, None
    finally:
        os.chdir(orig_cwd)
        shutil.rmtree(work_dir, ignore_errors=True)


def run_icepack(terminal_callback, asc_path, bin_path=None):
    if not icepack_available():
        terminal_callback("icepack not available (yowasp-nextpnr-ice40).\n")
        return None

    if not os.path.isfile(asc_path):
        terminal_callback(f"ASC file not found: {asc_path}\n")
        return None

    from yowasp_nextpnr_ice40 import run_icepack

    if bin_path is None:
        bin_path = os.path.splitext(asc_path)[0] + ".bin"

    work_dir = tempfile.mkdtemp(prefix="icepack_")
    try:
        shutil.copy2(asc_path, os.path.join(work_dir, "input.asc"))
        orig_cwd = os.getcwd()
        os.chdir(work_dir)

        terminal_callback(f"Running icepack on {os.path.basename(asc_path)}...\n")

        try:
            run_icepack(["input.asc", os.path.basename(bin_path)])
        except SystemExit:
            pass
        except Exception as e:
            terminal_callback(f"icepack error: {e}\n")
            os.chdir(orig_cwd)
            return None

        os.chdir(orig_cwd)

        out_file = os.path.join(work_dir, os.path.basename(bin_path))
        if os.path.isfile(out_file):
            os.makedirs(os.path.dirname(bin_path) or ".", exist_ok=True)
            shutil.copy2(out_file, bin_path)
            terminal_callback(f"Bitstream generated -> {bin_path}\n")
            return bin_path
        terminal_callback("icepack did not produce a bitstream file.\n")
        return None
    finally:
        os.chdir(orig_cwd)
        shutil.rmtree(work_dir, ignore_errors=True)
