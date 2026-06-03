# HDLStudio

A modern IDE for digital hardware design with Verilog, SystemVerilog and VHDL support.

## Features

- **Code editor** — Syntax highlighting, autocompletion, snippets, hover documentation
- **Simulation** — Icarus Verilog or Verilator (via WSL) compilation & run
- **Waveform viewer** — GTKWave integration (VCD, FST, LXT, GHW)
- **Synthesis** — Yosys HDL synthesis (BLIF, JSON, Verilog, EDIF output)
- **Schematic viewer** — Gate-level schematic via Yosys + Graphviz
- **Place & Route** — nextpnr-ice40 for Lattice iCE40 FPGAs
- **Testbench generator** — Automatic testbench generation from HDL module/entity ports
- **File explorer** — Project tree with context actions for all tools
- **Extension system** — Extend the IDE via Python plugins
- **Themes** — Dark and light themes
- **Settings** — Configurable editor font, tab width, word wrap, auto-save

## Requirements

| Component   | Required | Notes                                                  |
|-------------|----------|--------------------------------------------------------|
| Python      | Yes      | >= 3.13                                                |
| Icarus      | Yes      | Bundled in `tools/iverilog/`                            |
| GTKWave     | Yes      | Bundled in `tools/gtkwave/`                             |
| Graphviz    | Yes      | Bundled in `tools/graphviz/`                            |
| Yosys       | Yes      | Installed via pip (`yowasp-yosys`)                      |
| nextpnr     | Optional | Installed via pip (`yowasp-nextpnr-ice40`)              |
| Verilator   | Optional | Via WSL2 with Ubuntu (see below)                        |

### Verilator (optional)

To use Verilator as the simulation backend:

1. Install WSL2 with Ubuntu:
   ```bash
   wsl --install -d Ubuntu
   ```
2. The IDE will auto-detect Verilator inside WSL and list it in the Simulator dropdown.

## Quick start

```bash
git clone https://github.com/josped385/hdlstudio.git
cd hdlstudio
pip install -r requirements.txt
python main.py
```

All bundled tools (`iverilog`, `gtkwave`, `graphviz`) are already included under `tools/`.
No additional PATH configuration needed.

## Packaging as a standalone executable

Use PyInstaller to create a single `.exe`:

```bash
pip install pyinstaller
pyinstaller --name HDLStudio --windowed --add-data "tools;tools" main.py
```

**Note:** Verilator requires WSL2 and cannot be bundled — it remains an optional
runtime dependency for users who install WSL separately.

## License

GPL v3 — see [LICENSE](LICENSE).

## Author

José Pedro Granado Olmo — [@josped385](https://github.com/josped385)
