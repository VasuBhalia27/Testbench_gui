"""
Common Trace32 helper for backend adapters.

Provides simple functions to connect to Trace32 and read variables.
Adapters should import and call `read_variable(var_name)`.
"""
import time
from typing import Optional
import os
import subprocess
import shutil
import platform
from pathlib import Path
import tempfile
import re
try:
    import winreg
except Exception:
    winreg = None

_dbg = None
_connected = False


def ensure_connected() -> bool:
    """Ensure connection to Trace32 debugger (localhost:20006)."""
    global _dbg, _connected
    if _connected and _dbg is not None:
        return True

    # Allow overriding host/port via environment for portability
    host = os.environ.get('TRACE32_HOST', 'localhost')
    port = int(os.environ.get('TRACE32_PORT', '20006'))
    
    print(f"[DEBUG] Attempting to connect to Trace32 at {host}:{port}...")
    
    try:
        import lauterbach.trace32.rcl as t32
        print(f"[DEBUG] Lauterbach library imported successfully")
        _dbg = t32.connect(node=host, port=port, protocol='UDP', packlen=1024, timeout=5.0)
        _connected = _dbg is not None
        if _connected:
            print(f"[DEBUG] Successfully connected to Trace32!")
        else:
            print(f"[DEBUG] t32.connect() returned None")
        return _connected
    except ImportError as e:
        print(f"[ERROR] Failed to import lauterbach library: {e}")
        print(f"[ERROR] Is lauterbach library installed?")
        _connected = False
        return False
    except Exception as e:
        print(f"[ERROR] Failed to connect to Trace32: {type(e).__name__}: {e}")
        print(f"[ERROR] Tried connecting to {host}:{port}")
        _connected = False
        return False


def send_test_command(did_cmd: int) -> bool:
    """Send DID test command to firmware via Trace32.
    
    Args:
        did_cmd: DID command number (e.g., 101 for LED test)
    
    Returns:
        True if command sent successfully, False otherwise
    """
    global _dbg
    if not ensure_connected():
        print(f"[ERROR] Cannot send command - not connected to Trace32")
        return False
    try:
        print(f"[DEBUG] Sending DID command: {did_cmd}")
        _dbg.cmd(f'Var.set TestFw_GuiCmd = {did_cmd}')
        # Increase wait to give firmware more time to act
        time.sleep(0.8)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send DID command {did_cmd}: {type(e).__name__}: {e}")
        return False


def get_debugger():
    """Get the global debugger reference."""
    global _dbg
    if not ensure_connected():
        return None
    return _dbg


def read_variable(var_name: str) -> Optional[float]:
    """Read a numeric variable from Trace32. Returns None on failure.

    Note: many firmware variables are provided in scaled units (mV, mA).
    Adapter code can convert to final units where required.
    """
    global _dbg
    if not ensure_connected():
        print(f"[DEBUG] Cannot read {var_name} - not connected to Trace32")
        return None

    # Custom exception to signal missing symbol in ELF
    class SymbolNotFoundError(Exception):
        pass

    attempts = 3
    delay = 0.2
    last_exc = None
    for attempt in range(1, attempts + 1):
        try:
            print(f"[DEBUG] Reading variable: {var_name} (attempt {attempt})")
            val = _dbg.fnc(f"Var.VALUE({var_name})")
            if val is None:
                print(f"[DEBUG] Variable {var_name} returned None")
                last_exc = None
                time.sleep(delay)
                continue
            result = float(val)
            print(f"[DEBUG] Variable {var_name} = {result}")
            return result
        except Exception as e:
            msg = str(e).lower()
            # Detect symbol-not-found from Lauterbach error message
            if "symbol not found" in msg or "functionerror" in msg:
                print(f"[ERROR] Variable {var_name}: symbol not found in ELF ({e})")
                # Return None for missing symbols so higher-level test suites
                # can continue and mark values as unavailable instead of
                # raising an exception that aborts the entire run.
                return None
            # Otherwise retry a few times for transient issues
            print(f"[WARNING] Read attempt {attempt} for {var_name} failed: {type(e).__name__}: {e}")
            last_exc = e
            time.sleep(delay)

    # If we reach here, all attempts exhausted
    if last_exc:
        print(f"[ERROR] Failed to read {var_name} after {attempts} attempts: {type(last_exc).__name__}: {last_exc}")
    else:
        print(f"[DEBUG] Variable {var_name} unavailable after {attempts} attempts")
    return None


def set_variable(var_name: str, value) -> bool:
    """Set a variable on the target via Trace32.

    Args:
        var_name: Variable name to set (without surrounding syntax)
        value: Value to write (int/float/bool)

    Returns:
        True on success, False on failure
    """
    global _dbg
    if not ensure_connected():
        print(f"[ERROR] Cannot set {var_name} - not connected to Trace32")
        return False
    try:
        # Use dbg.cmd to set the variable exactly as GUI does
        _dbg.cmd(f'Var.set {var_name} = {value}')
        # brief pause to let firmware see the change
        time.sleep(0.05)
        print(f"[DEBUG] Set variable {var_name} = {value}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to set {var_name} = {value}: {type(e).__name__}: {e}")
        return False


def start_powerview(powerview_path: str, args: list | None = None) -> bool:
    """
    Launch Lauterbach PowerView (Trace32) if installed locally.

    Args:
        powerview_path: Full path to the PowerView executable.

    Returns:
        True if the process was launched successfully, False otherwise.
    """
    # If a full path is provided, try it first
    try:
        if powerview_path:
            p = Path(powerview_path)
            if p.exists():
                cmd = [str(p)] + (args or [])
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True

        # Try to find a known PowerView/Trace32 executable on PATH
        candidates = [
            'PowerView.exe',
            'TRACE32.exe',
            'Trace32.exe',
            'pv.exe',
            'PowerView'
        ]
        for name in candidates:
            exe = shutil.which(name)
            if exe:
                cmd = [exe] + (args or [])
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True

        # Check common environment variables and standard install directories
        env_vars = ['TRACE32_HOME', 'TRACE32_DIR', 'LAUTERBACH', 'LAUTERBACH_DIR']
        for ev in env_vars:
            p = os.environ.get(ev)
            if p:
                candidate = Path(p) / 'PowerView.exe'
                if candidate.exists():
                    cmd = [str(candidate)] + (args or [])
                    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return True

        # Common Windows install locations
        common_paths = [
            r'C:\Program Files\Lauterbach',
            r'C:\Program Files (x86)\Lauterbach',
            r'C:\Program Files\Lauterbach\PowerView',
            r'C:\Program Files (x86)\Lauterbach\PowerView'
        ]
        for base in common_paths:
            try:
                basep = Path(base)
                if basep.exists():
                    for exe in basep.rglob('PowerView*.exe'):
                        cmd = [str(exe)] + (args or [])
                        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        return True
            except Exception:
                continue

        # Avoid broad recursive searches (can be very slow on some machines).
        # We've already checked common install locations above; skip exhaustive ProgramFiles scans.

        # Try probing Windows registry for Lauterbach install entries
        if platform.system() == 'Windows' and winreg is not None:
            try:
                # Search HKLM for keys containing 'Lauterbach' and try their values
                hives = [(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_64KEY),
                         (winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_32KEY)]
                for hive, flag in hives:
                    try:
                        with winreg.OpenKey(hive, r"SOFTWARE", 0, winreg.KEY_READ | flag) as so:
                            # Enumerate subkeys and look for Lauterbach entries
                            i = 0
                            while True:
                                try:
                                    sub = winreg.EnumKey(so, i)
                                    if 'Lauterbach' in sub or 'TRACE32' in sub.upper():
                                        try:
                                            with winreg.OpenKey(hive, r"SOFTWARE\\%s" % sub, 0, winreg.KEY_READ | flag) as k:
                                                try:
                                                    install = winreg.QueryValueEx(k, 'InstallDir')[0]
                                                except Exception:
                                                    try:
                                                        install = winreg.QueryValueEx(k, 'InstallPath')[0]
                                                    except Exception:
                                                        install = None
                                                if install:
                                                    candidate = Path(install) / 'PowerView.exe'
                                                    if candidate.exists():
                                                        subprocess.Popen([str(candidate)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                                                        return True
                                        except Exception:
                                            pass
                                    i += 1
                                except OSError:
                                    break
                    except Exception:
                        continue
            except Exception:
                pass

        # On non-Windows platforms, attempt generic names on PATH
        if platform.system() != 'Windows':
            exe = shutil.which('PowerView') or shutil.which('trace32')
            if exe:
                subprocess.Popen([exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True

        return False
    except Exception:
        return False


def start_and_connect(powerview_path: Optional[str] = None, host: str = 'localhost', port: int = 20006, retries: int = 5, delay: float = 1.0, start_target: bool = True) -> bool:
    """
    Try to start PowerView (optional) and connect to Trace32's RCL server.

    This will attempt to launch PowerView if `powerview_path` is provided, then repeatedly
    call `ensure_connected()` until successful or retries exhausted. Optionally call
    a debugger command to start the target (`Go`) if `start_target` is True.

    Returns True when connected, False otherwise.
    """
    # Optionally launch PowerView (try autodiscovery if no path provided)
    try:
        repo = os.environ.get('TRACE32_REPO_PATH')
        # If not explicitly provided, try to discover the repo using the
        # fixed suffix used by the GUI: Testbench_gui_Charan\SmartBU
        if not repo:
            discovered = find_gui_repo_by_suffix()
            if discovered:
                repo = discovered
                # set in-env so subsequent logic can reuse it
                os.environ['TRACE32_REPO_PATH'] = repo
        preset = int(os.environ.get('TRACE32_PRESET', '1'))
        config_path = os.environ.get('TRACE32_CONFIG_PATH')

        # If repo is provided, attempt to launch using the same sequence as the GUI
        if repo:
            try:
                launch_trace32_like_gui(repo, preset=preset, powerview_path=powerview_path, config_path=config_path)
            except Exception:
                # Fallback to generic launcher
                start_powerview(powerview_path)
        else:
            # No repo provided — try generic launch
            start_powerview(powerview_path)
    except Exception:
        pass

    # Respect environment overrides for host/port if present
    env_host = os.environ.get('TRACE32_HOST')
    env_port = os.environ.get('TRACE32_PORT')
    if env_host:
        host = env_host
    if env_port:
        try:
            port = int(env_port)
        except Exception:
            pass

    # Try to connect repeatedly
    for _ in range(retries):
        if ensure_connected():
            try:
                if start_target and _dbg is not None:
                    try:
                        _dbg.cmd('Go')
                    except Exception:
                        pass
                return True
            except Exception:
                return True
        time.sleep(delay)

    return False


def _replace_line_starting_with(file_path: Path, prefix: str, new_line: str) -> None:
    fd, tmpname = None, None
    dirn = os.path.dirname(str(file_path)) or "."
    try:
        fd, tmpname = tempfile.mkstemp(dir=dirn)
        with os.fdopen(fd, 'w', encoding='utf-8') as fout, open(file_path, 'r', encoding='utf-8', errors='ignore') as fin:
            for line in fin:
                if line.lstrip().startswith(prefix):
                    fout.write(new_line + '\n')
                else:
                    fout.write(line)
        os.replace(tmpname, str(file_path))
    except Exception:
        if tmpname and os.path.exists(tmpname):
            os.remove(tmpname)
        raise


def _edit_flash_cmm(flash_cmm_path: Path, repo_path: Path, preset: int) -> Path:
    # Create a copy and replace Data.LOAD.Elf with the selected ELF path
    new_path = flash_cmm_path.with_name(flash_cmm_path.stem + '_automation' + flash_cmm_path.suffix)
    shutil.copy(str(flash_cmm_path), str(new_path))

    if preset == 1:
        elf_rel = Path('Non_Nfc_Test') / 'XNF-Handle_NonDriver_C2_App.elf'
    else:
        elf_rel = Path('Nfc_Test') / 'XNF-Handle_Driver_C2_App.elf'

    elf_path = repo_path.joinpath(elf_rel)
    elf_path_str = str(elf_path).replace('/', '\\')
    _replace_line_starting_with(new_path, 'Data.LOAD.Elf', 'Data.LOAD.Elf ' + elf_path_str)
    return new_path


def _edit_autoexec_cmm(autoexec_cmm_path: Path) -> Path:
    new_path = autoexec_cmm_path.with_name(autoexec_cmm_path.stem + '_automation' + autoexec_cmm_path.suffix)
    shutil.copy(str(autoexec_cmm_path), str(new_path))
    # Replace any line that references flash.cmm with flash_automation.cmm
    try:
        fd, tmpname = tempfile.mkstemp(dir=str(new_path.parent))
        with os.fdopen(fd, 'w', encoding='utf-8') as fout, open(new_path, 'r', encoding='utf-8', errors='ignore') as fin:
            pattern = re.compile(r'DO\s*[~\s]*\\flash\.cmm', re.IGNORECASE)
            for line in fin:
                if pattern.search(line):
                    fout.write('DO ~~~~\\flash_automation.cmm\n')
                else:
                    fout.write(line)
        os.replace(tmpname, str(new_path))
    except Exception:
        if tmpname and os.path.exists(tmpname):
            os.remove(tmpname)
        raise
    return new_path


def find_trace32_executable() -> Optional[str]:
    # Prefer explicit env var
    pv = os.environ.get('TRACE32_POWERVIEW_PATH')
    if pv and Path(pv).exists():
        return pv

    # Check common user conan path used by GUI
    user_path = str(Path.home())
    possible = Path(user_path) / '.conan2'
    if possible.exists():
        for p in possible.rglob('t32marm.exe'):
            return str(p)

    # Fall back to PATH search
    for name in ('t32marm.exe', 'PowerView.exe', 'TRACE32.exe'):
        exe = shutil.which(name)
        if exe:
            return exe

    return None


def find_gui_repo_by_suffix(suffix: str = r"Testbench_gui_Charan\\SmartBU") -> Optional[str]:
    """Find a repository path that ends with the given fixed suffix.

    The search is constrained to the current working directory tree to avoid
    scanning entire drives. Returns the first matching absolute path or None.
    """
    try:
        cwd = Path.cwd()
        # Look for direct parent-match first (handles case where cwd is inside the repo)
        for p in [cwd] + list(cwd.parents):
            if str(p).replace('/', '\\').endswith(suffix):
                return str(p)

        # Otherwise search the workspace tree for a folder matching the suffix
        # Limit the rglob to the current workspace to avoid expensive system-wide scans
        pattern = Path('**') / Path(suffix)
        for match in cwd.rglob(suffix.split('\\')[-1]):
            # Reconstruct candidate path ending with the full suffix
            candidate = match
            try:
                # Walk up to see if parent chain contains the full suffix
                parts = []
                p = candidate
                for _ in range(6):  # don't climb more than 6 levels
                    parts.insert(0, p.name)
                    p = p.parent
                    if str(Path(*parts)).replace('/', '\\').endswith(suffix.split('\\')[-1]):
                        pass
                # Try to build candidate by checking parents for the full suffix
                candidate_full = None
                p = match
                # Walk up building tail until it matches the suffix start
                tail = ''
                while True:
                    tail = os.path.join(p.name, tail) if tail else p.name
                    if tail.replace('/', '\\').endswith(suffix.split('\\')[-1]):
                        # assemble potential full path by walking further up
                        # attempt to see if the parent chain ends with the full suffix
                        possible = str(match)
                        if possible.replace('/', '\\').endswith(suffix):
                            candidate_full = possible
                            break
                    if p.parent == p:
                        break
                    p = p.parent
                    if len(str(p)) < 3:
                        break
                if candidate_full:
                    return candidate_full
            except Exception:
                continue
    except Exception:
        return None
    return None


def launch_trace32_like_gui(repo_path: str, preset: int = 1, powerview_path: Optional[str] = None, config_path: Optional[str] = None) -> bool:
    """Replicate the GUI's LaunchTrace32 behaviour from `Functional/trace32.py`.

    Steps:
    - Kill existing t32marm.exe
    - Find autoexec.cmm and flash.cmm under repo Tests/DebuggerScripts
    - Create automation copies and edit flash to set ELF, edit autoexec to call flash_automation
    - Optionally edit config.t32 if provided
    - Launch Trace32 executable with -c <config> -s <autoexec_automation.cmm>
    """
    try:
        # Kill existing process (Windows)
        if platform.system() == 'Windows':
            os.system('taskkill /F /IM t32marm.exe /T >nul 2>&1')
            time.sleep(2)

        repo_p = Path(repo_path)
        if not repo_p.exists():
            return False

        cmms_path = repo_p / 'Tests' / 'DebuggerScripts'
        if not cmms_path.exists():
            return False

        autoexec_cmm = None
        flash_cmm = None
        for p in cmms_path.rglob('*.cmm'):
            if p.name.lower() == 'autoexec.cmm':
                autoexec_cmm = p
            if p.name.lower() == 'flash.cmm':
                flash_cmm = p

        if not autoexec_cmm or not flash_cmm:
            return False

        new_flash = _edit_flash_cmm(flash_cmm, repo_p, preset)
        new_autoexec = _edit_autoexec_cmm(autoexec_cmm)

        # If config_path provided, use it; else try to find config.t32 in repo root
        cfg = None
        if config_path and Path(config_path).exists():
            cfg = str(Path(config_path))
        else:
            cfg_candidates = list(repo_p.rglob('config.t32'))
            if cfg_candidates:
                cfg = str(cfg_candidates[0])

        trace_exe = powerview_path or find_trace32_executable()
        if not trace_exe:
            return False

        cmd = [trace_exe]
        if cfg:
            cmd += ['-c', cfg]
        cmd += ['-s', str(new_autoexec)]

        subprocess.Popen(cmd)
        # give GUI time to initialize
        time.sleep(6)
        return True
    except Exception:
        return False
