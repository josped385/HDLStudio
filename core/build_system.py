import os
import glob
import subprocess


HDLSTUDIO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class BuildSystem:

    def __init__(self, project):
        self.project = project
        self.working_dir = None
        self.module_file = None
        self.testbench_file = None
        self.output_name = "simulation.vvp"
        self.build_dir_name = "build"
        self.last_vcd_path = None

    @property
    def _iverilog_path(self):
        return os.path.join(HDLSTUDIO_ROOT, "iverilog", "bin", "iverilog.exe")

    @property
    def _vvp_path(self):
        return os.path.join(HDLSTUDIO_ROOT, "iverilog", "bin", "vvp.exe")

    @property
    def root_dir(self):
        if self.project and self.project.is_loaded():
            return self.project.root_path
        return self.working_dir

    def iverilog_available(self):
        return os.path.isfile(self._iverilog_path)

    def vvp_available(self):
        return os.path.isfile(self._vvp_path)

    _SKIP_DIRS = {"gtkwave", "iverilog", ".venv", ".git", "__pycache__"}

    def collect_hdl_files(self):
        root = self.root_dir
        if not root:
            return []
        hdl_files = []
        for ext in ("**/*.v", "**/*.sv", "**/*.vhd", "**/*.vhdl"):
            for f in glob.glob(os.path.join(root, ext), recursive=True):
                parts = os.path.relpath(f, root).replace("\\", "/").split("/")
                if any(p in self._SKIP_DIRS for p in parts):
                    continue
                if os.path.isfile(f):
                    hdl_files.append(f)
        return sorted(hdl_files)

    def set_working_dir_from_file(self, filepath):
        d = os.path.dirname(os.path.abspath(filepath))
        self.working_dir = d

    def auto_select_files(self):
        files = self.collect_hdl_files()
        if not files:
            self.module_file = None
            self.testbench_file = None
            return

        tb_candidates = []
        module_candidates = []

        for f in files:
            name = os.path.splitext(os.path.basename(f))[0].lower()
            if name.startswith("tb_") or name.endswith("_tb"):
                tb_candidates.append(f)
            else:
                module_candidates.append(f)

        if len(files) == 1:
            self.module_file = files[0]
            self.testbench_file = None
        elif tb_candidates:
            self.testbench_file = tb_candidates[0]
            remaining = [f for f in files if f != self.testbench_file]
            self.module_file = remaining[0] if remaining else None
        else:
            self.module_file = module_candidates[0] if module_candidates else files[0]
            self.testbench_file = files[1] if len(files) > 1 else None

    def compile(self, terminal_callback):
        root = self.root_dir
        if not root:
            terminal_callback("No project or file open.\n")
            return False

        if not self.iverilog_available():
            terminal_callback(
                f"iverilog not found at {self._iverilog_path}\n"
                "Make sure Icarus Verilog is bundled in the iverilog/ directory.\n"
            )
            return False

        sources = []
        if self.module_file and os.path.isfile(self.module_file):
            sources.append(self.module_file)
        if self.testbench_file and os.path.isfile(self.testbench_file):
            if self.testbench_file not in sources:
                sources.append(self.testbench_file)

        if not sources:
            sources = self.collect_hdl_files()
            if not sources:
                terminal_callback("No HDL files found.\n")
                return False

        build_dir = os.path.join(root, self.build_dir_name)
        os.makedirs(build_dir, exist_ok=True)
        output_path = os.path.join(build_dir, self.output_name)

        cmd = [self._iverilog_path, "-o", output_path, "-g2012"] + sources
        terminal_callback(f"{' '.join(cmd)}\n\n")

        env = os.environ.copy()
        env["PATH"] = os.path.join(HDLSTUDIO_ROOT, "iverilog", "bin") + os.pathsep + env.get("PATH", "")

        startupinfo = None
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=root,
            env=env,
            startupinfo=startupinfo,
        )

        if result.stdout:
            terminal_callback(result.stdout)
        if result.stderr:
            terminal_callback(result.stderr)

        if result.returncode == 0:
            terminal_callback(f"\nCompilation successful -> {self.output_name}\n")
            return True

        terminal_callback(f"\nCompilation failed (exit code {result.returncode})\n")
        return False

    def _find_dump_files(self, search_dir):
        """Find waveform dump files (.vcd, .fst, .lxt, .ghw, .vcd.gz) in search_dir."""
        if not search_dir or not os.path.isdir(search_dir):
            return []
        patterns = ["*.vcd", "*.fst", "*.lxt", "*.lxt2", "*.ghw", "*.vcd.gz"]
        found = []
        for p in patterns:
            found.extend(glob.glob(os.path.join(search_dir, p)))
        found.extend(glob.glob(os.path.join(search_dir, "**", "dump.vcd")))
        found.extend(glob.glob(os.path.join(search_dir, "**", "*.vcd")))
        return sorted(set(found))

    def _latest_dump(self, search_dir):
        files = self._find_dump_files(search_dir)
        if not files:
            return None
        return max(files, key=os.path.getmtime)

    def run(self, terminal_callback):
        root = self.root_dir
        if not root:
            terminal_callback("No project or file open.\n")
            return False

        if not self.vvp_available():
            terminal_callback(f"vvp not found at {self._vvp_path}\n")
            return False

        build_dir = os.path.join(root, self.build_dir_name)
        output_path = os.path.join(build_dir, self.output_name)

        if not os.path.isfile(output_path):
            terminal_callback("No compiled simulation found. Compile first.\n")
            return False

        cmd = [self._vvp_path, output_path]
        terminal_callback(f"{' '.join(cmd)}\n\n")

        env = os.environ.copy()
        env["PATH"] = os.path.join(HDLSTUDIO_ROOT, "iverilog", "bin") + os.pathsep + env.get("PATH", "")

        startupinfo = None
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=root,
            env=env,
            startupinfo=startupinfo,
        )

        if result.stdout:
            terminal_callback(result.stdout + "\n")
        if result.stderr:
            terminal_callback("[STDERR] " + result.stderr + "\n")

        if result.returncode == 0:
            terminal_callback("Simulation finished successfully.\n")

            self.last_vcd_path = self._latest_dump(root)
            if not self.last_vcd_path:
                self.last_vcd_path = self._latest_dump(build_dir)

            if self.last_vcd_path:
                terminal_callback(
                    f"\n>> Waveform: {os.path.basename(self.last_vcd_path)}\n"
                    f"   Press F7 or click View Waves to open\n"
                )
            else:
                terminal_callback(
                    "\n>> No waveform (.vcd) generated.\n"
                    "   Make sure your testbench includes:\n"
                    '     initial begin\n'
                    '         $dumpfile("dump.vcd");\n'
                    '         $dumpvars(0, testbench_name);\n'
                    '     end\n'
                )
            return True

        terminal_callback(f"Simulation exited with code {result.returncode}\n")
        return False