#!/usr/bin/env python3
"""VisualTk Studio: visual Tkinter designer, event IDE and process debugger."""
from runtime_requirements import ensure_current, validate_interpreter

if __name__ == "__main__":
    try: ensure_current()
    except RuntimeError as exc: raise SystemExit(str(exc))

import builtins
import webbrowser
from support_ui import SupportMixin
import copy
import io
import json
import keyword
import os
from pathlib import Path
import queue
import re
import subprocess
import sys
import tempfile
import threading
import tokenize
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser, simpledialog
from tkinter.scrolledtext import ScrolledText
from core import KINDS, EVENTS, new_project, generate, load, validate, identifier
from components import registry, descriptor, requirements, install_args
from library_explorer import LibraryExplorer
from ux_theme import apply_theme, style_editor
from workspace_ui import WorkspaceMixin
from assist_ui import AssistMixin

BASE = Path(__file__).resolve().parent
SETTINGS = Path.home()/'.visualtkstudio.json'

class Studio(AssistMixin,WorkspaceMixin,SupportMixin,tk.Tk):
    def __init__(self):
        ensure_current()
        super().__init__()
        self.title('VisualTk Studio • Python Visual Development')
        self.geometry('1400x900'); self.minsize(1050,650)
        self.project=new_project(); self.path=None; self.selected=None; self.form_index=0
        self.history=[]; self.future=[]; self.proc=None; self.messages=queue.Queue(); self.code_target=None
        self.temp=tempfile.TemporaryDirectory(prefix='visualtk-'); self.config_data={'grid':10,'font_size':13,'python':str(Path.home()/'Applications/VisualTkStudio/.venv/bin/python') if getattr(sys,'frozen',False) else sys.executable}
        try: self.config_data.update(json.loads(SETTINGS.read_text()))
        except (OSError,ValueError): pass
        self.saved_state=json.dumps(self.project,sort_keys=True); self.drag=None; self.breaks=set()
        self.build(); self.apply_appearance(); self.menus(); self.refresh(); self.after(70,self.poll)
        self.protocol('WM_DELETE_WINDOW',self.close)
        self.bind('<F1>',lambda e:self.help())
        for sequence, action in [('<Command-s>',self.save),('<Control-s>',self.save),('<Command-o>',self.open_project),('<Control-o>',self.open_project),('<Command-z>',self.undo),('<Control-z>',self.undo),('<F5>',self.run),('<Shift-F5>',self.stop),('<F9>',self.debug)]:
            self.bind(sequence,lambda e,a=action:a())

    @property
    def form(self): return self.project['forms'][self.form_index]
    def checkpoint(self):
        self.history.append(copy.deepcopy(self.project)); self.history=self.history[-100:]; self.future.clear()
    def undo(self):
        self.commit_code()
        if self.history:
            self.future.append(copy.deepcopy(self.project)); self.project=self.history.pop(); self.form_index=min(self.form_index,len(self.project['forms'])-1); self.selected=None; self.code_target=None; self.refresh()
    def redo(self):
        if self.future:
            self.history.append(copy.deepcopy(self.project)); self.project=self.future.pop(); self.form_index=min(self.form_index,len(self.project['forms'])-1); self.selected=None; self.code_target=None; self.refresh()
    def build(self):
        apply_theme(self)
        header=ttk.Frame(self,padding=(18,12)); header.pack(fill='x')
        ttk.Label(header,text='VisualTk Studio',style='Brand.TLabel').pack(side='left')
        ttk.Label(header,text='DESIGN  /  CODE  /  BUILD',style='Muted.TLabel').pack(side='left',padx=20)
        ttk.Button(header,text='Guida  F1',command=self.help).pack(side='right')
        toolbar=ttk.Frame(self,padding=(14,0,14,12)); toolbar.pack(fill='x')
        for label,cmd in [('Nuovo',self.new),('Apri',self.open_project),('Salva',self.save),('↶',self.undo),('↷',self.redo),('+ Finestra',self.add_form),('▶ Avvia F5',self.run),('● Debug F9',self.debug),('■ Stop',self.stop),('✓ Verifica',self.check),('Build .app',self.package)]:
            ttk.Button(toolbar,text=label,command=cmd,style='Accent.TButton' if cmd==self.run else 'Toolbar.TButton').pack(side='left',padx=3)
        self.status=tk.StringVar(value='Pronto'); ttk.Label(self,textvariable=self.status,anchor='w',padding=(16,8),style='Muted.TLabel').pack(side='bottom',fill='x')
        vertical=ttk.Panedwindow(self,orient='vertical'); vertical.pack(fill='both',expand=True)
        main=ttk.Panedwindow(vertical,orient='horizontal'); vertical.add(main,weight=5)
        left=ttk.Frame(main,width=190,padding=8); main.add(left,weight=0)
        ttk.Label(left,text='Componenti',style='Title.TLabel').pack(anchor='w')
        self.palette_query=tk.StringVar()
        search=ttk.Entry(left,textvariable=self.palette_query); search.pack(fill='x',pady=(10,4))
        ttk.Label(left,text='Cerca un componente',style='Muted.TLabel').pack(anchor='w')
        self.palette_query.trace_add('write',lambda *_:self.filter_palette())
        self.palette=tk.Listbox(left,height=14,exportselection=False,font=('Helvetica',12),bg='#ffffff',fg='#25324a',selectbackground='#dce8ff',selectforeground='#174eb6',borderwidth=0,highlightthickness=0,activestyle='none'); self.palette.pack(fill='x',pady=5)
        self.kinds=list(KINDS)+list(registry(self.project))
        for k in self.kinds:self.palette.insert('end',k)
        self.palette.bind('<Double-Button-1>',lambda e:self.add_widget())
        ttk.Button(left,text='Inserisci nel form',command=self.add_widget).pack(fill='x')
        ttk.Button(left,text='+ Componente esterno…',command=self.component_wizard).pack(fill='x',pady=5)
        ttk.Label(left,text='Esplora progetto',style='Title.TLabel').pack(anchor='w',pady=(20,5))
        self.tree=ttk.Treeview(left,show='tree',selectmode='browse'); self.tree.pack(fill='both',expand=True)
        self.tree.bind('<<TreeviewSelect>>',self.tree_select)
        center=ttk.Frame(main); main.add(center,weight=4)
        self.tabs=ttk.Notebook(center); self.tabs.pack(fill='both',expand=True)
        design=ttk.Frame(self.tabs); self.tabs.add(design,text='Designer')
        row=ttk.Frame(design,padding=5); row.pack(fill='x')
        self.formvar=tk.StringVar(); self.formbox=ttk.Combobox(row,textvariable=self.formvar,state='readonly',width=22); self.formbox.pack(side='left'); self.formbox.bind('<<ComboboxSelected>>',self.switch_form)
        ttk.Button(row,text='Form…',command=self.manage_forms).pack(side='left',padx=4)
        for label,cmd in [('Evento / doppio clic',self.edit_event),('Duplica',self.duplicate),('Elimina',self.delete),('Allinea X',lambda:self.align('x')),('Allinea Y',lambda:self.align('y'))]:ttk.Button(row,text=label,command=cmd).pack(side='left',padx=2)
        self.canvas=tk.Canvas(design,bg='#e8edf5',highlightthickness=0,scrollregion=(0,0,2000,1600))
        xs=ttk.Scrollbar(design,orient='horizontal',command=self.canvas.xview); xs.pack(side='bottom',fill='x')
        ys=ttk.Scrollbar(design,orient='vertical',command=self.canvas.yview); ys.pack(side='right',fill='y')
        self.canvas.pack(fill='both',expand=True); self.canvas.configure(xscrollcommand=xs.set,yscrollcommand=ys.set)
        self.canvas.bind('<Button-1>',self.press); self.canvas.bind('<B1-Motion>',self.motion); self.canvas.bind('<ButtonRelease-1>',self.release); self.canvas.bind('<Double-Button-1>',lambda e:self.edit_event())
        self.canvas.bind('<Delete>',lambda e:self.delete()); self.canvas.bind('<BackSpace>',lambda e:self.delete())
        for key,dx,dy in [('Left',-1,0),('Right',1,0),('Up',0,-1),('Down',0,1)]: self.canvas.bind('<'+key+'>',lambda e,x=dx,y=dy:self.nudge(x,y))
        codeframe=ttk.Frame(self.tabs); self.tabs.add(codeframe,text='Codice eventi')
        cr=ttk.Frame(codeframe,padding=5); cr.pack(fill='x')
        self.code_label=tk.StringVar(value='Seleziona un componente e un evento')
        ttk.Label(cr,textvariable=self.code_label).pack(side='left')
        self.evvar=tk.StringVar(value='Click'); self.evbox=ttk.Combobox(cr,textvariable=self.evvar,values=['Load']+list(EVENTS),state='readonly',width=14); self.evbox.pack(side='right'); self.evbox.bind('<<ComboboxSelected>>',lambda e:self.edit_event())
        ttk.Button(cr,text='Applica codice',command=self.commit_code).pack(side='right',padx=5)
        self.code=ScrolledText(codeframe,undo=True,bg='#202633',fg='#e2e8f0',insertbackground='white',font=('Menlo',self.config_data['font_size']),tabs=('32',)); self.code.pack(fill='both',expand=True)
        self.build_assistant(codeframe); self.code.bind('<Control-space>',self.complete); self.code.bind('<Tab>',self.tab_indent); self.code.bind('<Return>',self.autoindent)
        for tag,color in [('kw','#c792ea'),('str','#c3e88d'),('comment','#8796a8'),('num','#f78c6c')]:self.code.tag_configure(tag,foreground=color)
        self.generated=ScrolledText(self.tabs,font=('Menlo',12),wrap='none',undo=False); self.tabs.add(self.generated,text='Python generato / breakpoint')
        style_editor(self.code)
        style_editor(self.generated)
        self.generated.bind('<Double-Button-1>',self.toggle_break)
        self.generated.tag_configure('break',background='#f6a0a0',foreground='#111111')
        right=ttk.Frame(main,width=260,padding=8); main.add(right,weight=0)
        ttk.Label(right,text='Proprietà',style='Title.TLabel').pack(anchor='w')
        self.propbox=ttk.Frame(right); self.propbox.pack(fill='x',pady=8)
        self.propvars={}
        ttk.Button(right,text='Applica proprietà',command=self.apply_props).pack(fill='x')
        ttk.Button(right,text='Scegli colore sfondo',command=lambda:self.pick_color('bg')).pack(fill='x',pady=3)
        ttk.Button(right,text='Scegli colore testo',command=lambda:self.pick_color('fg')).pack(fill='x')
        ttk.Button(right,text='Scegli carattere…',command=self.choose_font).pack(fill='x',pady=3)
        ttk.Label(right,text='Trascina per spostare.\nQuadrato in basso: ridimensiona.\nDoppio clic: codice evento.\nCtrl+Spazio: completamento.\n\nCoordinate in pixel.\nI contenitori sono grafici:\nogni controllo appartiene\nalla finestra corrente.',wraplength=235).pack(anchor='w',pady=15)
        bottom=ttk.Frame(vertical); vertical.add(bottom,weight=1)
        br=ttk.Frame(bottom); br.pack(fill='x')
        ttk.Label(br,text='OUTPUT / DEBUG',style='Title.TLabel').pack(side='left',padx=5)
        for label,cmd in [('Continua',lambda:self.debug_cmd('continue')),('Passo',lambda:self.debug_cmd('next')),('Entra',lambda:self.debug_cmd('step')),('Stack',lambda:self.debug_cmd('where')),('Locali',lambda:self.debug_cmd('pp locals()')),('Pulisci',self.clear_log)]:ttk.Button(br,text=label,command=cmd).pack(side='left')
        self.log=ScrolledText(bottom,height=9,bg='#151a23',fg='#dbe6ef',font=('Menlo',11)); self.log.pack(fill='both',expand=True)
        style_editor(self.log)
        self.command=ttk.Entry(bottom); self.command.pack(fill='x'); self.command.bind('<Return>',self.console_command)
        self.command.insert(0,'')
    def menus(self):
        bar=tk.Menu(self); self.config(menu=bar)
        for title,items in [('File',[('Nuovo progetto',self.new),('Apri progetto…',self.open_project),('Salva',self.save),('Salva con nome…',lambda:self.save(True)),('Esporta Python…',self.export),('Esci',self.close)]),('Modifica',[('Annulla',self.undo),('Ripeti',self.redo),('Duplica componente',self.duplicate),('Elimina selezione',self.delete),('Aspetto ambiente…',self.appearance_settings),('Impostazioni…',self.settings)]),('Progetto',[('Gestione form…',self.manage_forms),('Aggiungi finestra',self.add_form),('Codice avvio',lambda:self.global_code('startup')),('Import e funzioni globali',lambda:self.global_code('imports'))]),('Esegui',[('Avvia F5',self.run),('Debug F9',self.debug),('Ferma',self.stop),('Verifica sintassi',self.check),('Crea applicazione',self.package)]),('Librerie',[('Aggiungi componente visuale…',self.component_wizard),('Esplora PyPI…',lambda:LibraryExplorer(self)),('Importa componente visuale…',self.import_component),('Componenti del progetto…',self.component_manager),('Tema del progetto…',self.choose_theme),('Installa dipendenze progetto',self.install_project_dependencies)]),('Help',[('Guida rapida — F1',self.help),('Manuale completo',lambda:self.help_topic('Manuale')),('Componenti ed estensioni',lambda:self.help_topic('Estensioni')),('Esempi di codice',lambda:self.help_topic('Esempi')),('Compatibilità',lambda:self.help_topic('Compatibilità')),('Apri esempi',self.open_examples),('Diagnostica dipendenze',self.diagnostics),('Documentazione online',lambda:webbrowser.open('https://docs.python.org/3/library/tkinter.html')),('Informazioni',lambda:messagebox.showinfo('VisualTk Studio','VisualTk Studio 1.6\nDesigner visuale Python / Tkinter'))])]:
            menu=tk.Menu(bar,tearoff=False); bar.add_cascade(label=title,menu=menu)
            for label,cmd in items:menu.add_command(label=label,command=cmd)
    def filter_palette(self):
        query=self.palette_query.get().strip().casefold()
        self.palette.delete(0,'end')
        for kind in self.kinds:
            if query in kind.casefold():self.palette.insert('end',kind)

    def refresh(self):
        self.kinds=list(KINDS)+list(registry(self.project)); self.palette.delete(0,'end')
        self.filter_palette()
        self.formbox['values']=[f['name'] for f in self.project['forms']]; self.formvar.set(self.form['name'])
        self.tree.delete(*self.tree.get_children())
        for i,f in enumerate(self.project['forms']):
            self.tree.insert('','end',iid='f:'+str(i),text=f['name'],open=True)
            for w in f['widgets']:self.tree.insert('f:'+str(i),'end',iid='w:'+w['name'],text=w['name']+' : '+w['kind'])
        self.draw(); self.properties(); self.update_source()
    def draw(self):
        c=self.canvas; c.delete('all'); f=self.form; ox=30; oy=45
        c.create_text(30,22,text=f['title']+'  —  '+f['name'],anchor='w',fill=self.config_data.get('appearance',{}).get('foreground','#455574'),font=('Helvetica',12,'bold'))
        c.create_rectangle(ox+5,oy+6,ox+f['width']+5,oy+f['height']+6,fill='#cfd8e6',outline='')
        c.create_rectangle(ox,oy,ox+f['width'],oy+f['height'],fill=f['bg'],outline='#909baa',tags='form')
        grid=max(1,int(self.config_data['grid']))
        if grid>=5:
            for x in range(ox,ox+min(f['width'],1600),grid):
                for y in range(oy,oy+min(f['height'],1200),grid): c.create_line(x,y,x+1,y,fill='#bfc6ce')
        for w in f['widgets']:
            x=ox+w['x']; y=oy+w['y']; width=w['width']; height=w['height']; p=w['props']; k=w['kind']
            bg=p.get('bg','#ffffff' if k in ('Entry','Text','Listbox','Combobox','Spinbox') else '#e4e8ee')
            try:
                c.create_rectangle(x,y,x+width,y+height,fill=bg,outline='#8190a1',tags=('widget',w['name']))
                text=p.get('text',k if k not in ('Entry','Text','Canvas','Frame') else '')
                if k in ('Checkbutton','Radiobutton'):text=('☐ ' if k=='Checkbutton' else '○ ')+text
                c.create_text(x+7,y+height/2,text=text,anchor='w',width=max(1,width-12),fill=p.get('fg','#1c2430'),font=p.get('font','Helvetica 12'),tags=('widget',w['name']))
            except tk.TclError: pass
            if self.selected is w:
                c.create_rectangle(x-2,y-2,x+width+2,y+height+2,outline='#1677ff',width=2)
                c.create_rectangle(x+width-5,y+height-5,x+width+5,y+height+5,fill='#1677ff',outline='white',tags='handle')
    def tree_select(self,event=None):
        ids=self.tree.selection()
        if not ids:return
        self.commit_code(); ident=ids[0]
        if ident.startswith('f:'):self.form_index=int(ident[2:]); self.selected=None
        else:
            for i,f in enumerate(self.project['forms']):
                for w in f['widgets']:
                    if 'w:'+w['name']==ident:self.form_index=i; self.selected=w
        self.formvar.set(self.form['name']); self.draw(); self.properties()
    def switch_form(self,event=None):
        self.commit_code(); self.form_index=self.formbox.current(); self.selected=None; self.draw(); self.properties()
    def properties(self):
        for w in self.propbox.winfo_children():w.destroy()
        self.propvars={}; obj=self.selected if self.selected is not None else self.form
        values={k:obj[k] for k in ('name','x','y','width','height','title','bg') if k in obj}
        if self.selected is not None:values.update(obj['props'])
        for i,(key,val) in enumerate(values.items()):
            ttk.Label(self.propbox,text=key,width=10).grid(row=i,column=0,sticky='w',pady=2)
            var=tk.StringVar(value=json.dumps(val,ensure_ascii=False) if isinstance(val,(list,dict)) else str(val)); self.propvars[key]=var
            entry=ttk.Entry(self.propbox,textvariable=var,width=18); entry.grid(row=i,column=1,sticky='ew'); entry.bind('<Return>',lambda e:self.apply_props())
        self.propbox.columnconfigure(1,weight=1)
    def apply_props(self):
        obj=self.selected if self.selected is not None else self.form; candidate=copy.deepcopy(obj)
        try:
            for k,v in self.propvars.items():
                value=v.get()
                if k in ('x','y','width','height'):candidate[k]=int(value)
                elif k in candidate:candidate[k]=value
                else:
                    previous=candidate['props'].get(k)
                    if isinstance(previous,bool):value=value.lower() in ('true','1','yes')
                    elif isinstance(previous,int):value=int(value)
                    elif isinstance(previous,float):value=float(value)
                    elif isinstance(previous,(list,dict)):value=json.loads(value)
                    if k in ('bg','fg','activebackground','selectbackground'):self.winfo_rgb(value)
                    if k=='values' and isinstance(value,str):value=json.loads(value)
                    candidate['props'][k]=value
            if 'bg' in candidate:self.winfo_rgb(candidate['bg'])
            if candidate['name']!=obj['name']:
                raise ValueError('Il nome si assegna alla creazione; rinominare richiede aggiornare il codice utente.')
            probe=copy.deepcopy(self.project)
            if self.selected is None:probe['forms'][self.form_index]=candidate
            else:probe['forms'][self.form_index]['widgets'][self.form['widgets'].index(obj)]=candidate
            validate(probe)
            if self.selected is not None and candidate['kind'] in KINDS:
                cls=getattr(ttk if candidate['kind'] in ('Combobox','Progressbar') else tk,candidate['kind'])
                test=cls(self,**candidate['props']); test.destroy()
            self.checkpoint(); obj.clear(); obj.update(candidate); self.refresh()
        except Exception as exc:messagebox.showerror('Proprietà non valide',str(exc))
    def pick_color(self,key):
        if key in self.propvars:
            value=colorchooser.askcolor(parent=self)[1]
            if value:self.propvars[key].set(value); self.apply_props()
    def unique(self,prefix):
        names={o['name'] for f in self.project['forms'] for o in [f]+f['widgets']}; n=1
        while prefix+str(n) in names:n+=1
        return prefix+str(n)
    def add_widget(self):
        selection=self.palette.curselection()
        if not selection:return
        k=self.palette.get(selection[0]); name=simpledialog.askstring('Nome componente','Nome Python del componente:',initialvalue=self.unique(k),parent=self)
        if name is None:return
        names={o['name'] for f in self.project['forms'] for o in [f]+f['widgets']}
        if not identifier(name) or name in names:return messagebox.showerror('Nome','Nome Python non valido o già utilizzato.')
        props={}
        if k in ('Button','Label','Checkbutton','Radiobutton'):props['text']=name
        if k not in ('Combobox','Progressbar'):props.update(bg='#ffffff' if k in ('Entry','Text','Listbox','Spinbox') else '#e4e8ee')
        if k not in ('Frame','Canvas','Progressbar','Combobox'):props.update(fg='#182230',font='Helvetica 12')
        if k=='Combobox':props={'values':['Prima','Seconda'],'state':'readonly'}
        if k=='Progressbar':props={'value':40,'maximum':100}
        if k in ('Button','Entry','Text','Checkbutton','Radiobutton','Listbox','Combobox','Scale','Spinbox'):props['state']='normal' if k!='Combobox' else 'readonly'
        if k in registry(self.project):props=copy.deepcopy(registry(self.project)[k].get('defaults',{}))
        self.checkpoint(); self.selected={'name':name,'kind':k,'x':30,'y':30,'width':480 if k in registry(self.project) else 140,'height':280 if k in registry(self.project) else (90 if k in ('Text','Listbox','Canvas','Frame') else 35),'props':props,'events':{}}
        self.form['widgets'].append(self.selected); self.refresh()
    def add_form(self):
        name=simpledialog.askstring('Nuova finestra','Nome Python:',initialvalue=self.unique('Form'),parent=self)
        if name is None:return
        if not identifier(name) or any(name==o['name'] for f in self.project['forms'] for o in [f]+f['widgets']):return messagebox.showerror('Nome','Nome non valido o duplicato')
        self.commit_code(); self.checkpoint(); self.project['forms'].append({'name':name,'title':name,'width':640,'height':440,'bg':'#f0f0f0','widgets':[],'events':{}}); self.form_index=len(self.project['forms'])-1; self.selected=None; self.refresh()
    def press(self,e):
        self.canvas.focus_set(); self.commit_code(); x=self.canvas.canvasx(e.x)-30; y=self.canvas.canvasy(e.y)-45
        resize=False; target=None
        if self.selected:
            w=self.selected
            if abs(x-w['x']-w['width'])<9 and abs(y-w['y']-w['height'])<9:target=w; resize=True
        if target is None:
            for w in reversed(self.form['widgets']):
                if w['x']<=x<=w['x']+w['width'] and w['y']<=y<=w['y']+w['height']:target=w; break
        self.selected=target
        if target:self.drag=(x,y,copy.deepcopy(target),resize); self.checkpoint()
        self.draw(); self.properties()
    def motion(self,e):
        if not self.drag or not self.selected:return
        x,y,original,resize=self.drag; dx=self.canvas.canvasx(e.x)-30-x; dy=self.canvas.canvasy(e.y)-45-y; grid=max(1,int(self.config_data['grid']))
        def snap(n):return round(n/grid)*grid
        if resize:self.selected['width']=max(10,snap(original['width']+dx)); self.selected['height']=max(10,snap(original['height']+dy))
        else:self.selected['x']=max(0,snap(original['x']+dx)); self.selected['y']=max(0,snap(original['y']+dy))
        self.draw()
    def release(self,e):
        if self.drag:self.drag=None; self.properties(); self.update_source()
    def nudge(self,x,y):
        if self.selected:self.checkpoint(); self.selected['x']=max(0,self.selected['x']+x); self.selected['y']=max(0,self.selected['y']+y); self.draw(); self.properties(); self.update_source()
    def duplicate(self):
        if self.selected:
            self.commit_code(); self.checkpoint(); w=copy.deepcopy(self.selected); w['name']=self.unique(w['kind']); w['x']+=20; w['y']+=20; self.form['widgets'].append(w); self.selected=w; self.refresh()
    def delete(self):
        if self.selected:
            self.commit_code(); self.checkpoint(); self.form['widgets'].remove(self.selected); self.selected=None; self.code_target=None; self.code.delete('1.0','end'); self.refresh()
        elif len(self.project['forms'])>1 and messagebox.askyesno('Elimina finestra','Eliminare la finestra e tutti i suoi componenti?'):
            self.commit_code(); self.checkpoint(); del self.project['forms'][self.form_index]; self.form_index=0; self.code_target=None; self.refresh()
    def align(self,axis):
        if self.selected:
            self.checkpoint(); self.selected[axis]=0; self.draw(); self.properties(); self.update_source()
    def commit_code(self):
        if not self.code_target:return
        obj,key,global_=self.code_target; value=self.code.get('1.0','end-1c')
        dest=obj if global_ else obj.setdefault('events',{})
        if value!=dest.get(key,''):
            self.checkpoint(); dest[key]=value
        self.update_source()
    def edit_event(self):
        self.commit_code(); obj=self.selected if self.selected is not None else self.form; event=self.evvar.get()
        self.code_target=(obj,event,False); self.code_label.set(obj['name']+' → '+event+'(self, event=None)')
        self.code.delete('1.0','end'); self.code.insert('1.0',obj.get('events',{}).get(event,'pass')); self.tabs.select(1); self.highlight(); self.code.focus_set(); self.update_assistant()
    def global_code(self,key):
        self.commit_code(); self.code_target=(self.project,key,True); self.code_label.set('Progetto → '+key); self.code.delete('1.0','end'); self.code.insert('1.0',self.project.get(key,'')); self.tabs.select(1); self.highlight(); self.update_assistant()
    def highlight(self):
        for tag in ('kw','str','comment','num'):self.code.tag_remove(tag,'1.0','end')
        try:
            for tok in tokenize.generate_tokens(io.StringIO(self.code.get('1.0','end-1c')).readline):
                tag='kw' if keyword.iskeyword(tok.string) else {tokenize.STRING:'str',tokenize.COMMENT:'comment',tokenize.NUMBER:'num'}.get(tok.type)
                if tag:self.code.tag_add(tag,f'{tok.start[0]}.{tok.start[1]}',f'{tok.end[0]}.{tok.end[1]}')
        except (tokenize.TokenError,IndentationError,SyntaxError):pass
    def tab_indent(self,event):
        if self.assist_popup:return self.accept_completion()
        self.code.insert('insert','    '); return 'break'
    def autoindent(self,event):
        if self.assist_popup:return self.accept_completion()
        line=self.code.get('insert linestart','insert'); indent=re.match(r'\s*',line).group(); self.code.insert('insert','\n'+indent+('    ' if line.rstrip().endswith(':') else '')); return 'break'
    def update_source(self):
        try:
            source=generate(self.project); self.generated.configure(state='normal'); self.generated.delete('1.0','end'); self.generated.insert('1.0',source)
            for line in self.breaks:self.generated.tag_add('break',f'{line}.0',f'{line}.end')
            self.generated.configure(state='disabled'); self.status.set('Pronto • '+('* modificato • ' if json.dumps(self.project,sort_keys=True)!=self.saved_state else '')+(str(self.path) if self.path else 'Progetto senza nome'))
        except Exception as exc:self.status.set('Codice da correggere: '+str(exc))
    def toggle_break(self,e):
        line=int(self.generated.index('@%s,%s'%(e.x,e.y)).split('.')[0])
        if line in self.breaks:self.breaks.remove(line)
        else:self.breaks.add(line)
        self.update_source(); return 'break'
    def dirty_guard(self):
        self.commit_code()
        if json.dumps(self.project,sort_keys=True)==self.saved_state:return True
        answer=messagebox.askyesnocancel('Modifiche non salvate','Salvare le modifiche prima di proseguire?')
        if answer is None:return False
        return self.save() if answer else True
    def new(self):
        if not self.dirty_guard():return
        self.project=new_project(); self.path=None; self.form_index=0; self.selected=None; self.code_target=None; self.history=[]; self.future=[]; self.breaks=set(); self.saved_state=json.dumps(self.project,sort_keys=True); self.code.delete('1.0','end'); self.refresh()
    def open_project(self):
        if not self.dirty_guard():return
        path=filedialog.askopenfilename(filetypes=[('VisualTk project','*.vtk.json'),('JSON','*.json')])
        if not path:return
        try:p=load(path)
        except Exception as exc:return messagebox.showerror('Apertura',str(exc))
        self.project=p; self.path=Path(path); self.form_index=0; self.selected=None; self.code_target=None; self.history=[]; self.future=[]; self.breaks=set(); self.saved_state=json.dumps(p,sort_keys=True); self.code.delete('1.0','end'); self.refresh()
    def save(self,as_new=False):
        self.commit_code()
        path=self.path
        if as_new or path is None:
            s=filedialog.asksaveasfilename(defaultextension='.vtk.json',filetypes=[('VisualTk project','*.vtk.json')]); path=Path(s) if s else None
        if path is None:return False
        try:
            # Save even unfinished code, allowing recovery after syntax errors.
            temp=path.with_name(path.name+'.tmp'); temp.write_text(json.dumps(self.project,indent=2,ensure_ascii=False),encoding='utf-8'); temp.replace(path)
            self.path=path; self.saved_state=json.dumps(self.project,sort_keys=True); self.update_source(); return True
        except OSError as exc:messagebox.showerror('Salvataggio',str(exc)); return False
    def check(self):
        self.commit_code()
        try:compile(generate(self.project),'application.py','exec'); self.write_log('✓ Sintassi e modello validi.\n'); return True
        except Exception as exc:self.write_log('ERRORE: '+str(exc)+'\n'); messagebox.showerror('Verifica',str(exc)); return False
    def export(self):
        if not self.check():return
        p=filedialog.asksaveasfilename(defaultextension='.py',initialfile='application.py')
        if p:
            try:
                Path(p).write_text(generate(self.project),encoding='utf-8'); self.write_requirements(Path(p).parent); self.write_log('Esportato: '+p+'\n')
            except OSError as exc:messagebox.showerror('Esportazione',str(exc))
    def write_log(self,s):self.log.insert('end',s); self.log.see('end')
    def clear_log(self):self.log.delete('1.0','end')
    def launch(self,args,cwd=None):
        if self.proc and self.proc.poll() is None:return messagebox.showwarning('Processo attivo','Arresta il processo corrente prima di avviarne un altro.')
        try:
            validate_interpreter(args[0])
            self.proc=subprocess.Popen(args,cwd=cwd,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,bufsize=0,env={**os.environ,'PYTHONUNBUFFERED':'1'})
        except (OSError,ValueError) as exc:return messagebox.showerror('Avvio',str(exc))
        proc=self.proc; self.write_log('\n$ '+ ' '.join(map(str,args))+'\n')
        def read():
            import codecs
            decoder=codecs.getincrementaldecoder('utf-8')('replace')
            while True:
                data=os.read(proc.stdout.fileno(),4096)
                if not data:break
                self.messages.put(decoder.decode(data))
            self.messages.put(decoder.decode(b'',final=True)); self.messages.put(f'\n[Processo terminato: {proc.wait()}]\n')
        threading.Thread(target=read,daemon=True).start()
    def poll(self):
        try:
            while True:self.write_log(self.messages.get_nowait())
        except queue.Empty:pass
        self.after(70,self.poll)
    def runtime_file(self):
        path=Path(self.temp.name)/'application.py'; path.write_text(generate(self.project),encoding='utf-8'); return path
    def run(self):
        if self.proc and self.proc.poll() is None:return messagebox.showwarning('Processo attivo','Arresta prima il processo corrente.')
        if self.check():self.launch([self.config_data['python'],'-u',str(self.runtime_file())],cwd=str(self.path.parent if self.path else BASE))
    def debug(self):
        if self.proc and self.proc.poll() is None:return messagebox.showwarning('Processo attivo','Arresta prima il processo corrente.')
        if not self.check():return
        args=[self.config_data['python'],'-u','-m','pdb']
        for line in sorted(self.breaks):args+=['-c',f'break {line}']
        args.append(str(self.runtime_file())); self.launch(args,cwd=str(self.path.parent if self.path else BASE)); self.write_log('Debug pdb: continue, next, step, pp espressione, where, break N, quit.\nLa GUI si blocca intenzionalmente ai breakpoint.\n'); self.command.focus_set()
    def debug_cmd(self,text):
        if self.proc and self.proc.poll() is None:
            try:self.proc.stdin.write((text+'\n').encode()); self.proc.stdin.flush()
            except (OSError,ValueError):pass
    def console_command(self,event=None):
        command=self.command.get(); self.command.delete(0,'end'); self.write_log('> '+command+'\n'); self.debug_cmd(command)
    def stop(self):
        if self.proc and self.proc.poll() is None:
            proc=self.proc; proc.terminate()
            def kill():
                if proc.poll() is None:proc.kill()
            self.after(1500,kill)
    def package(self):
        if self.proc and self.proc.poll() is None:return messagebox.showwarning('Processo attivo','Arresta prima il processo corrente.')
        if not self.check():return
        out=filedialog.askdirectory(title='Cartella di destinazione build')
        if not out:return
        try:
            source=Path(out)/'application.py'; source.write_text(generate(self.project),encoding='utf-8'); self.write_requirements(Path(out))
            self.launch([self.config_data['python'],str(BASE/'build_project.py'),str(source)],cwd=out)
        except OSError as exc:messagebox.showerror('Build',str(exc))
    def write_requirements(self,directory):
        (directory/'requirements-visualtk.txt').write_text('\n'.join(requirements(self.project))+'\n',encoding='utf-8')
    def install_project_dependencies(self):
        self.commit_code()
        try:specs=requirements(self.project)
        except Exception as exc:return messagebox.showerror('Dipendenze',str(exc))
        if not specs:return messagebox.showinfo('Dipendenze','Nessuna dipendenza esterna richiesta dai componenti attuali.')
        if messagebox.askyesno('Dipendenze progetto','Installare nell’interprete configurato?\n'+self.config_data['python']+'\n\n'+'\n'.join(specs)):
            self.launch(install_args(self.config_data['python'],specs))
    def import_component(self):
        path=filedialog.askopenfilename(title='Descrittore componente visuale',filetypes=[('VisualTk component','*.vtk-component.json'),('JSON','*.json')])
        if not path:return
        try:
            data=json.loads(Path(path).read_text(encoding='utf-8'));name=data['name'];desc=descriptor(data)
            if name in registry(self.project):return messagebox.showinfo('Componente','Componente già disponibile nella palette.')
            if not identifier(name) or name in KINDS:raise ValueError('Nome componente non valido')
            self.commit_code();self.checkpoint();self.project.setdefault('components',{})[name]=desc;self.refresh()
            messagebox.showinfo('Componente aggiunto','Il componente è nella palette. Installa le sue dipendenze prima di avviarlo. Il modulo non viene importato durante il design.')
        except Exception as exc:messagebox.showerror('Importazione componente',str(exc))
    def component_manager(self):
        win=tk.Toplevel(self);win.title('Componenti visuali');win.geometry('720x450');text=ScrolledText(win,wrap='word');text.pack(fill='both',expand=True)
        for name,desc in registry(self.project).items():
            text.insert('end',name+' — '+desc.get('description','')+'\n'+desc['module']+'.'+desc['class']+'\nDipendenze: '+', '.join(desc.get('requirements',[]))+'\n\n')
        text.insert('end','Per aggiungere un widget di una libreria esterna importa un descrittore JSON. Esempio in examples/CTkButton.vtk-component.json. La classe deve accettare master e le proprietà defaults, e supportare place e bind. Le dipendenze sono installate solo su richiesta.');text.configure(state='disabled')

    def settings(self):
        win=tk.Toplevel(self); win.title('Impostazioni'); win.transient(self); vars={}
        for row,(key,label) in enumerate([('grid','Griglia pixel (1–100)'),('font_size','Font codice (8–32)'),('python','Interprete Python (con Tk)')]):
            ttk.Label(win,text=label).grid(row=row,column=0,padx=10,pady=8); vars[key]=tk.StringVar(value=str(self.config_data[key])); ttk.Entry(win,textvariable=vars[key],width=48).grid(row=row,column=1,padx=10)
        def apply():
            try:
                data={**self.config_data,**{k:v.get() for k,v in vars.items()}}; data['grid']=int(data['grid']); data['font_size']=int(data['font_size'])
                if not 1<=data['grid']<=100 or not 8<=data['font_size']<=32:raise ValueError('Valori fuori intervallo')
                if not Path(data['python']).is_file():raise ValueError('Interprete inesistente')
                validate_interpreter(data['python'])
                SETTINGS.write_text(json.dumps(data,indent=2),encoding='utf-8'); self.config_data=data; self.code.configure(font=('Menlo',data['font_size'])); self.draw(); win.destroy()
            except Exception as exc:messagebox.showerror('Impostazioni',str(exc),parent=win)
        ttk.Button(win,text='Salva',command=apply).grid(row=3,column=1,pady=12)
    def help(self):self.help_topic('Guida rapida')
    def close(self):
        if not self.dirty_guard():return
        self.stop()
        if self.proc and self.proc.poll() is None:
            try:self.proc.wait(timeout=2)
            except subprocess.TimeoutExpired:self.proc.kill(); self.proc.wait()
        self.temp.cleanup(); self.destroy()

HELP='''VISUALTK STUDIO 1.3.1 — Guida rapida

Novità: 36 controlli/descrittori in palette. Per web/video, drag & drop,
calendari, temi e dipendenze consulta le sezioni Estensioni e Compatibilità.
Help offre esempi di codice, diagnostica e ricerca nei documenti.


1. Doppio clic su un componente nella palette per inserirlo.
2. Trascina sul designer; usa il quadratino blu per ridimensionare.
3. Modifica le proprietà e premi Applica. I colori si scelgono anche dal dialogo.
4. Doppio clic sul componente apre il codice. Seleziona Click, DoubleClick,
   Enter, Leave, KeyPress, FocusIn, FocusOut, Change o Load.
5. Scrivi soltanto il corpo del metodo (senza def). self è l'applicazione;
   ogni controllo è accessibile come self.Button1, self.Entry1, ecc.

Esempio Click di Button1:
    nome = self.Entry1.get()
    self.Label1.configure(text="Ciao " + nome)
    self.show("Form2")

Load viene eseguito dopo la creazione di tutte le finestre e all'avvio del loop.
Change è l'evento di selezione dei Combobox; KeyPress offre event.keysym.
Click usa il mouse, non l'attivazione da tastiera del Button.
Import e funzioni globali: codice a livello modulo. Codice avvio: corpo metodo.
Il codice eventi non è eseguito durante il disegno.

F5 avvia un processo separato; Shift-F5 lo termina. F9 avvia pdb.
Nel Python generato, doppio clic su una riga per impostare/togliere breakpoint.
I breakpoint sono numeri di riga: ricontrollali dopo modifiche al progetto.
Usa Continua per entrare nel mainloop, quindi interagisci con la finestra.
Quando scatta un breakpoint, usa Passo, Entra, Stack, Locali o la console.
Nella console: p self.Entry1.get(), pp locals(), break N, continue, quit.
Gli errori nei callback sono mostrati a video e nell'output con traceback.

Ctrl+Spazio apre i suggerimenti (Jedi se installato e nomi del progetto).
Tab inserisce 4 spazi, Invio mantiene l'indentazione, sintassi colorata.
Annulla/Ripeti riguardano il progetto; l'editor ha anche undo nativo Tk.
Il salvataggio e la riapertura JSON conservano anche codice incompleto;
la verifica sintattica è obbligatoria prima di esecuzione ed esportazione.

Build usa PyInstaller nell'interprete configurato. Su Mac crea .app sul Mac;
non è cross-compilazione. Firma e notarizzazione Apple sono passaggi esterni.
Le risorse esterne e le dipendenze specifiche del progetto vanno gestite
separatamente. Il designer usa posizionamento assoluto, non pack/grid.
Frame e Canvas non contengono controlli annidati in questa versione.
Il codice utente viene eseguito con i permessi dell'utente: apri progetti fidati.
'''

if __name__=='__main__':
    Studio().mainloop()
