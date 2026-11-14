"""Bounded literal search over project sources and confined Python files. Never executes code."""
import bisect
import hashlib
import os
from pathlib import Path
import re
from project_files import EXCLUDED,project_file
from i18n import tr

MAX_FILE_BYTES=2*1024*1024
MAX_TOTAL_BYTES=20*1024*1024
MAX_FILES=200
MAX_RESULTS=1000


def digest(text):return hashlib.sha256(text.encode('utf-8',errors='surrogatepass')).hexdigest()


def project_sources(project,override=None):
    sources=[]
    def add(key,label,text):
        if override and key==override[0]:text=override[1]
        sources.append({'key':key,'label':label,'text':text})
    for field in ('imports','startup'):add(('global',field),tr('Progetto')+' / '+field,project.get(field,''))
    for form in project['forms']:
        for obj in [form]+form['widgets']:
            events=dict(obj.get('events',{}))
            if override and override[0][:3]==('event',form['name'],obj['name']):events.setdefault(override[0][3],'')
            for event,text in events.items():add(('event',form['name'],obj['name'],event),form['name']+' / '+obj['name']+' / '+event,text)
    return sources


def read_python(path):
    if path.stat().st_size>MAX_FILE_BYTES:raise ValueError('File exceeds 2 MiB')
    with path.open('r',encoding='utf-8') as stream:text=stream.read(MAX_FILE_BYTES+1)
    if '\x00' in text or len(text.encode('utf-8'))>MAX_FILE_BYTES:raise ValueError('Binary file or file exceeds 2 MiB')
    return text


def python_sources(root,buffers,warnings,stop):
    if root is None:return
    root=Path(root).resolve();seen=set();count=0
    # Buffers take priority, even if the backing file has been removed on disk.
    candidates=list(sorted(buffers))
    def disk_paths():
        def error(exc):warnings.append(str(exc)[:200])
        for folder,dirs,files in os.walk(root,followlinks=False,onerror=error):
            if stop.is_set():return
            dirs[:]=sorted(d for d in dirs if not d.startswith('.') and d not in EXCLUDED and not Path(folder,d).is_symlink())
            for name in sorted(files):
                if stop.is_set():return
                if name.endswith('.py') and not name.startswith('.'):yield (Path(folder)/name).relative_to(root).as_posix()
    import itertools
    for relative in itertools.chain(candidates,disk_paths()):
        if stop.is_set():return
        if relative in seen:continue
        seen.add(relative)
        if count>=MAX_FILES:warnings.append('Python file limit: 200');return
        count+=1
        try:
            path=project_file(root,relative)
            if path.suffix!='.py':continue
            if relative in buffers:text=buffers[relative]
            else:
                text=read_python(path)
            if '\x00' in text:raise ValueError('Binary file')
            yield {'key':('file',relative),'label':relative,'text':text}
        except (OSError,ValueError,UnicodeError) as exc:warnings.append(relative+': '+str(exc)[:150])


def matches_in_chunks(matcher,text,width,stop):
    # Bound each regex call so cancellation and Tk can run between chunks.
    next_allowed=0
    for start in range(0,len(text),4096):
        if stop.is_set():return
        boundary=min(len(text),start+4096)
        scan_start=max(start,next_allowed)
        if scan_start>=boundary:continue
        for match in matcher.finditer(text,scan_start,min(len(text),boundary+width+1)):
            if match.start()>=boundary:break
            next_allowed=match.end()
            yield match


def search(project,query,root=None,buffers=None,override=None,case_sensitive=False,whole_word=False,stop=None):
    import threading,itertools
    stop=stop or threading.Event();rows=[];warnings=[];total=0;truncated=False
    if not query or len(query)>1000:raise ValueError('Use a search string of 1–1000 characters.')
    pattern=re.escape(query)
    if whole_word:pattern=r'(?<!\w)'+pattern+r'(?!\w)'
    matcher=re.compile(pattern,0 if case_sensitive else re.IGNORECASE)
    sources=itertools.chain(project_sources(project,override),python_sources(root,buffers or {},warnings,stop))
    for source in sources:
        if stop.is_set():return {'rows':[],'warnings':warnings,'cancelled':True,'truncated':False}
        text=source['text'];size=len(text.encode('utf-8',errors='surrogatepass'))
        if size>MAX_FILE_BYTES:warnings.append(source['label']+': source exceeds 2 MiB');continue
        total+=size
        if total>MAX_TOTAL_BYTES:truncated=True;warnings.append('Search byte limit: 20 MiB');break
        starts=[0]+[m.end() for m in re.finditer('\n',text)];fingerprint=digest(text)
        for match in matches_in_chunks(matcher,text,len(query),stop):
            if stop.is_set():return {'rows':[],'warnings':warnings,'cancelled':True,'truncated':False}
            if len(rows)>=MAX_RESULTS:truncated=True;break
            line=bisect.bisect_right(starts,match.start());column=match.start()-starts[line-1]
            endline=bisect.bisect_right(starts,match.end());endcolumn=match.end()-starts[endline-1]
            line_end=text.find('\n',match.start())
            preview_start=max(starts[line-1],match.start()-80);preview_end=min(line_end if line_end>=0 else len(text),match.start()+200)
            rows.append({'key':source['key'],'label':source['label'],'line':line,'column':column,'endline':endline,'endcolumn':endcolumn,'preview':text[preview_start:preview_end].strip(),'digest':fingerprint})
        if truncated:break
    return {'rows':rows,'warnings':warnings,'cancelled':False,'truncated':truncated}
