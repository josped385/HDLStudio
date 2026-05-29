import os
import glob
from PyQt6.QtCore import QProcess


HDLSTUDIO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def gtkwave_path():
    exe = os.path.join(HDLSTUDIO_ROOT, "gtkwave", "bin", "gtkwave.exe")
    return exe if os.path.isfile(exe) else None


def find_vcd_files(search_dir):
    if not search_dir:
        return []
    return sorted(glob.glob(os.path.join(search_dir, "*.vcd")))


def find_wave_files(search_dir):
    """Find waveform dump files (.vcd, .fst, .lxt, .ghw) recursively."""
    if not search_dir or not os.path.isdir(search_dir):
        return []
    patterns = ["*.vcd", "*.fst", "*.lxt", "*.lxt2", "*.ghw", "*.vcd.gz"]
    found = []
    for p in patterns:
        found.extend(glob.glob(os.path.join(search_dir, p), recursive=True))
    return sorted(set(found))


def latest_vcd(search_dir):
    files = find_vcd_files(search_dir)
    if not files:
        return None
    return max(files, key=os.path.getmtime)


class WaveViewer:

    def __init__(self):
        self._process = None
        self._vcd_path = None

    @property
    def available(self):
        return gtkwave_path() is not None

    def open(self, vcd_path):
        exe = gtkwave_path()
        if not exe:
            return False
        if not vcd_path or not os.path.isfile(vcd_path):
            return False

        self._vcd_path = vcd_path
        self._process = QProcess()
        self._process.setProgram(exe)
        self._process.setArguments([vcd_path])
        self._process.start()

        return self._process.waitForStarted(3000)

    def open_latest(self, search_dir):
        vcd = latest_vcd(search_dir)
        if not vcd:
            return False
        return self.open(vcd)

    def close(self):
        if self._process and self._process.state() != QProcess.ProcessState.NotRunning:
            self._process.terminate()
            self._process.waitForFinished(2000)
