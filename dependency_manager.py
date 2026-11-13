"""Dependency plans and interpreter-scoped checks; no Tk or shell required."""
from i18n import tr
import json
import re
import subprocess
import os
import threading
from components import registry, requirements, install_args
from productivity_specs import productivity_requirements

PACKAGE_MODULES = {'mido':'mido','python-rtmidi':'rtmidi','openpyxl':'openpyxl','pypdf':'pypdf','openai':'openai','anthropic':'anthropic','google-genai':'google.genai','google-api-python-client':'googleapiclient.discovery','google-auth-oauthlib':'google_auth_oauthlib','google-auth-httplib2':'google_auth_httplib2','boto3':'boto3','requests':'requests','sv-ttk':'sv_ttk','pmw':'Pmw','customtkinter':'customtkinter','ttkbootstrap':'ttkbootstrap','ttkthemes':'ttkthemes','tksheet':'tksheet','tkcalendar':'tkcalendar','tkintermapview':'tkintermapview','tkinterweb':'tkinterweb','jedi':'jedi','pillow':'PIL','opencv-python':'cv2','numpy':'numpy','pygame-ce':'pygame','pyusb':'usb','pyserial':'serial','sqlalchemy':'sqlalchemy','psycopg':'psycopg','pymysql':'pymysql','python-vlc':'vlc','yt-dlp':'yt_dlp','pywebview':'webview','tkvideoplayer':'tkVideoPlayer','pyinstaller':'PyInstaller'}
NOTES = {
 'WebcamView':tr('OpenCV acquisisce il video e richiede NumPy; Pillow converte e visualizza i fotogrammi. Dopo l’installazione macOS deve autorizzare la Fotocamera per Python o l’app avviata.'),
 'USBExplorer':tr('PyUSB richiede anche la libreria nativa libusb (su Mac: brew install libusb). Il wizard PIP non installa driver di sistema.'),
 'VideoPlayer':tr('Il pacchetto python-vlc richiede VLC/libVLC della stessa architettura di Python, installato separatamente.'),
 'YouTubePlayer':tr('Servono anche VLC/libVLC. La disponibilità dei flussi dipende dal servizio video.'),
 'DatabaseView':tr('SQLite è incluso in Python. PostgreSQL richiede SQLAlchemy e psycopg; MySQL richiede SQLAlchemy e PyMySQL. Nessuna password viene salvata nel progetto.'),
 'LegacyVideoPlayer':tr('Componente legacy: la disponibilità di pacchetti per questo Python va verificata.'),
}

def component_requirements(project, kind, props=None):
    specs=list(registry(project).get(kind,{}).get('requirements',[]));props=props or {}
    specs+=productivity_requirements(kind,props)
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
import json,importlib.metadata,sys
try:
 from packaging.requirements import Requirement
except ImportError:
 from pip._vendor.packaging.requirements import Requirement
out=[]
for spec in json.loads(sys.argv[1]):
 req=Requirement(spec);name=req.name
 item={'spec':spec,'package':name,'version':'','state':'missing','detail':'Non installato'}
 try:
  version=importlib.metadata.version(name);item['version']=version
  if req.specifier and not req.specifier.contains(version,prereleases=False):item.update(state='incompatible',detail='Versione fuori dal requisito '+str(req.specifier))
  else:item.update(state='ready',detail='Versione verificata; modulo esterno non importato')
 except importlib.metadata.PackageNotFoundError:pass
 out.append(item)
print('VISUALTK_DEPENDENCIES='+json.dumps(out))
'''
    result=subprocess.run([python,'-c',script,json.dumps(specs)],capture_output=True,text=True,timeout=30)
    if result.returncode:raise RuntimeError(tr('Verifica non riuscita: ')+(result.stderr or result.stdout)[-1000:])
    try:
        payload=next(line.split('=',1)[1] for line in result.stdout.splitlines() if line.startswith('VISUALTK_DEPENDENCIES='))
        items=json.loads(payload)
    except (ValueError,StopIteration):raise RuntimeError(tr('L’interprete non ha restituito una verifica leggibile.')) from None
    for item in items:
        detail=item.get('detail','')
        prefix='Versione fuori dal requisito '
        item['detail']=tr(prefix)+detail[len(prefix):] if detail.startswith(prefix) else tr(detail)
        module=PACKAGE_MODULES.get(item['package'].lower().replace('_','-'))
        if item['state']!='ready' or not module:continue
        try:
            check=subprocess.run([python,'-c','import importlib,sys; importlib.import_module(sys.argv[1]); print("VISUALTK_IMPORT_OK")',module],capture_output=True,text=True,timeout=25)
            if check.returncode==0 and 'VISUALTK_IMPORT_OK' in check.stdout:item['detail']=tr('Import verificato')
            else:item.update(state='broken',detail=(check.stderr or check.stdout or tr('Import terminato con codice ')+str(check.returncode))[-240:])
        except subprocess.TimeoutExpired:item.update(state='broken',detail=tr('Import bloccato: tempo massimo superato'))
    return items


def pip_install_command(python,specs,binary_only=False):
    args=install_args(python,specs)
    args[4:4]=['--disable-pip-version-check','--no-input','--prefer-binary','--timeout','15','--retries','1']
    if binary_only:args.append('--only-binary=:all:')
    return args


class DependencyInstallError(RuntimeError):
    pass


def install_dependencies(python,specs,binary_only=False,repair=False,on_output=None,cancelled=None,process_changed=None):
    """Install, check and import in a worker; callbacks never require Tk access."""
    output=on_output or (lambda line:None)
    cancelled=cancelled or (lambda:False)
    process_changed=process_changed or (lambda process:None)
    if not specs:return []
    install_args(python,specs)
    def run(args,timeout=600):
        if cancelled():raise DependencyInstallError(tr('Operazione interrotta. I pacchetti già installati vengono conservati.'))
        output('$ '+' '.join(args)+'\n');tail=[]
        process=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace',bufsize=1,env={**os.environ,'PYTHONUNBUFFERED':'1','PIP_PROGRESS_BAR':'off'})
        process_changed(process)
        if cancelled():process.terminate()
        timer=threading.Timer(timeout,process.kill);timer.daemon=True;timer.start()
        try:
            for line in process.stdout:
                output(line);tail.append(line)
                if len(tail)>80:tail.pop(0)
            code=process.wait()
        finally:timer.cancel();process.stdout.close();process_changed(None)
        if cancelled():raise DependencyInstallError(tr('Installazione interrotta. Ripeti la verifica prima di usare il componente.'))
        return code,''.join(tail)
    available=subprocess.run([python,'-m','pip','--version'],capture_output=True,timeout=15)
    if available.returncode:
        code,tail=run([python,'-m','ensurepip','--upgrade'])
        if code:raise DependencyInstallError(tr('PIP non disponibile: scegli un ambiente Python con PIP.\n')+tail)
    # Pre-existing conflicts must not be misreported as a new failure caused by this install.
    baseline=subprocess.run([python,'-m','pip','check'],capture_output=True,text=True,timeout=40)
    old_conflicts=set(baseline.stdout.splitlines()) if baseline.returncode else set()
    command=pip_install_command(python,specs,binary_only)
    if repair:command.append('--force-reinstall')
    code,tail=run(command)
    if code:
        raise DependencyInstallError(tr('PIP non ha completato l’installazione. Leggi il log per il dettaglio. Nessun requisito viene dichiarato pronto.\n')+tail)
    code,tail=run([python,'-m','pip','check'],timeout=40)
    if code:
        # Extract the result separately from informational warnings emitted on stderr.
        current=subprocess.run([python,'-m','pip','check'],capture_output=True,text=True,timeout=40)
        conflicts=set(current.stdout.splitlines())
        if not conflicts or not conflicts.issubset(old_conflicts):raise DependencyInstallError(tr('Conflitti di dipendenze dopo l’installazione.\n')+tail)
        output(tr('AVVISO: conflitti già presenti nell’ambiente prima dell’installazione; controlla il log.\n'))
    output(tr('Verifica finale delle versioni e degli import…\n'))
    if cancelled():raise DependencyInstallError(tr('Operazione interrotta prima della verifica finale.'))
    return probe_interpreter(python,specs)


def preparation_action(results,automatic,attempted,continue_after):
    if all(item['state']=='ready' for item in results):return 'continue' if continue_after else 'ready'
    return 'install' if automatic and not attempted else 'wait'
