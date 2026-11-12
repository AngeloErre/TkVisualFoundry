"""Dependency plans and interpreter-scoped checks; no Tk or shell required."""
import json
import re
import subprocess
from components import registry, requirements, install_args

PACKAGE_MODULES = {'pillow':'PIL','opencv-python':'cv2','numpy':'numpy','pygame-ce':'pygame','pyusb':'usb','pyserial':'serial','sqlalchemy':'sqlalchemy','psycopg':'psycopg','pymysql':'pymysql','python-vlc':'vlc','yt-dlp':'yt_dlp','pywebview':'webview','tkvideoplayer':'tkVideoPlayer','pyinstaller':'PyInstaller'}
NOTES = {
 'WebcamView':'OpenCV acquisisce il video e richiede NumPy; Pillow converte e visualizza i fotogrammi. Dopo l’installazione macOS deve autorizzare la Fotocamera per Python o l’app avviata.',
 'USBExplorer':'PyUSB richiede anche la libreria nativa libusb (su Mac: brew install libusb). Il wizard PIP non installa driver di sistema.',
 'VideoPlayer':'Il pacchetto python-vlc richiede VLC/libVLC della stessa architettura di Python, installato separatamente.',
 'YouTubePlayer':'Servono anche VLC/libVLC. La disponibilità dei flussi dipende dal servizio video.',
 'DatabaseView':'SQLite è incluso in Python. PostgreSQL richiede SQLAlchemy e psycopg; MySQL richiede SQLAlchemy e PyMySQL. Nessuna password viene salvata nel progetto.',
 'LegacyVideoPlayer':'Componente legacy: la disponibilità di pacchetti per questo Python va verificata.',
}

def component_requirements(project, kind, props=None):
    specs=list(registry(project).get(kind,{}).get('requirements',[]));props=props or {}
    if kind=='WebcamView':specs.append('numpy')
    if kind=='DatabaseView':
        backend=props.get('backend','sqlite')
        if backend=='postgresql':specs+=['SQLAlchemy>=2.0','psycopg[binary]>=3']
        elif backend=='mysql':specs+=['SQLAlchemy>=2.0','PyMySQL>=1.1']
    if kind=='FileBrowserButton' and props.get('advanced'):specs.append('tkfilebrowser>=2.3')
    if kind=='YouTubePlayer' and props.get('backend') in ('pytube','pytubefix'):specs.append(props['backend'])
    return sorted(set(specs))


def dependency_plan(project, kind=None, props=None):
    specs=component_requirements(project,kind,props) if kind else requirements(project)
    install_args('python',specs) if specs else None
    return specs


def probe_interpreter(python,specs):
    """Check versions and imports in the selected interpreter, never the IDE's own."""
    if not specs:return []
    install_args(python,specs)
    script=r'''
import json,importlib,importlib.metadata,re,sys,contextlib,io
try:
 from packaging.requirements import Requirement
except ImportError:
 from pip._vendor.packaging.requirements import Requirement
payload=json.loads(sys.argv[1]);out=[]
for spec in payload['specs']:
 req=Requirement(spec);name=req.name;norm=name.lower().replace('_','-');module=payload['modules'].get(norm)
 item={'spec':spec,'package':name,'version':'','state':'missing','detail':'Non installato'}
 try:
  version=importlib.metadata.version(name);item['version']=version
  if req.specifier and not req.specifier.contains(version,prereleases=False):
   item.update(state='incompatible',detail='Versione fuori dal requisito '+str(req.specifier))
  else:
   if module:
    with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):importlib.import_module(module)
   item.update(state='ready',detail='Import verificato' if module else 'Versione verificata; modulo esterno non importato')
 except importlib.metadata.PackageNotFoundError:pass
 except Exception as exc:item.update(state='broken',detail=type(exc).__name__+': '+str(exc)[:200])
 out.append(item)
print(json.dumps(out))
'''
    result=subprocess.run([python,'-c',script,json.dumps({'specs':specs,'modules':PACKAGE_MODULES})],capture_output=True,text=True,timeout=max(40,min(120,len(specs)*8)))
    if result.returncode:raise RuntimeError('Verifica non riuscita: '+(result.stderr or result.stdout)[-1500:])
    try:return json.loads(result.stdout)
    except ValueError:raise RuntimeError('L’interprete non ha restituito una verifica leggibile.') from None


def pip_install_command(python,specs,binary_only=True):
    args=install_args(python,specs)
    args[4:4]=['--disable-pip-version-check','--timeout','15','--retries','1']
    if binary_only:args.append('--only-binary=:all:')
    return args
