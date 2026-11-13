"""Package a generated project and supply camera privacy metadata on macOS."""
from i18n import tr
from runtime_requirements import ensure_current
import plistlib
from pathlib import Path
import subprocess
import sys

def main():
    ensure_current()
    source=Path(sys.argv[1]).resolve();out=source.parent
    extras=[]
    requirements=out/'requirements-visualtk.txt'
    specs=requirements.read_text().lower() if requirements.exists() else ''
    if 'psycopg' in specs:extras += ['--hidden-import=sqlalchemy.dialects.postgresql.psycopg','--collect-all=psycopg','--collect-all=psycopg_binary']
    if 'pymysql' in specs:extras += ['--hidden-import=sqlalchemy.dialects.mysql.pymysql','--collect-all=pymysql']
    subprocess.run([sys.executable,'-m','PyInstaller','--noconfirm','--windowed','--name','VisualTkApplication','--distpath',str(out/'dist'),'--workpath',str(out/'build'),'--specpath',str(out),*extras,str(source)],check=True)
    if sys.platform=='darwin':
        app=out/'dist/VisualTkApplication.app';info=app/'Contents/Info.plist'
        data=plistlib.loads(info.read_bytes());data['NSCameraUsageDescription']=tr('Questa applicazione usa la webcam quando viene avviato il componente WebcamView.');info.write_bytes(plistlib.dumps(data))
        subprocess.run(['codesign','--force','--deep','--sign','-',str(app)],check=True)
    print(tr('Build completata:'),out/'dist')
if __name__=='__main__':main()
