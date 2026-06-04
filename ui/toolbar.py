import os
from PyQt6.QtWidgets import QToolBar, QLabel, QComboBox, QWidget, QSizePolicy

from core.build_system import BuildSystem


class MainToolBar(QToolBar):

    def __init__(self, parent=None):
        super().__init__("Main Toolbar", parent)

        self.setMovable(False)
        self.setIconSize(parent.iconSize())

        self.main = parent
        self._user_selected_module = False
        self._user_selected_tb = False
        self._build()

    def _build(self):

        a = self.main.ide_actions

        self.addAction(a.open_project)
        self.addAction(a.new_file)
        self.addAction(a.open_file)

        self.addSeparator()

        self.addAction(a.save)
        self.addAction(a.save_as)

        self.addSeparator()

        self.addAction(a.compile)
        self.addAction(a.run)
        self.addAction(a.synthesize)
        self.addAction(a.place_and_route)
        self.addAction(a.view_waves)

        self.addSeparator()

        mod_label = QLabel("Module:")
        mod_label.setStyleSheet("color: #aaaaaa; padding-left: 4px;")
        self.addWidget(mod_label)

        self.module_combo = QComboBox()
        self.module_combo.setMinimumWidth(120)
        self.module_combo.setMaximumWidth(180)
        self.module_combo.setPlaceholderText("(auto)")
        self.module_combo.currentIndexChanged.connect(self._on_module_changed)
        self.addWidget(self.module_combo)

        tb_label = QLabel("TB:")
        tb_label.setStyleSheet("color: #aaaaaa; padding-left: 4px;")
        self.addWidget(tb_label)

        self.tb_combo = QComboBox()
        self.tb_combo.setMinimumWidth(120)
        self.tb_combo.setMaximumWidth(180)
        self.tb_combo.setPlaceholderText("(auto)")
        self.tb_combo.currentIndexChanged.connect(self._on_tb_changed)
        self.addWidget(self.tb_combo)

        sim_label = QLabel("Sim:")
        sim_label.setStyleSheet("color: #aaaaaa; padding-left: 4px;")
        self.addWidget(sim_label)

        self.sim_combo = QComboBox()
        self.sim_combo.setMinimumWidth(100)
        self.sim_combo.setMaximumWidth(140)
        self.sim_combo.addItem("Icarus Verilog", BuildSystem.SIM_ICARUS)
        self.sim_combo.addItem("Verilator", BuildSystem.SIM_VERILATOR)
        self.sim_combo.currentIndexChanged.connect(self._on_simulator_changed)
        self.addWidget(self.sim_combo)

        spacer = QWidget()
        spacer.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.addWidget(spacer)

        self.addAction(a.toggle_theme)

    def apply_theme(self, colors):
        css = f"color: {colors['text_secondary']}; padding-left: 4px;"
        for w in self.findChildren(QLabel):
            w.setStyleSheet(css)

    def _on_module_changed(self, index):
        path = self.module_combo.itemData(index)
        self.main.build_system.module_file = path
        self._user_selected_module = True

    def _on_tb_changed(self, index):
        path = self.tb_combo.itemData(index)
        self.main.build_system.testbench_file = path
        self._user_selected_tb = True

    def _on_simulator_changed(self, index):
        sim = self.sim_combo.itemData(index)
        self.main.build_system.simulator = sim

    def populate(self, initial=False):
        self.module_combo.blockSignals(True)
        self.tb_combo.blockSignals(True)
        self.sim_combo.blockSignals(True)

        prev_module = self.module_combo.currentData()
        prev_tb = self.tb_combo.currentData()

        self.module_combo.clear()
        self.tb_combo.clear()

        self.module_combo.addItem("(auto detect)", None)
        self.tb_combo.addItem("(auto detect)", None)

        bs = self.main.build_system
        files = bs.collect_hdl_files()
        root = bs.root_dir

        for f in files:
            if root:
                rel = os.path.relpath(f, root)
            else:
                rel = os.path.basename(f)
            self.module_combo.addItem(rel, f)
            self.tb_combo.addItem(rel, f)

        if initial:
            bs.auto_select_files()
            self._user_selected_module = False
            self._user_selected_tb = False

        if self._user_selected_module and prev_module:
            idx = self.module_combo.findData(prev_module)
            self.module_combo.setCurrentIndex(idx if idx >= 0 else 0)
        elif bs.module_file:
            idx = self.module_combo.findData(bs.module_file)
            self.module_combo.setCurrentIndex(idx if idx >= 0 else 0)
        else:
            self.module_combo.setCurrentIndex(0)

        if self._user_selected_tb and prev_tb:
            idx = self.tb_combo.findData(prev_tb)
            self.tb_combo.setCurrentIndex(idx if idx >= 0 else 0)
        elif bs.testbench_file:
            idx = self.tb_combo.findData(bs.testbench_file)
            self.tb_combo.setCurrentIndex(idx if idx >= 0 else 0)
        else:
            self.tb_combo.setCurrentIndex(0)

        idx_sim = self.sim_combo.findData(bs.simulator)
        if idx_sim >= 0:
            self.sim_combo.setCurrentIndex(idx_sim)

        self.module_combo.blockSignals(False)
        self.tb_combo.blockSignals(False)
        self.sim_combo.blockSignals(False)

    def reset_auto_select(self):
        self._user_selected_module = False
        self._user_selected_tb = False
