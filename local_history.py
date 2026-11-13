"""Bounded local project snapshots, separate from project files and deployment."""
import copy
import difflib
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from core import validate
from project_files import atomic_write_text

MAX_BYTES=10*1024*1024

def history_root():
    if sys.platform=='darwin':base=Path.home()/'Library/Application Support'
    elif sys.platform=='win32':base=Path(os.environ.get('LOCALAPPDATA') or str(Path.home()/'AppData/Local'))
    else:base=Path(os.environ.get('XDG_STATE_HOME') or str(Path.home()/'.local/state'))
    return base/'VisualTkStudio/history'

def captured_project(project,target=None,body=None):
    result=copy.deepcopy(project)
    if target and body is not None:
        name,event,global_=target
        if global_:result[event]=body
        else:
            obj=next((o for f in result['forms'] for o in [f]+f['widgets'] if o['name']==name),None)
            if obj is not None:obj.setdefault('events',{})[event]=body
    return result

def project_text(project):return json.dumps(project,indent=2,ensure_ascii=False,sort_keys=True)

def compare_projects(current,previous,limit=100000):
    lines=difflib.unified_diff(project_text(current).splitlines(True),project_text(previous).splitlines(True),fromfile='Current',tofile='Snapshot')
    result='';truncated=False
    for line in lines:
        if len(result)+len(line)>limit:truncated=True;break
        result+=line
    return result,truncated

def recovered_path(original):
    if not original:return None
    source=Path(original)
    if not source.parent.is_dir():raise ValueError('Original project folder is missing. Restore its resources before opening this snapshot.')
    stem=source.name.removesuffix('.vtk.json') if source.name.endswith('.vtk.json') else source.stem
    candidate=source.with_name(stem+'-recovered.vtk.json');index=2
    while candidate.exists():candidate=source.with_name(stem+f'-recovered-{index}.vtk.json');index+=1
    return candidate

class HistoryStore:
    def __init__(self,root=None,keep=30):self.root=Path(root) if root else history_root();self.keep=max(1,int(keep))
    def save(self,project,path,session,dirty=True,kind='autosave'):
        validate(project,code=False)
        identity=str(Path(path).absolute()) if path else 'unsaved:'+session
        key=hashlib.sha256(identity.encode()).hexdigest();folder=self.root/key
        content=project_text(project);digest=hashlib.sha256(content.encode()).hexdigest()
        if len(content.encode('utf-8'))>MAX_BYTES:raise ValueError('Snapshot exceeds 10 MB.')
        folder.mkdir(parents=True,exist_ok=True,mode=0o700)
        existing=sorted(folder.glob('*.json'),reverse=True)
        if existing:
            try:
                previous=json.loads(existing[0].read_text(encoding='utf-8'))
                if previous.get('digest')==digest and previous.get('dirty')==dirty:return existing[0]
            except (OSError,ValueError):pass
        created=time.time_ns();record={'schema':1,'created':created,'project_path':str(Path(path).absolute()) if path else None,'session':session,'dirty':bool(dirty),'kind':kind,'digest':digest,'project':project}
        target=folder/(str(created)+'-'+digest[:12]+'.json');atomic_write_text(target,json.dumps(record,ensure_ascii=False))
        for old in sorted(folder.glob('*.json'),reverse=True)[self.keep:]:old.unlink(missing_ok=True)
        return target
    def read(self,file):
        file=Path(file)
        if not file.resolve().is_relative_to(self.root.resolve()) or file.is_symlink():raise ValueError('Invalid history location.')
        if file.stat().st_size>MAX_BYTES+1024*1024:raise ValueError('Invalid history size.')
        record=json.loads(file.read_text(encoding='utf-8'))
        if not isinstance(record,dict):raise ValueError('Invalid snapshot record.')
        if record.get('schema')!=1:raise ValueError('Unsupported snapshot format.')
        if type(record.get('created')) is not int or not 0<record['created']<2**63:raise ValueError('Invalid snapshot date.')
        if record.get('project_path') is not None and (not isinstance(record['project_path'],str) or not Path(record['project_path']).is_absolute()):raise ValueError('Invalid project path.')
        if not isinstance(record.get('kind'),str):raise ValueError('Invalid snapshot type.')
        try:validate(record['project'],code=False)
        except (KeyError,TypeError,ValueError,AttributeError) as exc:raise ValueError('Invalid project snapshot.') from exc
        return record
    def index(self,limit=300):
        rows=[]
        for file in sorted(self.root.glob('*/*.json'),key=lambda p:p.name,reverse=True)[:limit]:
            try:record=self.read(file)
            except (OSError,ValueError,KeyError,TypeError):continue
            rows.append({key:value for key,value in record.items() if key!='project'}|{'file':str(file)})
        return rows
