"""Stable Python runtime policy shared by the IDE and its launch/build tools."""
import json
import subprocess
import sys

MINIMUM = (3, 15)
MESSAGE = 'È richiesto Python 3.15 o successivo in versione stabile (final), con Tkinter. Le versioni alpha, beta e release candidate non sono accettate.'

def supported(version):
    return len(version)>=4 and tuple(version[:2])>=MINIMUM and version[3]=='final'

def format_version(version):
    base='.'.join(str(part) for part in version[:3])
    label={'alpha':'a','beta':'b','candidate':'rc'}.get(version[3],'')
    return base+(label+str(version[4]) if label else '')

def ensure_current():
    if not supported(tuple(sys.version_info)):raise RuntimeError(MESSAGE+'\nVersione rilevata: '+sys.version.split()[0])

def validate_interpreter(python):
    try:
        result=subprocess.run([str(python),'-c','import sys,json,tkinter; print(json.dumps(list(sys.version_info)))'],capture_output=True,text=True,timeout=10)
        if result.returncode:raise ValueError(result.stderr.strip() or 'Tkinter non disponibile')
        version=json.loads(result.stdout)
        if not supported(version):raise ValueError(MESSAGE+'\nVersione rilevata: '+format_version(version)+' (stato: '+version[3]+')')
        return version
    except (OSError,subprocess.TimeoutExpired,ValueError) as exc:
        raise ValueError('Interprete non utilizzabile: '+str(python)+'\n'+str(exc)) from exc

if __name__=='__main__':
    try:ensure_current()
    except RuntimeError as exc:raise SystemExit(str(exc))
    print('Python stabile compatibile:',sys.version.split()[0])
