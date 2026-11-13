"""Confined project file operations and explicit deployment membership."""
from pathlib import Path, PurePosixPath
import shutil
import time

EXCLUDED={'.git','.venv','venv','__pycache__','build','dist','.visualtk-trash'}

def project_file(root,relative):
    root=Path(root).resolve();rel=PurePosixPath(str(relative))
    if not rel.parts or rel.is_absolute() or any(p in ('..','.') or ':' in p or '\\' in p or p.startswith('.') for p in rel.parts):raise ValueError('Use a relative path without hidden folders or parent traversal.')
    path=root.joinpath(*rel.parts)
    for parent in [path,*path.parents]:
        if parent==root:break
        if parent.is_symlink():raise ValueError('Symbolic links are not supported in project files.')
    if not path.resolve().is_relative_to(root):raise ValueError('Path outside project folder.')
    return path

def list_files(root,limit=1500):
    root=Path(root).resolve();result=[]
    def walk(folder):
        for path in sorted(folder.iterdir(),key=lambda p:(not p.is_dir(),p.name.casefold())):
            if path.name.startswith('.') or path.name in EXCLUDED or path.is_symlink():continue
            if limit is not None and len(result)>=limit:return
            result.append((path.relative_to(root).as_posix(),path.is_dir()))
            if path.is_dir():walk(path)
    walk(root);return result

def included_files(project,root):
    root=Path(root).resolve();result={}
    for relative in project.get('files',[]):
        path=project_file(root,relative)
        if not path.exists():raise ValueError('Missing project file: '+relative)
        if path.is_dir():
            for child,is_dir in list_files(path,limit=None):
                if not is_dir:
                    item=path/child;result[item.relative_to(root).as_posix()]=item
        else:result[path.relative_to(root).as_posix()]=path
    return result

def rename_file(project,root,relative,new_relative):
    source=project_file(root,relative);target=project_file(root,new_relative)
    if target.exists():raise FileExistsError(target)
    if not target.parent.is_dir():raise ValueError('Destination folder does not exist.')
    source.rename(target)
    project['files']=[new_relative+name[len(relative):] if name==relative or name.startswith(relative+'/') else name for name in project.get('files',[])]

def trash_file(project,root,relative):
    source=project_file(root,relative);trash=Path(root)/'.visualtk-trash'
    if trash.is_symlink():raise ValueError('Invalid trash folder.')
    trash.mkdir(exist_ok=True);target=trash/(str(time.time_ns())+'-'+source.name);shutil.move(str(source),str(target))
    project['files']=[name for name in project.get('files',[]) if name!=relative and not name.startswith(relative+'/')]
    return target
