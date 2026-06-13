import re


class VCDParser:

    def __init__(self, path):
        self.path = path
        self.timescale = "1ns"
        self.var_codes = {}
        self.time_values = []
        self.snapshots = {}

    def parse(self):
        self.var_codes = {}
        self.time_values = []
        self.snapshots = {}

        with open(self.path, "r") as f:
            raw = f.read()

        header_end = raw.find("$enddefinitions $end")
        if header_end == -1:
            return
        header = raw[:header_end]
        body = raw[header_end + len("$enddefinitions $end"):]

        for m in re.finditer(r'\$var\s+\S+\s+\S+\s+(\S+)\s+(\S+)\s+\$end', header):
            code, name = m.group(1), m.group(2)
            self.var_codes[code] = name

        ts = re.search(r'\$timescale\s+(\S+)\s+\$end', header)
        if ts:
            self.timescale = ts.group(1)

        body = body.strip()
        if body.startswith("$dumpvars"):
            end = body.find("$end")
            if end != -1:
                body = body[end + 4:].strip()

        times = []
        snapshots = {}
        current_time = 0
        current_values = {}

        for line in body.split("\n"):
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                current_time = int(line[1:])
                times.append(current_time)
                snapshots[current_time] = {}
            elif line.startswith("b") or line.startswith("B"):
                parts = line.split()
                if len(parts) >= 2:
                    val, code = parts[0], parts[1]
                    current_values[code] = val
                    if current_time in snapshots:
                        snapshots[current_time][code] = val
            elif len(line) >= 2 and line[0] in "01xXzZ":
                val, code = line[0], line[1:].strip()
                current_values[code] = val
                if current_time in snapshots:
                    snapshots[current_time][code] = val

        self.time_values = sorted(set(times))
        self.snapshots = snapshots

    def signal_value(self, signal_name, time):
        for code, name in self.var_codes.items():
            if name == signal_name:
                snaps = self.snapshots.get(time, {})
                if code in snaps:
                    return snaps[code]
                for t in reversed(self.time_values):
                    if t < time and code in self.snapshots.get(t, {}):
                        return self.snapshots[t][code]
                return None
        return None

    def snapshot_text(self, time, max_signals=20):
        snaps = self.snapshots.get(time, {})
        if not snaps:
            return f"[t={time}] (no changes at this time point)"

        signals = []
        for code in sorted(snaps.keys(), key=lambda c: self.var_codes.get(c, c)):
            name = self.var_codes.get(code, code)
            val = snaps[code]
            signals.append((name, val))
            if len(signals) >= max_signals and len(snaps) > max_signals:
                signals.append(("...", f"({len(snaps) - max_signals} more)"))
                break

        col1 = max(len(s) for s, _ in signals) if signals else 8
        if col1 < 8:
            col1 = 8
        col2 = 10
        ruler = f"  +{'-' * (col1 + 2)}+{'-' * (col2 + 2)}+"
        hdr = f"  | {'Signal'.ljust(col1)} | {'Value'.ljust(col2)} |"
        lines = [
            f"  t={time}  {self.timescale}",
            ruler,
            hdr,
            ruler,
        ]
        for name, val in signals:
            lines.append(f"  | {name.ljust(col1)} | {str(val).ljust(col2)} |")
        lines.append(ruler)
        return "\n".join(lines)
