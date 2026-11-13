"""Owned IDE installation and conservative uninstall planning. No project deletion."""
import argparse
import hashlib
import json
import os
from pathlib import Path,PurePosixPath
import shutil
import subprocess
import sys
import uuid

MARKER='.visualtk-install.json'
APP_NAME='TkVisualFoundry.app'
LEGACY_APP_NAME='VisualTk Studio.app'
SHORTCUT_NAME='TkVisualFoundry.lnk'
LEGACY_SHORTCUT_NAME='VisualTk Studio.lnk'

def install_root():
    return Path(os.environ.get('LOCALAPPDATA',str(Path.home()/'AppData/Local')))/'Programs/VisualTkStudio' if sys.platform=='win32' else Path.home()/'Applications/VisualTkStudio'

def is_link(path):return path.is_symlink() or (hasattr(path,'is_junction') and path.is_junction())

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def confined(root,relative):
    rel=PurePosixPath(relative)
    if rel.is_absolute() or not rel.parts or any(part in ('.','..') or ':' in part or '\\' in part for part in rel.parts):raise ValueError('Unsafe installation path')
    path=root.joinpath(*rel.parts)
    for item in [path,*path.parents]:
        if is_link(item):raise ValueError('Symbolic links are not removed')
        if item==root:break
    return path

def distribution_files(source):
    for p in sorted(source.iterdir()):
        if p.name.startswith('.'):continue
        if p.is_file() and p.suffix in ('.py','.md','.txt','.json','.command','.cmd','.ps1') and not is_link(p):yield p
        elif p.name in ('docs','examples') and p.is_dir():
            for child in p.rglob('*'):
                if child.is_file() and not is_link(child) and not any(x.startswith('.') or x=='__pycache__' for x in child.relative_to(p).parts):yield child

def record_install(root,source,app=None):
    if root.resolve()==source.resolve():raise ValueError('Run installation from the extracted download')
    if is_link(root):raise ValueError('Refusing linked installation root')
    previous={}
    marker=confined(root,MARKER)
    if marker.is_file():
        previous=json.loads(marker.read_text())
        if previous.get('product')!='VisualTkStudio':raise ValueError('Unrecognized prior installation')
    token=uuid.uuid4().hex;files={}
    for p in distribution_files(source):
        relative=p.relative_to(source).as_posix();target=confined(root,relative)
        if target.is_file():files[relative]=digest(target)
    env=root/'.venv'
    if is_link(env):raise ValueError('Refusing linked environment')
    if env.is_dir():confined(env,'.visualtk-owner').write_text(token)
    data={'format':1,'product':'VisualTkStudio','token':token,'files':files,'environment':env.is_dir()}
    if app:
        if app.name not in (APP_NAME,LEGACY_APP_NAME):raise ValueError('Unexpected launcher name')
        data['app_name']=app.name
        legacy=previous.get('app_files',{}) if previous.get('app_name',LEGACY_APP_NAME)==LEGACY_APP_NAME else previous.get('legacy_app_files',{})
        if app.name==APP_NAME and legacy:data['legacy_app_files']=legacy
        owned={}
        for rel in ('Contents/Info.plist','Contents/MacOS/VisualTkStudio'):
            path=confined(app,rel)
            if path.is_file():owned[rel]=digest(path)
        data['app_files']=owned
    marker=root/MARKER;temporary=confined(root,MARKER+'.tmp');temporary.write_text(json.dumps(data,indent=2));os.replace(temporary,marker)
    return data

def uninstall_plan(root,expected=None,app=None):
    expected=expected or install_root()
    if root.absolute()!=expected.absolute() or is_link(root):raise ValueError('Unexpected installation root')
    marker=confined(root,MARKER);data=json.loads(marker.read_text())
    if data.get('format')!=1 or data.get('product')!='VisualTkStudio' or not isinstance(data.get('token'),str) or len(data['token'])!=32:raise ValueError('Unrecognized installation manifest')
    remove=[];preserve=[]
    for rel,sha in data['files'].items():
        path=confined(root,rel)
        if path.is_file():(remove if digest(path)==sha else preserve).append(path)
    app_roots=[]
    if app:
        app_roots=[app]
        bundles=[(app,data.get('app_files',{}))]
        if data.get('legacy_app_files'):
            legacy=Path.home()/'Applications'/LEGACY_APP_NAME;app_roots.append(legacy);bundles.append((legacy,data['legacy_app_files']))
        for bundle,files in bundles:
            for rel,sha in files.items():
                path=confined(bundle,rel)
                if path.is_file():(remove if digest(path)==sha else preserve).append(path)
    env=confined(root,'.venv');environment=None
    if data.get('environment') and env.exists():
        owner=confined(env,'.visualtk-owner')
        if owner.is_file() and owner.read_text()==data['token']:environment=env
        else:preserve.append(env)
    return {'files':remove,'preserve':preserve,'environment':environment,'marker':marker,'app_roots':app_roots}

def uninstall_mac(root,dry_run=False):
    name=json.loads(confined(root,MARKER).read_text()).get('app_name',LEGACY_APP_NAME)
    if name not in (APP_NAME,LEGACY_APP_NAME):raise ValueError('Unexpected launcher name')
    app=Path.home()/'Applications'/name;plan=uninstall_plan(root,app=app)
    print('Files / File:',len(plan['files']),'— modified files kept / modificati conservati:',len(plan['preserve']))
    print('Projects, settings, history and system Python are kept. / Progetti, impostazioni, cronologia e Python di sistema restano.')
    print('Installation / Installazione:',root)
    if dry_run:
        for path in plan['files']:print('REMOVE:',path)
        print('Managed environment:',plan['environment']);return plan
    print('Close TkVisualFoundry before continuing. / Chiudi TkVisualFoundry prima di continuare.')
    if input('Uninstall TkVisualFoundry? / Disinstallare? [y/N]: ').strip().lower() not in ('y','yes','s','si'):return plan
    if plan['environment']:shutil.rmtree(plan['environment'])
    for path in plan['files']:
        try:path.unlink()
        except FileNotFoundError:pass
    directories=set()
    for path in plan['files']:
        for directory in path.parents:
            if directory==root or directory in plan['app_roots']:
                directories.add(directory);break
            directories.add(directory)
    for directory in sorted(directories,key=lambda p:len(p.parts),reverse=True):
        try:directory.rmdir()
        except OSError:pass
    plan['marker'].unlink(missing_ok=True)
    try:root.rmdir()
    except OSError:pass
    print('Uninstalled. Untracked/modified files remain. / Disinstallato. File personali/modificati conservati.')
    return plan

def install_windows(source):
    if sys.platform!='win32':raise RuntimeError('Windows installation must run on Windows')
    if sys.version_info[:2]<(3,15) or sys.version_info.releaselevel!='final':raise RuntimeError('Python 3.15+ final required')
    import winreg
    root=install_root();root.mkdir(parents=True,exist_ok=True)
    if is_link(root):raise ValueError('Linked installation root is unsupported')
    if source.resolve()==root.resolve():raise ValueError('Run the installer from the extracted download, not the installation folder')
    for path in distribution_files(source):
        target=confined(root,path.relative_to(source).as_posix());target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
    env=root/'.venv'
    if is_link(env):raise ValueError('Linked environment is unsupported')
    subprocess.run([sys.executable,'-m','venv',str(env)],check=True);python=env/'Scripts/python.exe'
    subprocess.run([str(python),'-m','pip','install','--upgrade','pip'],check=True);subprocess.run([str(python),'-m','pip','install','-r',str(root/'requirements.txt')],check=True)
    subprocess.run([str(python),'-c','import tkinter,jedi,PyInstaller'],check=True)
    # Use environment-local Python by default when Studio is launched through this shortcut.
    shortcut=Path(os.environ['APPDATA'])/'Microsoft/Windows/Start Menu/Programs'/SHORTCUT_NAME;shortcut.parent.mkdir(parents=True,exist_ok=True)
    def ps(value):return "'"+str(value).replace("'","''")+"'"
    command='$s=(New-Object -ComObject WScript.Shell).CreateShortcut('+ps(shortcut)+');$s.TargetPath='+ps(env/'Scripts/pythonw.exe')+';$s.Arguments='+ps('"'+str(root/'studio.py')+'"')+';$s.WorkingDirectory='+ps(root)+';$s.Save()'
    subprocess.run(['powershell.exe','-NoProfile','-Command',command],check=True)
    old_marker=confined(root,MARKER);previous=json.loads(old_marker.read_text()) if old_marker.is_file() else {}
    data=record_install(root,source);data['shortcut_name']=SHORTCUT_NAME;data['shortcut_sha256']=digest(shortcut)
    if previous.get('shortcut_name',LEGACY_SHORTCUT_NAME)==LEGACY_SHORTCUT_NAME and previous.get('shortcut_sha256'):data['legacy_shortcut_sha256']=previous['shortcut_sha256']
    elif previous.get('legacy_shortcut_sha256'):data['legacy_shortcut_sha256']=previous['legacy_shortcut_sha256']
    (root/MARKER).write_text(json.dumps(data,indent=2))
    version=json.loads((root/'RELEASE.json').read_text())['version']
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER,r'Software\Microsoft\Windows\CurrentVersion\Uninstall\VisualTkStudio') as key:
        for name,value in {'DisplayName':'TkVisualFoundry','DisplayVersion':version,'Publisher':'TkVisualFoundry','InstallLocation':str(root),'VTSToken':data['token'],'UninstallString':'"'+os.environ.get('COMSPEC','cmd.exe')+'" /c ""'+str(root/'Uninstall_Windows.cmd')+'""'}.items():winreg.SetValueEx(key,name,0,winreg.REG_SZ,value)
    print('Installed:',root,'— Uninstall from Windows Settings / Disinstalla da Impostazioni Windows.')

def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['record-mac','install-windows','uninstall-mac']);p.add_argument('--source',default=str(Path(__file__).resolve().parent));p.add_argument('--dry-run',action='store_true');args=p.parse_args();root=install_root()
    if args.action=='record-mac':record_install(root,Path(args.source),Path.home()/'Applications'/APP_NAME)
    elif args.action=='install-windows':install_windows(Path(args.source))
    elif sys.platform=='darwin':uninstall_mac(root,args.dry_run)
    else:raise RuntimeError('Use Uninstall_Windows.cmd on Windows')

if __name__=='__main__':main()
