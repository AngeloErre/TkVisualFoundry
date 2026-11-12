"""Package a generated project and supply camera privacy metadata on macOS."""
from runtime_requirements import ensure_current
import plistlib
from pathlib import Path
import subprocess
import sys

def main():
    ensure_current()
    source=Path(sys.argv[1]).resolve();out=source.parent
    subprocess.run([sys.executable,'-m','PyInstaller','--noconfirm','--windowed','--name','VisualTkApplication','--distpath',str(out/'dist'),'--workpath',str(out/'build'),'--specpath',str(out),str(source)],check=True)
    if sys.platform=='darwin':
        app=out/'dist/VisualTkApplication.app';info=app/'Contents/Info.plist'
        data=plistlib.loads(info.read_bytes());data['NSCameraUsageDescription']='Questa applicazione usa la webcam quando viene avviato il componente WebcamView.';info.write_bytes(plistlib.dumps(data))
        subprocess.run(['codesign','--force','--deep','--sign','-',str(app)],check=True)
    print('Build completata:',out/'dist')
if __name__=='__main__':main()
