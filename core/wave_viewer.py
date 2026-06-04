import os
import glob
from PyQt6.QtCore import QObject, pyqtSignal, QProcess


HDLSTUDIO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def gtkwave_path():
    exe = os.path.join(HDLSTUDIO_ROOT, "tools", "gtkwave", "bin", "gtkwave.exe")
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


class WaveViewer(QObject):

    error_occurred = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
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
        self._process.setWorkingDirectory(os.path.dirname(vcd_path))
        self._process.finished.connect(self._on_finished)
        self._process.start()

        if self._process.waitForStarted(3000):
            return True
        else:
            err = self._process.errorString()
            self.error_occurred.emit(f"Failed to launch GTKWave: {err}")
            return False

    def _on_finished(self, exit_code, exit_status):
        if exit_code == 0:
            return
        if exit_code == -1:
            return  # process was killed by us
        stderr = bytes(self._process.readAllStandardError()).decode("utf-8", errors="replace")
        msg = f"GTKWave exited with code {exit_code}"
        if stderr.strip():
            msg += f":\n{stderr.strip()}"
        self.error_occurred.emit(msg)

    def open_latest(self, search_dir):
        vcd = latest_vcd(search_dir)
        if not vcd:
            return False
        return self.open(vcd)

    def close(self):
        if self._process and self._process.state() != QProcess.ProcessState.NotRunning:
            self._process.terminate()
            self._process.waitForFinished(2000)
