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
        self._closing = False
        self._tcl_script_path = None

    @property
    def available(self):
        return gtkwave_path() is not None

    def open(self, vcd_path, tcl_script=None):
        exe = gtkwave_path()
        if not exe:
            return False
        if not vcd_path or not os.path.isfile(vcd_path):
            return False

        if self._process and self._process.state() != QProcess.ProcessState.NotRunning:
            self.close()
            if not self._process.waitForFinished(3000):
                self._process.kill()
                self._process.waitForFinished(1000)

        self._vcd_path = vcd_path
        self._process = QProcess()
        args = [vcd_path]
        if tcl_script and os.path.isfile(tcl_script):
            args = ["-T", tcl_script, vcd_path]
        self._process.setProgram(exe)
        self._process.setArguments(args)
        self._process.setWorkingDirectory(os.path.dirname(vcd_path))
        self._process.finished.connect(self._on_finished)
        self._process.start()

        if self._process.waitForStarted(3000):
            return True
        else:
            err = self._process.errorString()
            self.error_occurred.emit(f"Failed to launch GTKWave: {err}")
            return False

    def reopen_at_time(self, vcd_path, time_in_native_units, timescale):
        try:
            unit = timescale.replace("1", "").strip()
            fs_per_unit = {"ps": 1000, "ns": 1000000, "us": 1000000000, "ms": 1000000000000}
            time_fs = time_in_native_units * fs_per_unit.get(unit, 1000000)

            script_dir = os.path.dirname(vcd_path)
            self._tcl_script_path = os.path.join(script_dir, "_gtkwave_step.tcl")
            with open(self._tcl_script_path, "w") as f:
                f.write(f"gtkwave::/Time/Set_Cursor_Time {time_fs}\n")
                f.write("gtkwave::/Zoom/Zoom_Full\n")
                f.write("gtkwave::/Window/Redraw\n")

            self._closing = True
            result = self.open(vcd_path, tcl_script=self._tcl_script_path)
            self._closing = False
            return result
        except Exception:
            self.open(vcd_path)
            return False

    def _on_finished(self, exit_code, exit_status):
        if exit_code == 0:
            return
        if exit_code == -1 or self._closing:
            return
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
        self._closing = True
        if self._process and self._process.state() != QProcess.ProcessState.NotRunning:
            self._process.terminate()
            if not self._process.waitForFinished(2000):
                self._process.kill()
                self._process.waitForFinished(1000)
        self._closing = False

        if self._tcl_script_path and os.path.isfile(self._tcl_script_path):
            try:
                os.unlink(self._tcl_script_path)
            except OSError:
                pass
            self._tcl_script_path = None
