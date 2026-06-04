import os
import shutil
import tempfile

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QImage, QPainter, QAction, QKeySequence
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QLabel, QSizePolicy, QScrollArea, QFileDialog,
    QMenu, QToolButton, QMessageBox, QApplication, QLineEdit,
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
        self._svg_data = svg_data
        self._renderer = QSvgRenderer(svg_data)
        self._zoom = 1.0

        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.CustomizeWindowHint
            | Qt.WindowType.WindowTitleHint
            | Qt.WindowType.WindowCloseButtonHint
            | Qt.WindowType.WindowMinMaxButtonsHint
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Scroll area for zoom/pan
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(False)
        self._scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.svg_widget = QSvgWidget()
        self.svg_widget.load(svg_data)
        self._default_size = self._renderer.defaultSize()
        if self._default_size.isValid() and not self._default_size.isNull():
            self._base_size = self._default_size
        else:
            self._base_size = QSize(800, 500)
        self.svg_widget.resize(self._base_size)
        self.svg_widget.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )

        self._scroll.setWidget(self.svg_widget)
        layout.addWidget(self._scroll)

        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(6, 4, 6, 4)

        save_btn = QToolButton()
        save_btn.setText("Save")
        save_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        save_menu = QMenu(self)
        svg_act = save_menu.addAction("SVG")
        svg_act.triggered.connect(lambda: self._save_as("svg"))
        png_act = save_menu.addAction("PNG")
        png_act.triggered.connect(lambda: self._save_as("png"))
        pdf_act = save_menu.addAction("PDF")
        pdf_act.triggered.connect(lambda: self._save_as("pdf"))
        save_btn.setMenu(save_menu)
        toolbar.addWidget(save_btn)

        toolbar.addStretch()

        zoom_out_btn = QPushButton("Zoom Out")
        zoom_out_btn.clicked.connect(self._zoom_out)
        toolbar.addWidget(zoom_out_btn)

        self._zoom_input = QLineEdit("100")
        self._zoom_input.setFixedWidth(50)
        self._zoom_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._zoom_input.setToolTip("Enter zoom % and press Enter")
        self._zoom_input.editingFinished.connect(self._zoom_custom)
        toolbar.addWidget(self._zoom_input)
        pct_label = QLabel("%")
        pct_label.setStyleSheet("color: #888;")
        toolbar.addWidget(pct_label)

        zoom_in_btn = QPushButton("Zoom In")
        zoom_in_btn.clicked.connect(self._zoom_in)
        toolbar.addWidget(zoom_in_btn)

        fit_btn = QPushButton("Fit")
        fit_btn.clicked.connect(self._fit)
        toolbar.addWidget(fit_btn)

        fs_btn = QPushButton("Fullscreen")
        fs_btn.setCheckable(True)
        fs_btn.clicked.connect(self._toggle_fullscreen)
        toolbar.addWidget(fs_btn)

        layout.addLayout(toolbar)

        shortcut = QAction("Fullscreen", self)
        shortcut.setShortcut(QKeySequence("F11"))
        shortcut.triggered.connect(self._toggle_fullscreen)
        self.addAction(shortcut)

    def _apply_zoom(self):
        w = int(self._base_size.width() * self._zoom)
        h = int(self._base_size.height() * self._zoom)
        self.svg_widget.setFixedSize(w, h)
        self._zoom_input.setText(str(int(self._zoom * 100)))

    def _zoom_custom(self):
        try:
            pct = int(self._zoom_input.text())
            self._zoom = max(0.05, min(pct / 100.0, 10.0))
            self._apply_zoom()
        except ValueError:
            self._zoom_input.setText(str(int(self._zoom * 100)))

    def _zoom_in(self):
        self._zoom = min(self._zoom * 1.25, 5.0)
        self._apply_zoom()

    def _zoom_out(self):
        self._zoom = max(self._zoom / 1.25, 0.2)
        self._apply_zoom()

    def _fit(self):
        self._zoom = 1.0
        self._apply_zoom()
        self.svg_widget.setMinimumSize(0, 0)
        self.svg_widget.setMaximumSize(16777215, 16777215)
        self.svg_widget.resize(self._base_size)

    def _toggle_fullscreen(self, checked=None):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _save_as(self, fmt):
        if fmt == "svg":
            filter_str = "SVG (*.svg)"
            default_ext = ".svg"
        elif fmt == "png":
            filter_str = "PNG (*.png)"
            default_ext = ".png"
        elif fmt == "pdf":
            filter_str = "PDF (*.pdf)"
            default_ext = ".pdf"
        else:
            return

        title = self.windowTitle()
        base = title.replace("Schematic — ", "").replace("Schematic", "schematic").strip()
        if not base:
            base = "schematic"

        path, _ = QFileDialog.getSaveFileName(
            self, f"Save as {fmt.upper()}", base + default_ext, filter_str
        )
        if not path:
            return

        try:
            if fmt == "svg":
                with open(path, "wb") as f:
                    f.write(self._svg_data)
            elif fmt == "png":
                self._render_to_image(path, "PNG")
            elif fmt == "pdf":
                self._render_to_pdf(path)
            self.status_bar_message(f"Saved: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))

    def _render_to_image(self, path, fmt):
        size = self._renderer.defaultSize()
        if not size.isValid() or size.isNull():
            size = QSize(800, 500)
        img = QImage(size, QImage.Format.Format_ARGB32)
        img.fill(Qt.GlobalColor.white)
        painter = QPainter(img)
        self._renderer.render(painter)
        painter.end()
        img.save(path, fmt)

    def _render_to_pdf(self, path):
        from PyQt6.QtPrintSupport import QPrinter
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(path)
        painter = QPainter(printer)
        self._renderer.render(painter)
        painter.end()

    def status_bar_message(self, msg):
        parent = self.parent()
        if parent:
            sb = parent.statusBar()
            if sb:
                sb.showMessage(msg, 3000)


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
