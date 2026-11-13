"""Standalone native build/install driver copied into each deployment kit."""
import json
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import sys
import time
import venv

ROOT=Path(__file__).resolve().parent

def call(args,**kwargs):
    kwargs.setdefault('env',{**os.environ,'PYINSTALLER_CONFIG_DIR':str(ROOT/'.pyinstaller-cache'),'PIP_CACHE_DIR':str(ROOT/'.pip-cache')})
    subprocess.run([str(a) for a in args],check=True,cwd=ROOT,**kwargs)

def main(action=None):
    action=action or (sys.argv[1] if len(sys.argv)>1 else 'build')
    if action not in ('run','build','install'):raise ValueError('Expected run, build or install')
    if sys.version_info[:2]<(3,15) or sys.version_info.releaselevel!='final':raise RuntimeError('Stable Python 3.15+ with Tkinter is required.')
    if sys.platform not in ('darwin','win32'):raise RuntimeError('Native build requires macOS or Windows.')
    import tkinter
    meta=json.loads((ROOT/'deploy.json').read_text());name=meta['name'];version=meta['version']
    env=ROOT/'.venv';python=env/('Scripts/python.exe' if sys.platform=='win32' else 'bin/python')
    if not python.exists():venv.EnvBuilder(with_pip=True).create(env)
    call([python,'-c','import sys,tkinter; assert sys.version_info[:2]>=(3,15) and sys.version_info.releaselevel=="final", "Stable Python 3.15+ required"'])
    call([python,'-m','pip','install','-r',ROOT/'requirements.txt'])
    if action=='run':return call([python,ROOT/'src/main.py'])
    call([python,'-m','pip','install','PyInstaller>=6'])
    extras=list(meta.get('packaging_flags',[]))
    icon=meta.get('icons',{}).get('mac' if sys.platform=='darwin' else 'windows')
    if icon:
        icon_path=(ROOT/icon).resolve()
        if not icon_path.is_relative_to(ROOT.resolve()) or not icon_path.is_file():raise ValueError('Missing or invalid build icon.')
        extras+=['--icon',str(icon_path)]
    specs=(ROOT/'requirements.txt').read_text().lower()
    if 'psycopg' in specs:extras+=['--hidden-import=sqlalchemy.dialects.postgresql.psycopg','--collect-all=psycopg','--collect-all=psycopg_binary']
    if 'pymysql' in specs:extras+=['--hidden-import=sqlalchemy.dialects.mysql.pymysql','--collect-all=pymysql']
    for file in (ROOT/'src').glob('*.py'):
        if file.stem!='main' and file.stem.isidentifier():extras+=['--hidden-import='+file.stem]
    for folder in (ROOT/'src').iterdir():
        if folder.is_dir() and (folder/'__init__.py').exists() and folder.name.isidentifier():extras+=['--collect-submodules='+folder.name]
    call([python,'-m','PyInstaller','--noconfirm','--clean','--windowed','--name',name,'--distpath',ROOT/'dist','--workpath',ROOT/'build','--specpath',ROOT,'--paths',ROOT/'src','--add-data',str(ROOT/'src')+':.',*extras,ROOT/'src/main.py'])
    installers=ROOT/'installers';installers.mkdir(exist_ok=True)
    if sys.platform=='darwin':
        app=ROOT/'dist'/(name+'.app');info=app/'Contents/Info.plist';data=plistlib.loads(info.read_bytes())
        data.update(CFBundleShortVersionString=version,CFBundleVersion=version,NSCameraUsageDescription='This application uses the camera when its webcam component is started.')
        info.write_bytes(plistlib.dumps(data));call(['codesign','--force','--deep','--sign','-',app])
        dmg=installers/(name+'-'+version+'.dmg')
        try:call(['hdiutil','create','-volname',name,'-srcfolder',app,'-ov','-format','UDZO',dmg])
        except (OSError,subprocess.CalledProcessError) as exc:
            print('DMG unavailable; preserving the app and creating a ZIP instead:',exc)
            call(['ditto','-c','-k','--sequesterRsrc','--keepParent',app,installers/(name+'-'+version+'-mac.zip')])
        if action=='install':
            target=Path.home()/'Applications'/(name+'.app');target.parent.mkdir(exist_ok=True)
            if target.exists():target.rename(target.with_name(name+'-backup-'+str(time.time_ns())+'.app'))
            shutil.copytree(app,target);print('Installed:',target)
    else:
        shutil.make_archive(str(installers/(name+'-'+version+'-portable')),'zip',ROOT/'dist',name)
        compiler=shutil.which('ISCC')
        if not compiler:
            for base in [os.environ.get('ProgramFiles(x86)'),os.environ.get('ProgramFiles'),os.environ.get('LOCALAPPDATA')]:
                if base:
                    for suffix in ['Inno Setup 6/ISCC.exe','Inno Setup 7/ISCC.exe','Programs/Inno Setup 6/ISCC.exe','Programs/Inno Setup 7/ISCC.exe']:
                        candidate=Path(base)/suffix
                        if candidate.is_file():compiler=str(candidate);break
                    if compiler:break
        if compiler:
            call([compiler,ROOT/'Installer_Windows.iss'])
            if action=='install':call([installers/(name+'-'+version+'-Setup.exe')])
        else:
            print('Portable build ready. Install Inno Setup to generate the Windows installer: https://jrsoftware.org/isinfo.php')
            if action=='install':raise RuntimeError('Inno Setup is required for this install action. The portable build is ready.')
    print('Build completed:',ROOT/'dist','— installers:',installers)

if __name__=='__main__':main()
