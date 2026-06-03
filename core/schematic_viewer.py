import os
import shutil
import tempfile

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QLabel, QSizePolicy,
)

HDLSTUDIO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOT_PATH = os.path.join(
    HDLSTUDIO_ROOT, "tools", "graphviz", "Graphviz-15.0.0-win64", "bin", "dot.exe"
)


def _dot_available():
    return os.path.isfile(DOT_PATH)


def _run_yosys(script, work_dir):
    from yowasp_yosys import run_yosys
    orig = os.getcwd()
    os.chdir(work_dir)
    try:
        run_yosys(["-p", script])
    except SystemExit:
        pass
    except Exception as e:
        raise RuntimeError(f"Yosys error: {e}") from e
    finally:
        os.chdir(orig)


def _dot_to_svg(dot_path, svg_path):
    import subprocess
    startupinfo = None
    if os.name == "nt":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    env = os.environ.copy()
    env["PATH"] = os.path.dirname(DOT_PATH) + os.pathsep + env.get("PATH", "")
    result = subprocess.run(
        [DOT_PATH, "-Tsvg", dot_path, "-o", svg_path],
        capture_output=True, text=True, env=env, startupinfo=startupinfo,
    )
    if result.returncode != 0:
        raise RuntimeError(f"dot.exe failed: {result.stderr}")


def _generate_svg_via_yosys(blif_path, work_dir, base):
    src = os.path.join(work_dir, "input.blif")
    shutil.copy2(blif_path, src)

    _run_yosys(f"read_blif input.blif; show -format dot -prefix {base}", work_dir)

    dot_file = os.path.join(work_dir, f"{base}.dot")
    if not os.path.isfile(dot_file):
        raise RuntimeError("Yosys show did not produce a DOT file")

    if not _dot_available():
        with open(dot_file) as f:
            dot_text = f.read()
        return None, dot_text

    svg_file = os.path.join(work_dir, f"{base}.svg")
    _dot_to_svg(dot_file, svg_file)

    if not os.path.isfile(svg_file):
        raise RuntimeError("dot.exe did not produce an SVG file")

    with open(svg_file, "rb") as f:
        svg_data = f.read()
    return svg_data, None


def show_schematic(blif_path, parent=None):
    work = tempfile.mkdtemp(prefix="sch_")
    try:
        svg_data, dot_text = _generate_svg_via_yosys(blif_path, work, "schematic")
        if svg_data:
            dlg = _SvgDialog("Schematic", svg_data, parent)
            return dlg
        elif dot_text:
            dlg = _DotFallbackDialog("Schematic (DOT fallback)", dot_text, parent)
            return dlg
        return None
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None
    finally:
        shutil.rmtree(work, ignore_errors=True)


def show_schematic_from_hdl(hdl_path, parent=None):
    ext = os.path.splitext(hdl_path)[1].lower()
    if ext in (".v", ".sv"):
        read_cmd = "read_verilog"
    elif ext in (".vhd", ".vhdl"):
        read_cmd = "read_vhdl"
    else:
        return None

    work = tempfile.mkdtemp(prefix="sch_")
    try:
        src = os.path.join(work, "input" + ext)
        shutil.copy2(hdl_path, src)

        _run_yosys(
            f"{read_cmd} input{ext}; proc; show -format dot -prefix schematic",
            work,
        )

        dot_file = os.path.join(work, "schematic.dot")
        if not os.path.isfile(dot_file):
            return None

        if not _dot_available():
            with open(dot_file) as f:
                dot_text = f.read()
            dlg = _DotFallbackDialog("Schematic (DOT fallback)", dot_text, parent)
            return dlg

        svg_file = os.path.join(work, "schematic.svg")
        _dot_to_svg(dot_file, svg_file)

        if not os.path.isfile(svg_file):
            return None

        with open(svg_file, "rb") as f:
            svg_data = f.read()

        dlg = _SvgDialog(f"Schematic — {os.path.basename(hdl_path)}", svg_data, parent)
        return dlg
    except Exception:
        import traceback
        traceback.print_exc()
        return None
    finally:
        shutil.rmtree(work, ignore_errors=True)


class _SvgDialog(QDialog):
    def __init__(self, title, svg_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(900, 650)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.svg_widget = QSvgWidget()
        self.svg_widget.load(svg_data)
        self.svg_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        layout.addWidget(self.svg_widget)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        fit_btn = QPushButton("Fit to Window")
        fit_btn.clicked.connect(self._fit)
        btn_layout.addWidget(fit_btn)
        layout.addLayout(btn_layout)

    def _fit(self):
        self.svg_widget.setFixedSize(self.svg_widget.sizeHint())


class _DotFallbackDialog(QDialog):
    def __init__(self, title, dot_text, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(800, 600)

        layout = QVBoxLayout(self)
        label = QLabel("Graphviz (dot.exe) not available. Showing raw DOT source:")
        label.setStyleSheet("color: #888; padding: 4px;")
        layout.addWidget(label)

        text_edit = QTextEdit(self)
        text_edit.setReadOnly(True)
        text_edit.setPlainText(dot_text)
        text_edit.setFont(QFont("Consolas", 10))
        text_edit.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4;")
        layout.addWidget(text_edit)
