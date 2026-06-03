import os
import glob
import subprocess
import tempfile
import shutil


HDLSTUDIO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class BuildSystem:

    SIM_ICARUS = "icarus"
    SIM_VERILATOR = "verilator"

    def __init__(self, project):
        self.project = project
        self.working_dir = None
        self.module_file = None
        self.testbench_file = None
        self.output_name = "simulation.vvp"
        self.build_dir_name = "build"
        self.last_vcd_path = None
        self.simulator = self.SIM_ICARUS

    @property
    def _iverilog_path(self):
        return os.path.join(HDLSTUDIO_ROOT, "tools", "iverilog", "bin", "iverilog.exe")

    @property
    def _vvp_path(self):
        return os.path.join(HDLSTUDIO_ROOT, "tools", "iverilog", "bin", "vvp.exe")

    @property
    def root_dir(self):
        if self.project and self.project.is_loaded():
            return self.project.root_path
        return self.working_dir

    def iverilog_available(self):
        return os.path.isfile(self._iverilog_path)

    def vvp_available(self):
        return os.path.isfile(self._vvp_path)

    def _find_verilator_cmd(self):
        direct = shutil.which("verilator")
        if direct:
            return [direct]
        startupinfo = None
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        try:
            result = subprocess.run(
                ["wsl", "verilator", "--version"],
                capture_output=True, text=True, timeout=15,
                startupinfo=startupinfo
            )
            if result.returncode == 0:
                return ["wsl", "verilator"]
        except Exception:
            pass
        return None

    def _win_to_wsl_path(self, win_path):
        win_path = os.path.normpath(win_path)
        drive = win_path[0].lower()
        rest = win_path[3:].replace("\\", "/")
        return f"/mnt/{drive}/{rest}"

    def _wsl_run(self, cmd_list):
        startupinfo = None
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        return subprocess.run(
            ["wsl"] + cmd_list,
            capture_output=True, text=True,
            startupinfo=startupinfo,
        )

    def verilator_available(self):
        return self._find_verilator_cmd() is not None

    _SKIP_DIRS = {"tools", ".venv", ".git", "__pycache__"}

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

    def _gather_sources(self, terminal_callback):
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
        return sources

    def compile(self, terminal_callback, output_path=None):
        if self.simulator == self.SIM_VERILATOR:
            return self._compile_verilator(terminal_callback, output_path)
        return self._compile_icarus(terminal_callback, output_path)

    def _compile_icarus(self, terminal_callback, output_path=None):
        root = self.root_dir
        if not root:
            terminal_callback("No project or file open.\n")
            return False

        if not self.iverilog_available():
            terminal_callback(
                f"iverilog not found at {self._iverilog_path}\n"
                "Make sure Icarus Verilog is bundled in the tools/iverilog/ directory.\n"
            )
            return False

        sources = self._gather_sources(terminal_callback)
        if not sources:
            return False

        if output_path:
            out_dir = os.path.dirname(output_path)
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)
        else:
            build_dir = os.path.join(root, self.build_dir_name)
            os.makedirs(build_dir, exist_ok=True)
            output_path = os.path.join(build_dir, self.output_name)

        cmd = [self._iverilog_path, "-o", output_path, "-g2012"] + sources
        terminal_callback(f"{' '.join(cmd)}\n\n")

        env = os.environ.copy()
        env["PATH"] = os.path.join(HDLSTUDIO_ROOT, "tools", "iverilog", "bin") + os.pathsep + env.get("PATH", "")

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
            name = os.path.basename(output_path)
            terminal_callback(f"\nCompilation successful -> {name}\n")
            return True

        terminal_callback(f"\nCompilation failed (exit code {result.returncode})\n")
        return False

    def _compile_verilator(self, terminal_callback, output_path=None):
        root = self.root_dir
        if not root:
            terminal_callback("No project or file open.\n")
            return False

        verilator_cmd = self._find_verilator_cmd()
        if not verilator_cmd:
            terminal_callback("verilator not found.\nInstall Verilator (on PATH or via WSL) and try again.\n")
            return False

        sources = self._gather_sources(terminal_callback)
        if not sources:
            return False

        if not self.testbench_file:
            terminal_callback("A testbench file must be selected for Verilator.\n")
            return False

        tb_base = os.path.splitext(os.path.basename(self.testbench_file))[0]
        build_dir = os.path.join(root, self.build_dir_name)
        os.makedirs(build_dir, exist_ok=True)

        if verilator_cmd == ["wsl", "verilator"]:
            # Build inside WSL tmp to avoid NTFS performance/compatibility issues.
            # The executable will be copied back to build/verilator_obj/ afterwards.
            import uuid
            ws = f"/tmp/hdl_vl_{uuid.uuid4().hex[:8]}"
            wsl_tmp = ws

            # Copy sources into WSL tmp
            self._wsl_run(["mkdir", "-p", wsl_tmp])
            for s in sources:
                self._wsl_run(["cp", self._win_to_wsl_path(s), f"{wsl_tmp}/{os.path.basename(s)}"])

            src_args = [f"{wsl_tmp}/{os.path.basename(s)}" for s in sources]
            mdir_arg = f"{wsl_tmp}/obj_dir"

            VL_FLAGS = ["--binary", "--trace", "-j", "4", "-Wno-fatal"]
            full_cmd = verilator_cmd + VL_FLAGS + [
                "--top-module", tb_base,
                "-Mdir", mdir_arg,
            ] + src_args
            terminal_callback(f"{' '.join(full_cmd)}\n\n")
        else:
            src_args = sources[:]
            mdir_arg = os.path.join(build_dir, "verilator_obj")
            VL_FLAGS = ["--binary", "--trace", "-j", "4", "-Wno-fatal"]
            full_cmd = verilator_cmd + VL_FLAGS + [
                "--top-module", tb_base,
                "-Mdir", mdir_arg,
            ] + src_args
            terminal_callback(f"{' '.join(full_cmd)}\n\n")

        startupinfo = None
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        result = subprocess.run(
            full_cmd,
            capture_output=True,
            text=True,
            cwd=root,
            startupinfo=startupinfo,
        )

        if result.stdout:
            terminal_callback(result.stdout)
        if result.stderr:
            terminal_callback(result.stderr)

        if result.returncode == 0:
            exe_name = f"V{tb_base}"
            if verilator_cmd == ["wsl", "verilator"]:
                # Copy executable back to Windows
                wsl_exe_src = f"{wsl_tmp}/obj_dir/{exe_name}"
                tmp_dst = os.path.join(build_dir, "verilator_obj")
                os.makedirs(tmp_dst, exist_ok=True)
                local_exe = os.path.join(tmp_dst, exe_name)
                self._wsl_run(["cp", wsl_exe_src, self._win_to_wsl_path(local_exe)])
                self._wsl_run(["rm", "-rf", wsl_tmp])
                final_path = output_path or local_exe
                if output_path and os.path.normpath(output_path) != os.path.normpath(local_exe):
                    import shutil
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    shutil.copy2(local_exe, output_path)
            else:
                final_path = output_path or os.path.join(build_dir, "verilator_obj", exe_name)
                if output_path:
                    import shutil
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    shutil.copy2(os.path.join(build_dir, "verilator_obj", exe_name), output_path)
            terminal_callback(f"\nVerilator compilation successful -> {final_path}\n")
            return True

        terminal_callback(f"\nVerilator compilation failed (exit code {result.returncode})\n")
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

    def run(self, terminal_callback, sim_path=None):
        if self.simulator == self.SIM_VERILATOR:
            return self._run_verilator(terminal_callback, sim_path)
        return self._run_icarus(terminal_callback, sim_path)

    def _run_icarus(self, terminal_callback, vvp_path=None):
        root = self.root_dir
        if not root:
            terminal_callback("No project or file open.\n")
            return False

        if not self.vvp_available():
            terminal_callback(f"vvp not found at {self._vvp_path}\n")
            return False

        build_dir = os.path.join(root, self.build_dir_name)

        if not vvp_path:
            vvp_path = os.path.join(build_dir, self.output_name)

        if not os.path.isfile(vvp_path):
            terminal_callback("No compiled simulation found. Compile first.\n")
            return False

        cmd = [self._vvp_path, vvp_path]
        terminal_callback(f"{' '.join(cmd)}\n\n")

        env = os.environ.copy()
        env["PATH"] = os.path.join(HDLSTUDIO_ROOT, "tools", "iverilog", "bin") + os.pathsep + env.get("PATH", "")

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

            return True

        terminal_callback(f"Simulation exited with code {result.returncode}\n")
        return False

    def _run_verilator(self, terminal_callback, exe_path=None):
        root = self.root_dir
        if not root:
            terminal_callback("No project or file open.\n")
            return False

        build_dir = os.path.join(root, self.build_dir_name)

        if not exe_path:
            if not self.testbench_file:
                terminal_callback("No testbench selected – cannot determine Verilator executable.\n")
                return False
            tb_base = os.path.splitext(os.path.basename(self.testbench_file))[0]
            exe_name = f"V{tb_base}"
            exe_path = os.path.join(build_dir, "verilator_obj", exe_name)

        # The executable is a Linux ELF binary (built inside WSL),
        # so run it via wsl.exe, converting the Windows path to a WSL path.
        wsl_exe_path = self._win_to_wsl_path(exe_path)
        wsl_root = self._win_to_wsl_path(root)

        cmd = ["wsl", wsl_exe_path]
        terminal_callback(f"{' '.join(cmd)}\n\n")

        startupinfo = None
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=root,
            startupinfo=startupinfo,
        )

        if result.stdout:
            terminal_callback(result.stdout + "\n")
        if result.stderr:
            terminal_callback("[STDERR] " + result.stderr + "\n")

        if result.returncode == 0:
            terminal_callback("Verilator simulation finished successfully.\n")

            self.last_vcd_path = self._latest_dump(root)
            if not self.last_vcd_path:
                self.last_vcd_path = self._latest_dump(build_dir)

            return True

        terminal_callback(f"Verilator simulation exited with code {result.returncode}\n")
        return False

    def yosys_available(self):
        try:
            from yowasp_yosys import run_yosys
            return True
        except ImportError:
            return False

    def _synth_script_for(self, read_cmd, output_ext):
        """Return the yosys synth script based on the output file extension."""
        scripts = {
            ".blif": f"{read_cmd} {{input}}; synth; write_blif {{output}}",
            ".json": f"{read_cmd} {{input}}; synth_ice40 -json {{output}}",
            ".v":    f"{read_cmd} {{input}}; synth; write_verilog {{output}}",
            ".edif": f"{read_cmd} {{input}}; synth; write_edif {{output}}",
        }
        return scripts.get(output_ext, f"{read_cmd} {{input}}; synth; write_blif {{output}}")

    def synthesize(self, terminal_callback, filepath, output_path=None, synth_script=None):
        if not self.yosys_available():
            terminal_callback("yowasp-yosys not installed. Run: pip install yowasp-yosys\n")
            return False

        if not os.path.isfile(filepath):
            terminal_callback(f"File not found: {filepath}\n")
            return False

        ext = os.path.splitext(filepath)[1].lower()
        if ext in (".v", ".sv"):
            read_cmd = "read_verilog"
        elif ext in (".vhd", ".vhdl"):
            read_cmd = "read_vhdl"
        else:
            terminal_callback(f"Unsupported file type: {ext}\n")
            return False

        from yowasp_yosys import run_yosys

        src_name = os.path.basename(filepath)
        base = os.path.splitext(src_name)[0]

        if output_path is None:
            out_dir = tempfile.mkdtemp(prefix="yosys_")
        else:
            out_dir = os.path.dirname(output_path)
            os.makedirs(out_dir, exist_ok=True)

        out_ext = os.path.splitext(output_path)[1].lower() if output_path else ".blif"

        if synth_script is None:
            synth_script = self._synth_script_for(read_cmd, out_ext)

        work_dir = tempfile.mkdtemp(prefix="synth_")
        try:
            shutil.copy2(filepath, os.path.join(work_dir, src_name))
            orig_cwd = os.getcwd()
            os.chdir(work_dir)

            out_name = f"{base}{out_ext}"
            script = synth_script.replace("{input}", src_name).replace("{output}", out_name)

            terminal_callback(f"Running yosys on {src_name}...\n")
            terminal_callback(f"  Script: {script}\n\n")

            try:
                run_yosys(["-p", script])
            except SystemExit:
                pass
            except Exception as e:
                terminal_callback(f"Yosys error: {e}\n")
                os.chdir(orig_cwd)
                return False

            os.chdir(orig_cwd)

            out_file = os.path.join(work_dir, out_name)
            if os.path.isfile(out_file):
                if output_path:
                    shutil.copy2(out_file, output_path)
                    terminal_callback(f"\nSynthesis output saved: {output_path}\n")
                else:
                    with open(out_file) as f:
                        terminal_callback(f"\n--- {out_name} ---\n")
                        terminal_callback(f.read())
                return True
            else:
                # Check for other output formats
                for f in os.listdir(work_dir):
                    if f != src_name:
                        terminal_callback(f"\nOutput file: {f}\n")
                        with open(os.path.join(work_dir, f)) as fh:
                            terminal_callback(fh.read())
                return True
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)