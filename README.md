# HDLStudio

A modern IDE for digital hardware design with Verilog, SystemVerilog and VHDL support.

## Features

- **Code editor** — Syntax highlighting, autocompletion, snippets, hover documentation
- **Simulation** — Icarus Verilog compilation & run, GTKWave waveform viewer integration
- **Synthesis** — Yosys HDL synthesis (BLIF, JSON, Verilog, EDIF output)
- **Schematic viewer** — Gate-level schematic via Yosys + Graphviz
- **Place & Route** — nextpnr-ice40 for Lattice iCE40 FPGAs
- **Testbench generator** — Automatic testbench generation from HDL module/entity ports
- **File explorer** — Project tree with context actions for all tools
- **Git integration** — Basic git panel
- **Plugin system** — Extend the IDE via Python extensions
- **Themes** — Dark and light themes

## Requirements

| Component   | Installation                                                    |
|-------------|-----------------------------------------------------------------|
| Python      | >= 3.13                                                         |
| Icarus      | [iverilog.icarus.com](https://github.com/steveicarus/iverilog)  |
| GTKWave     | [gtkwave.sourceforge.net](https://gtkwave.sourceforge.net)      |
| Graphviz    | [graphviz.org/download](https://graphviz.org/download)          |

## Quick start

```bash
git clone https://github.com/jpgranado/hdlstudio.git
cd hdlstudio
pip install -r requirements.txt
python main.py
```

Place Icarus Verilog (`iverilog/bin/`) and GTKWave (`gtkwave/bin/`) next to `main.py`,
or add them to your system PATH. Graphviz `dot.exe` goes under `graphviz/Graphviz-*-win64/bin/`.

## License

GPL v3 — see [LICENSE](LICENSE).

## Author

José Pedro Granado Olmo
