"""Searchable PyPI project-name index, cached locally; no package code imported."""
import gzip
import codecs
from html.parser import HTMLParser
from pathlib import Path
import os
import re
import sys
import tempfile
import time
from urllib.request import Request,urlopen
from startup_checks import https_context

NAME=re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]*\Z')

class ProjectNames(HTMLParser):
    def __init__(self):super().__init__();self.anchor=False;self.parts=[];self.names=[];self.complete=False
    def handle_starttag(self,tag,attrs):
        if tag=='a':self.anchor=dict(attrs).get('href','').startswith('/simple/');self.parts=[]
    def handle_data(self,data):
        if self.anchor:self.parts.append(data)
    def handle_endtag(self,tag):
        if tag=='a' and self.anchor:
            name=''.join(self.parts).strip()
            if NAME.fullmatch(name):self.names.append(name)
            self.anchor=False
        if tag=='html':self.complete=True

def cache_file():
    if sys.platform=='darwin':root=Path.home()/'Library/Caches'
    elif sys.platform=='win32':root=Path(os.environ.get('LOCALAPPDATA',str(Path.home()/'AppData/Local')))
    else:root=Path(os.environ.get('XDG_CACHE_HOME',str(Path.home()/'.cache')))
    return root/'VisualTkStudio'/'pypi-projects.txt'

def project_names(path=None,refresh=False,cancelled=None,progress=None):
    path=Path(path) if path else cache_file()
    def stop():return cancelled is not None and cancelled.is_set()
    if stop():raise InterruptedError('Cancelled')
    if path.exists() and not refresh:
        try:names=path.read_text(encoding='utf-8').splitlines()
        except (OSError,UnicodeError):names=[]
        if names and all(NAME.fullmatch(n) for n in names):
            return {'names':names,'cached':True,'age':max(0,time.time()-path.stat().st_mtime)}
    parser=ProjectNames();decoder=codecs.getincrementaldecoder('utf-8')();started=time.monotonic();size=0
    request=Request('https://pypi.org/simple/',headers={'Accept':'application/vnd.pypi.simple.v1+html','Accept-Encoding':'gzip','User-Agent':'TkVisualFoundry/1.30'})
    with urlopen(request,timeout=12,context=https_context()) as response:
        stream=gzip.GzipFile(fileobj=response) if response.headers.get('Content-Encoding')=='gzip' else response
        while True:
            if stop():raise InterruptedError('Cancelled')
            if time.monotonic()-started>120:raise TimeoutError('PyPI index download timeout')
            chunk=stream.read(65536)
            if not chunk:break
            size+=len(chunk)
            if size>256*1024*1024:raise ValueError('PyPI index exceeds 256 MB')
            parser.feed(decoder.decode(chunk))
            if progress:progress(len(parser.names))
    parser.feed(decoder.decode(b'',final=True));parser.close()
    if not parser.complete or not parser.names:raise ValueError('Incomplete PyPI project index')
    names=sorted(set(parser.names),key=str.casefold)
    if stop():raise InterruptedError('Cancelled')
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,temporary=tempfile.mkstemp(prefix='.pypi-',dir=path.parent)
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as output:output.write('\n'.join(names)+'\n')
        os.replace(temporary,path)
    finally:Path(temporary).unlink(missing_ok=True)
    return {'names':names,'cached':False,'age':0}

def search_names(names,query,offset=0,limit=100):
    tokens=query.casefold().split();query=query.casefold().strip()
    exact=[];prefix=[];other=[]
    for name in names:
        folded=name.casefold()
        if not all(token in folded for token in tokens):continue
        (exact if folded==query else prefix if query and folded.startswith(query) else other).append(name)
    matches=exact+prefix+other
    return {'names':matches[offset:offset+limit],'total':len(matches),'offset':offset}
