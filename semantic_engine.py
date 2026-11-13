"""Project-aware static completion; never evaluate submitted editor code."""
from i18n import tr
import ast
import builtins
import importlib
import inspect
import io
from pathlib import Path
import re
import tokenize
from components import registry
from code_assist import completions,signature

PRELUDE='''import tkinter
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog, colorchooser, font
from tkinter.scrolledtext import ScrolledText
import traceback
'''
SAFE_MODULES={'tkinter','tkinter.ttk','tkinter.messagebox','tkinter.filedialog','tkinter.simpledialog','tkinter.colorchooser','tkinter.font','tkinter.scrolledtext','json','math','os','os.path','pathlib','re','datetime','collections','itertools','functools','statistics','typing','sys','random'}
ALIASES={'tk':'tkinter','tkinter':'tkinter','ttk':'tkinter.ttk','messagebox':'tkinter.messagebox','filedialog':'tkinter.filedialog','simpledialog':'tkinter.simpledialog','colorchooser':'tkinter.colorchooser','font':'tkinter.font'}


def in_literal(before):
    row=before.count('\n')+1
    try:
        for token in tokenize.generate_tokens(io.StringIO(before).readline):
            if token.type==tokenize.COMMENT and token.end[0]==row:return True
            if token.type==tokenize.ERRORTOKEN and token.string in ('"',"'") and token.start[0]==row:return True
    except tokenize.TokenError as exc:
        if 'string' in str(exc):return True
    except (IndentationError,SyntaxError):pass
    return False


def word_prefix(before):
    match=re.search(r'\w*$',before);return match.group() if match else ''


def editor_source(request):
    project=request['project'];body=request['body'];row,column=map(int,request['cursor'].split('.'));mode=request.get('mode','event')
    imports=project.get('imports','') if mode!='imports' else ''
    head=PRELUDE+imports+'\n';reg=registry(project);constructors=[];assignments=['        self.root = tk.Tk()']
    for form in project['forms']:
        assignments.append('        self.'+form['name']+' = tk.Toplevel(self.root)')
        for widget in form['widgets']:
            kind=widget['kind']
            if kind in reg:
                desc=reg[kind];alias='_vt_'+kind;constructors.append(f"from {desc['module']} import {desc['class']} as {alias}");constructor=alias
            else:constructor=('ttk.' if kind in ('Combobox','Progressbar') else 'tk.')+kind
            assignments.append(f"        self.{widget['name']} = {constructor}(self.{form['name']})")
    head+='\n'.join(dict.fromkeys(constructors))+'\n'
    stub='class Application:\n    def __init__(self):\n'+'\n'.join(assignments)+'\n    def show(self, name):\n        pass\n    def hide(self, name):\n        pass\n'
    if mode=='imports':return head+body+'\n\n'+stub,row+head.count('\n'),column
    head+=stub+'    def _editor_event(self, event: tk.Event = None):\n'
    return head+'\n'.join('        '+line for line in body.split('\n')),row+head.count('\n'),column+8


def _aliases(source):
    aliases=dict(ALIASES)
    try:nodes=ast.parse(source).body
    except SyntaxError:
        nodes=[]
        for line in source.splitlines():
            if line.lstrip().startswith(('import ','from ')):
                try:nodes.extend(ast.parse(line.strip()).body)
                except SyntaxError:pass
    for node in nodes:
        if isinstance(node,ast.Import):
            for name in node.names:
                aliases.pop(name.asname or name.name.split('.')[0],None)
                if name.name in SAFE_MODULES:aliases[name.asname or name.name.split('.')[0]]=name.name if name.asname else name.name.split('.')[0]
        elif isinstance(node,ast.ImportFrom) and node.module:
            for name in node.names:
                aliases.pop(name.asname or name.name,None)
                full=node.module+'.'+name.name
                if full in SAFE_MODULES:aliases[name.asname or name.name]=full
    # A reassigned alias belongs to Jedi's inference, not the stdlib fallback.
    for line in source.splitlines():
        reassigned=re.match(r'\s*([A-Za-z_]\w*)\s*=(?!=)',line)
        if reassigned:aliases.pop(reassigned.group(1),None)
    return aliases


def _member(reference,source):
    parts=reference.split('.');aliases=_aliases(source)
    if parts[0] in aliases:obj=importlib.import_module(aliases[parts[0]])
    elif parts[0] in ('str','list','dict','tuple','set','int','float','bytes'):obj=getattr(builtins,parts[0])
    else:return None
    for part in parts[1:]:
        try:obj=inspect.getattr_static(obj,part)
        except AttributeError:return None
    return obj


def _entry(name,obj,prefix_len):
    kind='module' if inspect.ismodule(obj) else 'class' if inspect.isclass(obj) else 'function' if callable(obj) else 'property'
    try:sig=name+str(inspect.signature(obj)) if callable(obj) else ''
    except (ValueError,TypeError):sig=''
    return {'name':name,'insert':name,'prefix_len':prefix_len,'kind':kind,'signature':sig,'doc':(inspect.getdoc(obj) or '')[:1800]}


def local_analysis(before,project,body=''):
    result={'items':[],'calltip':'','engine':tr('Locale')}
    if in_literal(before):return result
    prefix,values=completions(before,project);word=word_prefix(before);receiver=prefix[:-len(word)] if word else prefix
    for text,doc in values:
        insert=text[len(receiver):] if receiver and text.startswith(receiver) else text
        result['items'].append({'name':insert,'insert':insert,'prefix_len':len(word) if receiver else len(prefix),'kind':'property' if insert.endswith('=') else 'member','signature':'','doc':doc})
    result['calltip']=signature(before,project);source=project.get('imports','')+'\n'+body
    match=re.search(r'([A-Za-z_]\w*(?:\.\w+)*)\.(\w*)$',before)
    if match:
        obj=_member(match.group(1),source);prefix=match.group(2)
        if obj is not None:
            for name,value in (vars(obj) if hasattr(obj,'__dict__') else vars(type(obj))).items():
                if name.startswith(prefix) and (prefix.startswith('_') or not name.startswith('_')):result['items'].append(_entry(name,value,len(prefix)))
    match=re.search(r'([A-Za-z_]\w*(?:\.\w+)*)\([^()]*$',before)
    if match:
        obj=_member(match.group(1),source)
        if obj is not None and callable(obj):result['calltip']=_entry(match.group(1),obj,0)['signature']
    if not result['items'] and word and not re.search(r'\.[\w]*$',before):
        import keyword
        names=keyword.kwlist+list(vars(builtins))+list(ALIASES)
        result['items']=[{'name':name,'insert':name,'prefix_len':len(word),'kind':'Python','signature':'','doc':''} for name in sorted(set(names)) if name.startswith(word)]
    return result


class SemanticEngine:
    def __init__(self,cache_directory=None):
        import jedi
        self.jedi=jedi;self.projects={}
        if cache_directory:jedi.settings.cache_directory=str(cache_directory)
    def analyze(self,request):
        source,row,column=editor_source(request);cwd=str(Path(request.get('cwd') or '.').resolve())
        if cwd not in self.projects:self.projects[cwd]=self.jedi.Project(cwd,added_sys_path=[str(Path(__file__).resolve().parent)])
        script=self.jedi.Script(source,path=str(Path(cwd)/'__visualtk_editor__.py'),project=self.projects[cwd])
        result={'items':[],'calltip':'','engine':'Jedi '+self.jedi.__version__}
        signatures=script.get_signatures(row,column)
        if signatures:
            sig=signatures[0];tip=sig.to_string()
            if sig.index is not None and sig.index<len(sig.params):tip+=tr('   • argomento: ')+sig.params[sig.index].name
            result['calltip']=tip
        if request.get('action')=='signature':return result
        candidates=script.complete(row,column);detail=request.get('detail_name')
        if detail:
            candidate=next((c for c in candidates if c.name_with_symbols==detail),None)
            if candidate:
                sigs=candidate.get_signatures();result['detail']={'name':detail,'signature':sigs[0].to_string() if sigs else '', 'doc':candidate.docstring(fast=False)[:4000]}
            return result
        prefix=request['body'].split('\n')[int(request['cursor'].split('.')[0])-1][:int(request['cursor'].split('.')[1])];word=word_prefix(prefix)
        for candidate in candidates:
            name=candidate.name_with_symbols
            if name.startswith('_') and not word.startswith('_'):continue
            result['items'].append({'name':name,'insert':name,'prefix_len':candidate.get_completion_prefix_length(),'kind':candidate.type,'signature':'','doc':candidate.description})
        result['items']=result['items'][:1200]
        return result
