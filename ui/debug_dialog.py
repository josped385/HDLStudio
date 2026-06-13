import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QRadioButton, QGroupBox, QFileDialog,
    QDialogButtonBox, QSpinBox, QComboBox, QFormLayout, QButtonGroup,
)
from PyQt6.QtCore import Qt


class DebugDialog(QDialog):

    MODE_FULL = "full"
    MODE_STEP = "step"

    def __init__(self, default_dir="", default_sim_path="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Debug Configuration")
        self.resize(520, 400)

        self._default_dir = default_dir

        layout = QVBoxLayout(self)

        mode_group = QGroupBox("Debug Mode")
        mode_layout = QVBoxLayout(mode_group)
        self._mode_group = QButtonGroup(self)

        self._radio_full = QRadioButton(
            "Complete — compile, run simulation, and open GTKWave automatically"
        )
        self._radio_full.setChecked(True)
        self._mode_group.addButton(self._radio_full, 1)

        self._radio_step = QRadioButton(
            "Step by time — run simulation then step through time points in the editor"
        )
        self._mode_group.addButton(self._radio_step, 2)

        mode_layout.addWidget(self._radio_full)
        mode_layout.addWidget(self._radio_step)
        layout.addWidget(mode_group)

        step_group = QGroupBox("Step Options")
        step_form = QFormLayout(step_group)

        self._step_size = QSpinBox()
        self._step_size.setRange(1, 999999)
        self._step_size.setValue(10)
        self._step_size.setSuffix(" ns")
        step_form.addRow("Time per step:", self._step_size)

        self._time_unit = QComboBox()
        self._time_unit.addItems(["ns", "ps", "us", "ms", "clock cycles"])
        step_form.addRow("Unit:", self._time_unit)

        self._max_time = QSpinBox()
        self._max_time.setRange(0, 99999999)
        self._max_time.setValue(10000)
        self._max_time.setSuffix(" ns")
        self._max_time.setSpecialValueText("No limit")
        step_form.addRow("Max simulation time:", self._max_time)

        layout.addWidget(step_group)

        file_group = QGroupBox("Output Files")
        file_layout = QFormLayout(file_group)

        sim_layout = QHBoxLayout()
        self._sim_path = QLineEdit(default_sim_path or os.path.join(default_dir, "build", "simulation.vvp"))
        sim_browse = QPushButton("Browse...")
        sim_browse.clicked.connect(self._browse_sim)
        sim_layout.addWidget(self._sim_path)
        sim_layout.addWidget(sim_browse)
        file_layout.addRow("Simulation output:", sim_layout)

        vcd_layout = QHBoxLayout()
        self._vcd_path = QLineEdit(os.path.join(default_dir, "build", "waves.vcd"))
        vcd_browse = QPushButton("Browse...")
        vcd_browse.clicked.connect(self._browse_vcd)
        vcd_layout.addWidget(self._vcd_path)
        vcd_layout.addWidget(vcd_browse)
        file_layout.addRow("VCD output:", vcd_layout)

        layout.addWidget(file_group)

        info_label = QLabel(
            "Step-by-step: after simulation, use Step Forward/Back in the\n"
            "terminal panel to navigate through time. Corresponding\n"
            "testbench lines with #delays will be highlighted in yellow."
        )
        info_label.setStyleSheet("color: #888; font-size: 9pt; padding: 8px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _browse_sim(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save simulation output as",
            self._sim_path.text(),
            "Simulation files (*.vvp *_vlsim);;All Files (*)"
        )
        if path:
            self._sim_path.setText(path)

    def _browse_vcd(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save waveform as",
            self._vcd_path.text(),
            "VCD files (*.vcd);;All Files (*)"
        )
        if path:
            self._vcd_path.setText(path)

    def sim_path(self):
        return self._sim_path.text()

    def mode(self):
        return self.MODE_FULL if self._radio_full.isChecked() else self.MODE_STEP

    def step_size_ns(self):
        return self._step_size.value() if self.mode() == self.MODE_STEP else 0

    def max_time_ns(self):
        return self._max_time.value() if self._max_time.value() > 0 else None

    def vcd_path(self):
        return self._vcd_path.text()
