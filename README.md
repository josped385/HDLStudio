# HDLStudio

[![Download](https://img.shields.io/badge/Download-v0.2.0-brightgreen)](https://github.com/josped385/HDLStudio/releases/tag/v0.2.0)
[![Docker](https://img.shields.io/badge/Docker-josped385/hdlstudio-2496ED?logo=docker)](https://hub.docker.com/r/josped385/hdlstudio)

A modern IDE for digital hardware design with Verilog, SystemVerilog and VHDL support — 100% generated with AI.

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
| Icarus      | Yes      | Place `iverilog.exe` in `tools/iverilog/` locally      |
| GTKWave     | Yes      | Place `gtkwave.exe` in `tools/gtkwave/` locally        |
| Graphviz    | Yes      | Place `dot.exe` in `tools/graphviz/` locally           |
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

### Download the installer (recommended)

Grab the latest release from the [Releases page](https://github.com/josped385/HDLStudio/releases/tag/v0.2.0):

- **`HDLStudio_Setup_v0.2.0.exe`** (~100 MB) — standalone installer, no external dependencies.

Run the installer and launch HDLStudio from the Start Menu or desktop shortcut.

### Run with Docker

HDLStudio is also available as a Docker image for Linux environments:

```bash
docker pull josped385/hdlstudio:latest
docker run --rm -it --network host -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix josped385/hdlstudio:latest
```

Requires an X11 server on the host. On Windows, use WSLg or VcXsrv.

See the [Dockerfile](Dockerfile) for details.

### Run from source

```bash
git clone https://github.com/josped385/hdlstudio.git
cd hdlstudio
pip install -r requirements.txt
pip install yowasp-yosys yowasp-nextpnr-ice40
python main.py
```

**Note:** Icarus Verilog, GTKWave and Graphviz must be placed in `tools/` locally when running from source. The standalone installer bundles them automatically.

See the full documentation at **https://josped385.github.io/HDLStudio/** for setup, usage, and API reference.

## Packaging as a standalone executable

Use PyInstaller with the provided spec file:

```bash
pip install pyinstaller
pyinstaller --clean HDLStudio.spec
```

The output appears in `dist/HDLStudio/`. A standalone installer can be built with Inno Setup
using `installer.iss` (requires Inno Setup 6+).

**Note:** Verilator requires WSL2 and cannot be bundled — it remains an optional
runtime dependency for users who install WSL separately.

## License

GPL v3 — see [LICENSE](LICENSE).

## Author

José Pedro Granado Olmo — [@josped385](https://github.com/josped385)

## Documentation

Full documentation is available at **https://josped385.github.io/HDLStudio/**
