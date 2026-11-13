"""Stable Python runtime policy shared by the IDE and its launch/build tools."""
from i18n import tr
import json
import subprocess
import sys

MINIMUM = (3, 15)
MESSAGE = tr('È richiesto Python 3.15 o successivo in versione stabile (final), con Tkinter. Le versioni alpha, beta e release candidate non sono accettate.')

def supported(version):
    return len(version)>=4 and tuple(version[:2])>=MINIMUM and version[3]=='final'

def format_version(version):
    base='.'.join(str(part) for part in version[:3])
    label={'alpha':'a','beta':'b','candidate':'rc'}.get(version[3],'')
    return base+(label+str(version[4]) if label else '')

def ensure_current():
    if not supported(tuple(sys.version_info)):raise RuntimeError(MESSAGE+tr('\nVersione rilevata: ')+sys.version.split()[0])

def validate_interpreter(python):
    try:
        result=subprocess.run([str(python),'-c','import sys,json,tkinter; print(json.dumps(list(sys.version_info)))'],capture_output=True,text=True,timeout=10)
        if result.returncode:raise ValueError(result.stderr.strip() or tr('Tkinter non disponibile'))
        version=json.loads(result.stdout)
        if not supported(version):raise ValueError(MESSAGE+tr('\nVersione rilevata: ')+format_version(version)+tr(' (stato: ')+version[3]+')')
        return version
    except (OSError,subprocess.TimeoutExpired,ValueError) as exc:
        raise ValueError(tr('Interprete non utilizzabile: ')+str(python)+'\n'+str(exc)) from exc

if __name__=='__main__':
    try:ensure_current()
    except RuntimeError as exc:raise SystemExit(str(exc))
    print(tr('Python stabile compatibile:'),sys.version.split()[0])
