from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QComboBox, QSpinBox, QDialogButtonBox, QLabel, QGroupBox
)
from PyQt6.QtCore import Qt

from core.pnr_system import FAMILIES, family_available


class PnrDialog(QDialog):

    FAMILY_DEVICES = {
        "ice40": ["LP384", "LP1K", "LP4K", "LP8K", "HX1K", "HX4K", "HX8K",
                   "UP3K", "UP5K", "U1K", "U2K", "U4K"],
        "ecp5":  ["12K", "25K", "45K", "85K"],
        "nexus": ["LIFCL-17", "LIFCL-33", "LIFCL-40", "LIFCL-55"],
        "machxo2": ["LCMXO2-256HC", "LCMXO2-256ZE", "LCMXO2-640HC",
                     "LCMXO2-640ZE", "LCMXO2-1200HC", "LCMXO2-1200ZE",
                     "LCMXO2-2000HC", "LCMXO2-2000ZE", "LCMXO2-4000HC",
                     "LCMXO2-4000ZE", "LCMXO2-7000HC", "LCMXO2-7000ZE"],
        "gowin": ["GW1N-1", "GW1N-2", "GW1N-4", "GW1N-6", "GW1N-9",
                   "GW1N-16", "GW1N-28", "GW1NR-4", "GW1NR-9",
                   "GW2A-18", "GW2A-55"],
    }

    FAMILY_PACKAGES = {
        "ice40":  ["VQ100", "TQ144", "CT256", "BG121", "BG256",
                    "QFN32", "QFN48", "QFN64", "MBGA81", ""],
        "ecp5":   ["CABGA256", "CSFBGA285", "CSFBGA381", "CABGA381",
                    "CSFBGA554", "CABGA554", ""],
        "nexus":  ["CSFBGA81", "CSFBGA121", "CSFBGA256",
                    "CSFBGA484", "CSFBGA564", ""],
        "machxo2": ["TQFP32", "TQFP44", "TQFP48", "TQFP64", "TQFP100",
                      "TQFP144", "caBGA256", "ftBGA256", ""],
        "gowin":  ["QFN48", "QFN88", "LQFP100", "LQFP144",
                    "BGA256", "BGA324", "BGA396", ""],
    }

    FAMILY_LABELS = {
        "ice40": "Lattice iCE40",
        "ecp5":  "Lattice ECP5",
        "nexus": "Lattice Nexus",
        "machxo2": "Lattice MachXO2",
        "gowin": "Gowin (himbaechel)",
    }

    FAMILY_NOTES = {
        "ice40": "Output: .asc  → icepack → .bin",
        "ecp5":  "Output: .config  → ecppack → .bit",
        "nexus": "Output: .bit (no separate pack step)",
        "machxo2": "Output: .config  → ecppack → .bit",
        "gowin": "Output: .fasm  → gowin_pack → .fs",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Place & Route Configuration")
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)

        # ── Family selection ──
        self.family_combo = QComboBox()
        for key, label in self.FAMILY_LABELS.items():
            avail = family_available(key)
            text = label if avail else f"{label}  (not installed)"
            self.family_combo.addItem(text, userData=key)
            if not avail:
                idx = self.family_combo.count() - 1
                self.family_combo.model().item(idx).setEnabled(False)
        self.family_combo.currentIndexChanged.connect(self._on_family_changed)

        dev_group = QGroupBox("Target")
        dev_layout = QFormLayout(dev_group)
        dev_layout.addRow("Family:", self.family_combo)

        # ── Device ──
        self.device_combo = QComboBox()
        self.device_combo.setEditable(True)
        dev_layout.addRow("Device:", self.device_combo)

        # ── Package ──
        self.package_combo = QComboBox()
        self.package_combo.setEditable(True)
        self.package_combo.setPlaceholderText("(auto / none)")
        dev_layout.addRow("Package:", self.package_combo)

        # ── Frequency ──
        self.freq_spin = QSpinBox()
        self.freq_spin.setRange(0, 500)
        self.freq_spin.setValue(12)
        self.freq_spin.setSuffix(" MHz")
        self.freq_spin.setSpecialValueText("auto")
        dev_layout.addRow("Frequency:", self.freq_spin)

        layout.addWidget(dev_group)

        # ── Info section ──
        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("color: #888; font-style: italic;")
        layout.addWidget(self.info_label)

        # ── Buttons ──
        self.bbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                     QDialogButtonBox.StandardButton.Cancel)
        self.bbox.accepted.connect(self.accept)
        self.bbox.rejected.connect(self.reject)
        layout.addWidget(self.bbox)

        self._populate_initial()
        self._on_family_changed()

    def _populate_initial(self):
        for i in range(self.family_combo.count()):
            if self.family_combo.model().item(i).isEnabled():
                self.family_combo.setCurrentIndex(i)
                break

    def _on_family_changed(self):
        key = self.family_combo.currentData()
        if not key:
            return

        self.device_combo.clear()
        self.device_combo.addItems(self.FAMILY_DEVICES.get(key, []))
        if self.device_combo.count():
            self.device_combo.setCurrentIndex(0)

        self.package_combo.clear()
        pkgs = self.FAMILY_PACKAGES.get(key, [])
        pkgs = [p for p in pkgs if p]
        self.package_combo.addItems(pkgs)
        self.package_combo.setCurrentIndex(-1)

        note = self.FAMILY_NOTES.get(key, "")
        self.info_label.setText(note)

    # ── getters ──

    def family_key(self):
        return self.family_combo.currentData()

    def device(self):
        return self.device_combo.currentText().strip()

    def package(self):
        p = self.package_combo.currentText().strip()
        return p if p else None

    def frequency(self):
        return self.freq_spin.value()
