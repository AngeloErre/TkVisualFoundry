"""Project model and deterministic standalone Python generator."""
from i18n import tr,get_language
import ast
import json
import keyword
from components import registry, requirements
from pathlib import Path
from hierarchy import ordered_widgets
from adaptive_layout import validate_layout
from event_breakpoints import validate_breakpoints
from watch_values import validate_watches
from library_catalog import theme_config
from productivity_specs import validate_productivity

KINDS = ('Button','Label','Entry','Text','Checkbutton','Radiobutton','Listbox','Combobox','Scale','Spinbox','Frame','Canvas','Progressbar')
EVENTS = {'Click':'<Button-1>', 'DoubleClick':'<Double-Button-1>', 'Enter':'<Enter>', 'Leave':'<Leave>', 'KeyPress':'<KeyPress>', 'FocusIn':'<FocusIn>', 'FocusOut':'<FocusOut>', 'Change':'<<ComboboxSelected>>', 'ImageSelected':'<<ImageSelected>>', 'PlaybackStarted':'<<PlaybackStarted>>', 'SnapshotSaved':'<<SnapshotSaved>>', 'DeviceSelected':'<<DeviceSelected>>', 'DeviceError':'<<DeviceError>>', 'DataReceived':'<<DataReceived>>', 'FilesDropped':'<<FilesDropped>>', 'FileSelected':'<<FileSelected>>', 'DialogClosed':'<<DialogClosed>>', 'NavigationStarted':'<<NavigationStarted>>', 'StreamResolved':'<<StreamResolved>>', 'TreeSelect':'<<TreeviewSelect>>', 'TabChanged':'<<NotebookTabChanged>>', 'DateSelected':'<<CalendarSelected>>', 'DatabaseConnected':'<<DatabaseConnected>>', 'DataLoaded':'<<DataLoaded>>', 'RecordSelected':'<<RecordSelected>>', 'DataChanged':'<<DataChanged>>', 'SheetChanged':'<<SheetChanged>>','SheetSelected':'<<SheetSelected>>','MapClicked':'<<MapClicked>>','MarkerSelected':'<<MarkerSelected>>', 'ServiceError':'<<ServiceError>>','MidiStarted':'<<MidiStarted>>','MidiFinished':'<<MidiFinished>>','ExcelLoaded':'<<ExcelLoaded>>','ExcelChanged':'<<ExcelChanged>>','ExcelSaved':'<<ExcelSaved>>','PDFLoaded':'<<PDFLoaded>>','PDFTextReady':'<<PDFTextReady>>','PDFSaved':'<<PDFSaved>>','PrintSubmitted':'<<PrintSubmitted>>','CloudConnected':'<<CloudConnected>>','CloudListed':'<<CloudListed>>','CloudTransferred':'<<CloudTransferred>>','LLMModelsReady':'<<LLMModelsReady>>','LLMResponse':'<<LLMResponse>>', 'DatabaseError':'<<DatabaseError>>'}

def new_project(language=None):
    return {'version':1,'files':[],'language':language or get_language(),'name':tr('Applicazione'),'forms':[{'name':'Form1','title':'Form1','width':640,'height':440,'bg':'#f0f0f0','widgets':[],'events':{}}], 'imports':'', 'startup':'self.Form1.deiconify()'}

def identifier(value):
    return isinstance(value,str) and value.isidentifier() and not keyword.iskeyword(value) and not value.startswith(('_','event_')) and value not in {'root','show','hide','startup','mainloop','destroy','report_callback_exception'}

def validate(p, code=True):
    if p.get('version') != 1 or not p.get('forms'): raise ValueError(tr('Formato progetto non supportato'))
    validate_breakpoints(p,project=True);validate_watches(p)
    files=p.get('files',[])
    if not isinstance(files,list) or not all(isinstance(value,str) for value in files):raise ValueError('Project files must be a list of relative paths.')
    if 'deployment' in p and not isinstance(p['deployment'],dict):raise ValueError('Invalid deployment settings.')
    reg=registry(p); requirements(p)
    theme_config(p)
    if p.get('appearance_mode','System') not in ('System','Light','Dark'):raise ValueError('Invalid CustomTkinter appearance mode')
    if 'environment' in p and (not isinstance(p['environment'],dict) or type(p['environment'].get('managed',False)) is not bool):raise ValueError('Invalid project environment settings.')
    names=set()
    for f in p['forms']:
        ordered_widgets(f)
        for obj in [f]+f['widgets']:
            validate_breakpoints(obj)
            n=obj['name']
            if not identifier(n) or n in names: raise ValueError(tr('Nome non valido o duplicato: {v0}', v0=f'{n}'))
            names.add(n)
            for dim in ('width','height'):
                if type(obj[dim]) is not int or not 1 <= obj[dim] <= 10000: raise ValueError(tr('Dimensioni tra 1 e 10000'))
            if obj is not f and any(type(obj.get(axis)) is not int for axis in ('x','y')):raise ValueError(tr('Le coordinate devono essere numeri interi.'))
            if obj is not f and obj['kind'] not in KINDS and obj['kind'] not in reg: raise ValueError(tr('Componente sconosciuto'))
            if obj is not f:validate_layout(f,obj,reg)
            validate_productivity(obj.get('kind'),obj.get('props',{}))
            if obj.get('kind')=='DatabaseView':
                props=obj.get('props',{})
                if props.get('backend','sqlite') not in ('sqlite','postgresql','mysql'):raise ValueError(tr('Backend database non supportato'))
                if not 0<=int(props.get('port',0))<=65535 or not 1<=int(props.get('limit',200))<=5000:raise ValueError(tr('Porta o limite database non validi'))
            for ev, body in obj.get('events',{}).items():
                if ev not in EVENTS and ev != 'Load': raise ValueError(tr('Evento sconosciuto'))
                if code: ast.parse('def handler(self, event=None):\n'+ '\n'.join('    '+l for l in (body or 'pass').splitlines()))
    if code: ast.parse(p.get('imports',''))
    if code: ast.parse('def startup(self):\n'+'\n'.join('    '+l for l in (p.get('startup') or 'pass').splitlines()))
    return p

def load(path):
    return validate(json.loads(Path(path).read_text(encoding='utf-8')), code=False)

def generate(p):
    validate(p)
    lines=['# Generated by VisualTk Studio — edit the project to preserve changes.', 'import tkinter','import tkinter as tk','from tkinter import ttk, messagebox, filedialog, simpledialog, colorchooser, font','import traceback',p.get('imports',''),'','class Application:', '    def __init__(self):','        self.root = tk.Tk()','        self.root.withdraw()', '        self.root.report_callback_exception = self._error']
    lines[1:1]=['import sys', 'if __name__ == "__main__" and (sys.version_info[:2] < (3, 15) or sys.version_info.releaselevel != "final"):', '    raise SystemExit("È richiesto Python 3.15 o successivo stabile")']
    language=p.get('language','it')
    if language not in ('it','en'):raise ValueError('Unsupported project language')
    reg=registry(p)
    used=sorted({w['kind'] for f in p['forms'] for w in f['widgets'] if w['kind'] in reg})
    prelude=[]
    if any(w.get('layout') is not None for f in p['forms'] for w in f['widgets']):
        runtime=Path(__file__).with_name('adaptive_layout.py').read_text(encoding='utf-8')
        for public,private in [('EDGES','_VTS_EDGES'),('PARENTS','_VTS_PARENTS'),('validate_layout','_vts_validate_layout'),('anchored_geometry','_vts_anchored_geometry')]:runtime=runtime.replace(public,private)
        prelude.append(runtime)
    embedded={'visualtk_runtime','database_runtime','integration_runtime','productivity_runtime'}
    if any(reg[k]['module'] in embedded for k in used):
        prelude.append(Path(__file__).with_name('i18n.py').read_text(encoding='utf-8')+'\nset_language('+repr(language)+')\n')
    for module in sorted({reg[k]['module'] for k in used}&embedded):
        runtime=Path(__file__).with_name(module+'.py').read_text(encoding='utf-8').replace('from i18n import tr\n','')
        if module=='productivity_runtime':
            prelude.append(Path(__file__).with_name('service_backends.py').read_text(encoding='utf-8'))
            runtime='\n'.join(line for line in runtime.splitlines() if not line.startswith('from service_backends import '))
        prelude.append(runtime)
    for kind in used:
        d=reg[kind]
        if d['module'] not in embedded:prelude.append(f"from {d['module']} import {d['class']} as _component_{kind}")
    # Insert embedded runtime and external imports before the Application class.
    index=lines.index('class Application:'); lines[index:index]=prelude+['']
    config=theme_config(p)
    setup=[]
    if config['provider']!='none':
        index=lines.index('class Application:');lines[index:index]=[Path(__file__).with_name('theme_runtime.py').read_text(encoding='utf-8')]
        setup.append(f"        self._theme_style = apply_project_theme(self.root, {config!r})")
    if p.get('appearance_mode'):
        index=lines.index('class Application:');lines[index:index]=['import customtkinter']
        setup.append(f"        customtkinter.set_appearance_mode({p['appearance_mode']!r})")
    if any(reg[k]['module']=='Pmw' for k in used):setup.extend(['        import Pmw','        Pmw.initialise(self.root)'])
    index=lines.index('        self.root.withdraw()');lines[index+1:index+1]=setup
    handlers=[]
    for f in p['forms']:
        fn=f['name']; ref='self.'+fn
        lines += [f'        {ref} = tk.Toplevel(self.root)', f'        {ref}.withdraw()',f'        {ref}.title({f["title"]!r})',f'        {ref}.geometry({str(f["width"])+"x"+str(f["height"])!r})',f'        {ref}.configure(bg={f["bg"]!r})', f'        {ref}.protocol("WM_DELETE_WINDOW", self.root.destroy)' if f is p['forms'][0] else f'        {ref}.protocol("WM_DELETE_WINDOW", {ref}.withdraw)']
        for w in ordered_widgets(f):
            name=w['name']; kind=w['kind']; wr='self.'+name
            opts=dict(w.get('props',{}))
            if kind in ('Combobox','Progressbar'): opts={k:v for k,v in opts.items() if k in ('values','state','maximum','value','orient','mode')}
            if kind in reg:
                d=reg[kind]; constructor=d['class'] if d['module'] in embedded else '_component_'+kind
            else:constructor=('ttk' if kind in ('Combobox','Progressbar') else 'tk')+'.'+kind
            custom_geometry=kind in reg and reg[kind]['module'].split('.')[0]=='customtkinter'
            if custom_geometry:opts.update(width=int(w['width']),height=int(w['height']))
            parent=w.get('parent');master='self.'+parent if parent and parent!=fn else ref
            if w.get('page'):master+=f".pages[{w['page']!r}]"
            lines.append(f'        {wr} = {constructor}({master}, **{opts!r})')
            placement={'x':int(w['x']),'y':int(w['y'])}
            if not custom_geometry:placement.update(width=int(w['width']),height=int(w['height']))
            lines.append(f'        {wr}.place('+', '.join(f'{key}={value}' for key,value in placement.items())+')')
            for ev,body in w.get('events',{}).items():
                method=f'event_{name}_{ev}'
                if ev=='Load': lines.append(f'        self.root.after_idle(self.{method})')
                else: lines.append(f'        {wr}.bind({EVENTS[ev]!r}, self.{method}, add="+")')
                handlers.append((method,body))
        for ev,body in f.get('events',{}).items():
            method=f'event_{fn}_{ev}'
            lines.append(f'        self.root.after_idle(self.{method})' if ev=='Load' else f'        {ref}.bind({EVENTS[ev]!r}, self.{method}, add="+")')
            handlers.append((method,body))
    for form in p['forms']:
        grouped={};by_name={w['name']:w for w in form['widgets']}
        for widget in form['widgets']:
            if widget.get('layout') is not None:grouped.setdefault((widget.get('parent') or form['name'],widget.get('page')),[]).append(widget)
        for (parent,page),widgets in grouped.items():
            container=by_name.get(parent,form);baseline=(container['width'],container['height'])
            entries=', '.join('(self.'+w['name']+', '+repr({key:w[key] for key in ('x','y','width','height')})+', '+repr(w['layout'])+')' for w in widgets)
            target='self.'+parent+(f'.pages[{page!r}]' if page else '')
            host=', baseline_host=self.'+parent if page else ''
            lines.append('        _vts_install_anchors('+target+', ['+entries+'], '+repr(baseline)+host+')')
    lines += ['        self.startup()','','    def _error(self, kind, value, tb):','        traceback.print_exception(kind, value, tb)',f'        messagebox.showerror({tr("Errore applicazione",language=language)!r}, str(value))','','    def show(self, name):','        getattr(self, name).deiconify()','','    def hide(self, name):','        getattr(self, name).withdraw()','','    def startup(self):']
    lines += ['        '+l for l in (p.get('startup') or 'pass').splitlines()]
    for name,body in handlers:
        lines += ['',f'    def {name}(self, event=None):']+['        '+l for l in (body or 'pass').splitlines()]
    lines += ['','if __name__ == "__main__":','    import sys', '    if sys.version_info[:2] < (3, 15) or sys.version_info.releaselevel != "final":', '        raise SystemExit("È richiesto Python 3.15 o successivo stabile")', '    import multiprocessing', '    multiprocessing.freeze_support()', '    app = Application()','    app.root.mainloop()','']
    source='\n'.join(lines); compile(source,'application.py','exec'); return source
