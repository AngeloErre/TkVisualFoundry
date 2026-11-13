"""Private project environments. Existing directories are never overwritten."""
from pathlib import Path
import shutil
import subprocess
from runtime_requirements import validate_interpreter

def environment_python(root):
    import sys
    folder=Path(root).resolve()/'.venv'
    if folder.is_symlink():raise ValueError('The project .venv cannot be a symbolic link.')
    return folder/('Scripts/python.exe' if sys.platform=='win32' else 'bin/python')

def create_environment(base_python,root):
    python=environment_python(root);folder=python.parent.parent
    if folder.exists():
        if not (folder/'pyvenv.cfg').is_file():raise ValueError('The existing .venv is not a virtual environment and will not be overwritten.')
        validate_interpreter(python);return str(python)
    validate_interpreter(base_python)
    folder.mkdir()  # Reserve atomically: a concurrent creation must not be overwritten.
    try:
        result=subprocess.run([str(base_python),'-m','venv',str(folder)],capture_output=True,text=True,timeout=120)
        if result.returncode:raise RuntimeError((result.stderr or result.stdout)[-2000:])
        validate_interpreter(python)
    except Exception:
        shutil.rmtree(folder);raise
    return str(python)
