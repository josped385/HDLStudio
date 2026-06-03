import os
from PyQt6.QtWidgets import QToolBar, QLabel, QComboBox, QWidget, QSizePolicy

from core.build_system import BuildSystem


class MainToolBar(QToolBar):

    def __init__(self, parent=None):
        super().__init__("Main Toolbar", parent)

        self.setMovable(False)
        self.setIconSize(parent.iconSize())

        self.main = parent
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
        self.addAction(a.toggle_terminal)

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

        tb_label = QLabel("Testbench:")
        tb_label.setStyleSheet("color: #aaaaaa; padding-left: 4px;")
        self.addWidget(tb_label)

        self.tb_combo = QComboBox()
        self.tb_combo.setMinimumWidth(120)
        self.tb_combo.setMaximumWidth(180)
        self.tb_combo.setPlaceholderText("(auto)")
        self.tb_combo.currentIndexChanged.connect(self._on_tb_changed)
        self.addWidget(self.tb_combo)

        sim_label = QLabel("Simulator:")
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

    def _on_tb_changed(self, index):
        path = self.tb_combo.itemData(index)
        self.main.build_system.testbench_file = path

    def _on_simulator_changed(self, index):
        sim = self.sim_combo.itemData(index)
        self.main.build_system.simulator = sim

    def refresh_file_lists(self):
        self.module_combo.blockSignals(True)
        self.tb_combo.blockSignals(True)
        self.sim_combo.blockSignals(True)

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

        idx_module = 0
        idx_tb = 0

        if bs.module_file:
            for i in range(self.module_combo.count()):
                if self.module_combo.itemData(i) == bs.module_file:
                    idx_module = i
                    break

        if bs.testbench_file:
            for i in range(self.tb_combo.count()):
                if self.tb_combo.itemData(i) == bs.testbench_file:
                    idx_tb = i
                    break

        self.module_combo.setCurrentIndex(idx_module)
        self.tb_combo.setCurrentIndex(idx_tb)

        idx_sim = self.sim_combo.findData(bs.simulator)
        if idx_sim >= 0:
            self.sim_combo.setCurrentIndex(idx_sim)

        self.module_combo.blockSignals(False)
        self.tb_combo.blockSignals(False)
        self.sim_combo.blockSignals(False)