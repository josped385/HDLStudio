from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QSpinBox, QCheckBox, QPushButton, QSlider, QDialogButtonBox,
    QGroupBox, QFormLayout, QTabWidget, QWidget,
)

from themes.theme_manager import ThemeManager


APP = "HDLStudio"
ORG = "HDLStudio"


def load_settings():
    s = QSettings(ORG, APP)
    return {
        "theme": s.value("theme", "dark"),
        "font_family": s.value("font_family", "Consolas"),
        "font_size": int(s.value("font_size", 10)),
        "tab_width": int(s.value("tab_width", 4)),
        "word_wrap": s.value("word_wrap", "false") == "true",
        "auto_save": s.value("auto_save", "false") == "true",
        "auto_save_interval": int(s.value("auto_save_interval", 30)),
        "language": s.value("language", "en"),
    }


def save_settings(settings):
    s = QSettings(ORG, APP)
    for k, v in settings.items():
        s.setValue(k, v)


class SettingsDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(480, 400)
        self._settings = load_settings()
        self._build()
        self._load()

    def _build(self):
        layout = QVBoxLayout(self)

        tabs = QTabWidget()
        layout.addWidget(tabs)

        # ── Editor tab ──
        editor_tab = QWidget()
        tabs.addTab(editor_tab, "Editor")
        editor_layout = QFormLayout(editor_tab)

        self.font_combo = QComboBox()
        for f in ("Consolas", "Courier New", "Lucida Console",
                   "Source Code Pro", "Fira Code", "JetBrains Mono",
                   "DejaVu Sans Mono", "Monaco", "Menlo", "Ubuntu Mono"):
            self.font_combo.addItem(f)
        self.font_combo.setEditable(True)
        editor_layout.addRow("Font family:", self.font_combo)

        font_size_layout = QHBoxLayout()
        self.font_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.font_size_slider.setRange(8, 24)
        self.font_size_label = QLabel("10")
        self.font_size_label.setFixedWidth(30)
        self.font_size_slider.valueChanged.connect(
            lambda v: self.font_size_label.setText(str(v))
        )
        font_size_layout.addWidget(self.font_size_slider)
        font_size_layout.addWidget(self.font_size_label)
        editor_layout.addRow("Font size:", font_size_layout)

        self.tab_width_spin = QSpinBox()
        self.tab_width_spin.setRange(2, 8)
        editor_layout.addRow("Tab width:", self.tab_width_spin)

        self.word_wrap_cb = QCheckBox("Enable word wrap")
        editor_layout.addRow(self.word_wrap_cb)

        # ── General tab ──
        general_tab = QWidget()
        tabs.addTab(general_tab, "General")
        general_layout = QFormLayout(general_tab)

        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Dark", "dark")
        self.theme_combo.addItem("Light", "light")
        general_layout.addRow("Theme:", self.theme_combo)

        self.lang_combo = QComboBox()
        self.lang_combo.addItem("English", "en")
        self.lang_combo.addItem("Spanish", "es")
        self.lang_combo.addItem("French", "fr")
        self.lang_combo.addItem("German", "de")
        general_layout.addRow("Language:", self.lang_combo)

        self.auto_save_cb = QCheckBox("Enable auto-save")
        general_layout.addRow(self.auto_save_cb)

        save_interval_layout = QHBoxLayout()
        self.auto_save_interval_spin = QSpinBox()
        self.auto_save_interval_spin.setRange(10, 300)
        self.auto_save_interval_spin.setSuffix(" sec")
        save_interval_layout.addWidget(self.auto_save_interval_spin)
        save_interval_layout.addStretch()
        general_layout.addRow("Auto-save interval:", save_interval_layout)

        # ── Language note ──
        lang_note = QLabel(
            "Language support is a placeholder. "
            "Restart required for some changes."
        )
        lang_note.setStyleSheet("color: #888; font-size: 9pt; padding: 4px;")
        lang_note.setWordWrap(True)
        general_layout.addRow(lang_note)

        # ── Buttons ──
        btn_layout = QHBoxLayout()
        restore_btn = QPushButton("Restore Defaults")
        restore_btn.clicked.connect(self._restore_defaults)
        btn_layout.addWidget(restore_btn)
        btn_layout.addStretch()

        self.btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        self.btn_box.accepted.connect(self._apply)
        self.btn_box.rejected.connect(self.reject)
        btn_layout.addWidget(self.btn_box)
        layout.addLayout(btn_layout)

    def _load(self):
        s = self._settings
        idx = self.theme_combo.findData(s["theme"])
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)
        idx = self.font_combo.findText(s["font_family"])
        if idx >= 0:
            self.font_combo.setCurrentIndex(idx)
        else:
            self.font_combo.setEditText(s["font_family"])
        self.font_size_slider.setValue(s["font_size"])
        self.tab_width_spin.setValue(s["tab_width"])
        self.word_wrap_cb.setChecked(s["word_wrap"])
        self.auto_save_cb.setChecked(s["auto_save"])
        self.auto_save_interval_spin.setValue(s["auto_save_interval"])
        idx = self.lang_combo.findData(s["language"])
        if idx >= 0:
            self.lang_combo.setCurrentIndex(idx)

    def _apply(self):
        s = self._settings
        s["theme"] = self.theme_combo.currentData()
        s["font_family"] = self.font_combo.currentText()
        s["font_size"] = self.font_size_slider.value()
        s["tab_width"] = self.tab_width_spin.value()
        s["word_wrap"] = self.word_wrap_cb.isChecked()
        s["auto_save"] = self.auto_save_cb.isChecked()
        s["auto_save_interval"] = self.auto_save_interval_spin.value()
        s["language"] = self.lang_combo.currentData()
        save_settings(s)

        main = self.window()
        if hasattr(main, "apply_settings"):
            main.apply_settings(s)

        self.accept()

    def _restore_defaults(self):
        self.theme_combo.setCurrentIndex(0)
        self.font_combo.setEditText("Consolas")
        self.font_size_slider.setValue(10)
        self.tab_width_spin.setValue(4)
        self.word_wrap_cb.setChecked(False)
        self.auto_save_cb.setChecked(False)
        self.auto_save_interval_spin.setValue(30)
        self.lang_combo.setCurrentIndex(0)
