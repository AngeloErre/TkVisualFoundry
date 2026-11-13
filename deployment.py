"""Prepare a portable source distribution; native builds run on each target OS."""
import json
from pathlib import Path
import re
import shutil
import tempfile
from core import generate
from components import requirements
from project_files import included_files,project_file
from deploy_icons import prepare_icons
from library_catalog import packaging_flags,theme_config

BUILD_HELPER=Path(__file__).with_name('deploy_build.py')

def mac_uninstall_script(name):
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,59}',name):raise ValueError('Invalid application name')
    return r'''#!/bin/bash
set -euo pipefail
app="$HOME/Applications/@NAME@.app"
owner="$HOME/Applications/.visualtk-@NAME@.sha256"
if [ ! -f "$owner" ] || [ -L "$owner" ] || [ -L "$app" ] || [ ! -d "$app" ]; then
  echo 'No recognized installation. Use the generated Install_Mac.command first.'; exit 1
fi
expected=$(cat "$owner")
actual=$(/usr/bin/shasum -a 256 "$app/Contents/MacOS/@NAME@" | /usr/bin/awk '{print $1}')
if [[ ! "$expected" =~ ^[a-f0-9]{64}$ ]] || [ "$actual" != "$expected" ]; then
  echo 'Application ownership changed; preserving files.'; exit 1
fi
echo 'Close @NAME@ before continuing. Data outside the app is preserved.'
read -r -p 'Move @NAME@ to Trash? [y/N]: ' answer
case "$answer" in y|Y|yes|s|si) ;; *) exit 0 ;; esac
mkdir -p "$HOME/.Trash"
mv "$app" "$HOME/.Trash/@NAME@-$(date +%Y%m%d-%H%M%S)-$$.app"
rm -f "$owner"
echo 'Moved to Trash. Personal data outside the app was preserved.'
'''.replace('@NAME@',name)

def export_deployment(project,project_path,destination,name,version):
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,59}',name):raise ValueError('Application name: letters, digits, _ and -, starting with a letter (max 60).')
    if not re.fullmatch(r'\d+(?:\.\d+){0,3}',version):raise ValueError('Version must contain 1–4 numeric parts.')
    source=generate(project);files=included_files(project,Path(project_path).resolve().parent)
    config=theme_config(project)
    if config['provider'] in ('azure','forest') and config.get('file') not in files:raise ValueError('Include the Tcl theme and its resource folder in project files.')
    reserved={'main.py','project.vtk.json','_visualtk_icon.png'}
    if reserved.intersection(files):raise ValueError('main.py and project.vtk.json are reserved deployment names.')
    parent=Path(destination).resolve();parent.mkdir(parents=True,exist_ok=True);target=parent/(name+'-'+version)
    if target.exists():raise FileExistsError('Choose a new output folder or version: '+str(target))
    for relative in project.get('files',[]):
        candidate=Path(project_path).resolve().parent/relative
        if candidate.is_dir() and target.is_relative_to(candidate.resolve()):raise ValueError('Output cannot be inside an included folder.')
    for path in files.values():
        if path.is_dir() or target.is_relative_to(path):raise ValueError('Output cannot be inside an included project folder.')
    temporary=Path(tempfile.mkdtemp(prefix='.visualtk-deploy-',dir=parent))
    try:
        src=temporary/'src';src.mkdir()
        for relative,path in files.items():
            out=src/relative;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,out)
        icons={};icon=project.get('deployment',{}).get('icon')
        if icon:
            icons=prepare_icons(project_file(Path(project_path).resolve().parent,icon),temporary)
            source=source.replace('        self.root.withdraw()', '        self.root.withdraw()\n        self._app_icon = tk.PhotoImage(file=str(Path(__file__).resolve().parent / "_visualtk_icon.png"))\n        self.root.iconphoto(True, self._app_icon)',1)
        prelude='import os, sys\nfrom pathlib import Path\nos.chdir(Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)))\n'
        (src/'main.py').write_text(prelude+source,encoding='utf-8')
        (temporary/'project.vtk.json').write_text(json.dumps(project,indent=2,ensure_ascii=False),encoding='utf-8')
        (temporary/'requirements.txt').write_text('\n'.join(requirements(project))+'\n',encoding='utf-8')
        (temporary/'deploy.json').write_text(json.dumps({'name':name,'version':version,'files':sorted(files),'packaging_flags':packaging_flags(project),'python_minimum':'3.15','project_language':project.get('language','it'),'icons':icons},indent=2),encoding='utf-8')
        shutil.copy2(BUILD_HELPER,temporary/'deploy_build.py')
        for filename,action in [('Run_Mac.command','run'),('Build_Mac.command','build'),('Install_Mac.command','install')]:
            (temporary/filename).write_text('#!/bin/bash\nset -euo pipefail\ncd "$(dirname "$0")"\nPYTHON_BIN="${VTS_PYTHON:-python3}"\nexec "$PYTHON_BIN" deploy_build.py '+action+'\n');(temporary/filename).chmod(0o755)
        for filename,action in [('Run_Windows.cmd','run'),('Build_Windows.cmd','build'),('Install_Windows.cmd','install')]:
            (temporary/filename).write_text('@echo off\ncd /d "%~dp0"\nif defined VTS_PYTHON (\n  "%VTS_PYTHON%" deploy_build.py '+action+'\n) else (\n  py -3 deploy_build.py '+action+'\n)\nif errorlevel 1 pause\n',encoding='utf-8')
        (temporary/'Uninstall_Mac.command').write_text(mac_uninstall_script(name));(temporary/'Uninstall_Mac.command').chmod(0o755)
        # Identifiers are restricted above, so they cannot inject Inno Setup directives.
        setup_icon='SetupIconFile=build-assets\\app.ico\n' if icons else ''
        (temporary/'Installer_Windows.iss').write_text(f'''[Setup]
{setup_icon}AppId=VisualTk.{name}
AppName={name}
AppVersion={version}
DefaultDirName={{localappdata}}\\Programs\\{name}
PrivilegesRequired=lowest
Uninstallable=yes
UninstallDisplayName={name}
OutputDir=installers
OutputBaseFilename={name}-{version}-Setup
Compression=lzma2
SolidCompression=yes
[Files]
Source: "dist\\{name}\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{{userprograms}}\\{name}"; Filename: "{{app}}\\{name}.exe"
''',encoding='utf-8')
        (temporary/'README_DEPLOY.md').write_text(f'''# {name} {version} — Deployment

This is a source/build kit, not a precompiled application. Build on the target OS and architecture with stable Python 3.15+ and Tkinter. Set VTS_PYTHON to a compatible Python executable if needed. Scripts create a private .venv and install declared requirements from PyPI. Internet access is required for initial setup.

- Run_Mac.command / Run_Windows.cmd: prepare dependencies and run the source.
- Build_Mac.command: build dist/{name}.app and installers/{name}-{version}.dmg on macOS (ZIP fallback if disk image creation is unavailable).
- Install_Mac.command: build and copy the app to ~/Applications; existing installations are preserved with a timestamp suffix.
- Build_Windows.cmd: build dist/{name}/{name}.exe, its supporting files, and a portable ZIP on Windows. If Inno Setup is installed, also build an installer in installers/.
- Uninstall_Mac.command: move the app installed by Install_Mac.command to Trash after ownership verification and confirmation. Manually copied apps can be moved to Trash in Finder.
- Windows Setup includes a native uninstaller in Windows Settings → Apps. Portable folders are not registered installations; remove their extracted files manually.
- Install_Windows.cmd: build and start that installer. Install Inno Setup from https://jrsoftware.org/isinfo.php if it is missing, then rerun.

Copy the entire app folder or portable ZIP, not just the exe. End users of native builds do not need Python. Compiled applications and installers are unsigned; distribution through Apple/Microsoft signing services is a separate step. Native libraries such as VLC, device drivers and camera permissions are separate requirements.

A selected application icon is converted to ICNS (macOS), ICO (Windows/Setup) and PNG (runtime windows), and included automatically.

Only explicitly included project files are copied. Verify that licenses, required resources and all imported Python packages are present. Declare extra libraries in the IDE PIP settings. Resource paths should be relative to the bundled source folder. Included files are resources: write persistent user data to a writable user folder, not the app bundle. Database credentials are not supplied by this kit. Test builds on a clean destination computer before distribution.

The build kit does not cross-compile Windows executables on a Mac or vice versa. Dynamic imports and native integrations may need custom PyInstaller hooks in deploy_build.py. src/ contains the exported code and selected files; project.vtk.json preserves the designer project.
''',encoding='utf-8')
        temporary.rename(target)
    except Exception:
        shutil.rmtree(temporary,ignore_errors=True);raise
    return target
