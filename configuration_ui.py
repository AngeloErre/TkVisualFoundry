"""Discoverable configuration center and component-specific setup."""
import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from components import registry
from dependency_manager import dependency_plan,NOTES
from dependency_ui import DependencyWizard
from runtime_requirements import validate_interpreter

class ConfigurationMixin:
    def open_dependencies(self,kind=None,props=None,on_ready=None,allow_skip=False,specs=None):
        previous=getattr(self,'dependency_window',None)
        if previous and previous.winfo_exists():previous.lift();return previous
        self.dependency_window=DependencyWizard(self,kind,props,on_ready,allow_skip,specs);return self.dependency_window

    def palette_info(self,event=None):
        sel=self.palette.curselection()
        if not sel:self.palette_details.set('Scegli un componente per vedere funzioni e requisiti.');return
        kind=self.palette.get(sel[0]);desc=registry(self.project).get(kind,{})
        specs=dependency_plan(self.project,kind)
        self.palette_details.set(desc.get('description','Controllo Tkinter standard.')+'\n'+('PIP: '+', '.join(specs) if specs else 'Pronto con Python/Tkinter • nessun pacchetto PIP.'))

    def selected_dependencies(self):
        obj=self.selected
        return self.open_dependencies(obj['kind'],obj.get('props',{})) if obj else self.open_dependencies()

    def configure_component(self):
        if self.selected and self.selected['kind']=='DatabaseView':return self.database_setup()
        return self.selected_dependencies()

    def database_setup(self):
        obj=self.selected
        if not obj or obj['kind']!='DatabaseView':return messagebox.showinfo('Database','Inserisci e seleziona DatabaseView dalla palette.')
        win=tk.Toplevel(self);win.title('Configura componente database');win.transient(self);win.geometry('720x550')
        ttk.Label(win,text='Connessione e tabella dati',style='Brand.TLabel',padding=12).pack(anchor='w')
        body=ttk.Frame(win,padding=12);body.pack(fill='x');fields={}
        labels={'backend':'Tipo database','database':'File SQLite / database remoto','host':'Host remoto','port':'Porta (0 = predefinita)','username':'Utente remoto','password_env':'Variabile ambiente password','table':'Tabella iniziale (facoltativa)','limit':'Righe visualizzate (1–5000)'}
        defaults=registry(self.project)['DatabaseView']['defaults']
        for i,(key,label) in enumerate(labels.items()):
            value=obj['props'].get(key,defaults.get(key,''));fields[key]=tk.StringVar(value=str(value));ttk.Label(body,text=label).grid(row=i,column=0,pady=7,sticky='w')
            control=ttk.Combobox(body,textvariable=fields[key],values=['sqlite','postgresql','mysql'],state='readonly',width=35) if key=='backend' else ttk.Entry(body,textvariable=fields[key],width=38)
            control.grid(row=i,column=1,padx=10,sticky='ew')
        def browse():
            path=filedialog.asksaveasfilename(parent=win,defaultextension='.sqlite',filetypes=[('SQLite','*.sqlite *.db'),('Tutti','*')])
            if path:fields['database'].set(path)
        ttk.Button(body,text='Scegli…',command=browse).grid(row=1,column=2)
        note=tk.StringVar();ttk.Label(win,textvariable=note,wraplength=670,padding=12).pack(fill='x')
        def update(*args):
            props={k:v.get() for k,v in fields.items()};specs=dependency_plan(self.project,'DatabaseView',props)
            note.set(('Nessun pacchetto necessario: SQLite è incluso in Python.' if not specs else 'Da installare: '+', '.join(specs))+'\nLa password verrà chiesta alla connessione oppure letta dalla variabile ambiente indicata; non viene salvata nel progetto.')
        fields['backend'].trace_add('write',update);update()
        def save(install=False):
            try:
                props={k:v.get().strip() for k,v in fields.items()};props['port']=int(props['port']);props['limit']=int(props['limit'])
                if not 0<=props['port']<=65535 or not 1<=props['limit']<=5000:raise ValueError('Porta o limite righe non validi.')
                if not props['database']:raise ValueError('Indica un file SQLite o un nome database.')
                if props['password_env'] and not props['password_env'].isidentifier():raise ValueError('Nome della variabile ambiente non valido.')
                self.commit_code();self.checkpoint();obj['props'].update(props);self.refresh();win.destroy()
                if install:self.open_dependencies('DatabaseView',props)
            except Exception as exc:messagebox.showerror('Configurazione database',str(exc),parent=win)
        row=ttk.Frame(win,padding=12);row.pack(fill='x')
        ttk.Button(row,text='Salva configurazione',command=save).pack(side='right',padx=4);ttk.Button(row,text='Salva e prepara dipendenze…',command=lambda:save(True)).pack(side='right',padx=4)

    def settings(self):
        win=tk.Toplevel(self);win.title('Configurazione • VisualTk Studio');win.geometry('740x490');win.transient(self)
        ttk.Label(win,text='Configura il tuo ambiente di lavoro',style='Brand.TLabel',padding=15).pack(anchor='w')
        tabs=ttk.Notebook(win);tabs.pack(fill='both',expand=True,padx=12,pady=8)
        general=ttk.Frame(tabs,padding=15);packages=ttk.Frame(tabs,padding=15);appearance=ttk.Frame(tabs,padding=15)
        tabs.add(general,text='Python e designer');tabs.add(packages,text='Pacchetti e componenti');tabs.add(appearance,text='Aspetto')
        fields={}
        for i,(key,label) in enumerate([('python','Interprete Python dei progetti'),('grid','Griglia designer (1–100 px)'),('font_size','Carattere editor (8–32)')]):
            fields[key]=tk.StringVar(value=str(self.config_data[key]));ttk.Label(general,text=label).grid(row=i,column=0,sticky='w',pady=12);ttk.Entry(general,textvariable=fields[key],width=43).grid(row=i,column=1,padx=8)
        def browse():
            path=filedialog.askopenfilename(parent=win,title='Seleziona Python con Tkinter')
            if path:fields['python'].set(path)
        ttk.Button(general,text='Sfoglia…',command=browse).grid(row=0,column=2)
        ttk.Label(general,text='Tutti i pacchetti del wizard saranno installati in questo Python.\nPuoi scegliere il Python di un ambiente virtuale.',wraplength=650).grid(row=3,column=0,columnspan=3,sticky='w',pady=16)
        flags={}
        for key,label,default in [('dependency_before_insert','Mostra i requisiti prima di aggiungere un componente esterno',True),('dependency_before_run','Verifica i pacchetti prima di Avvia / Debug',True),('pip_binary_only','Preferisci pacchetti precompilati nel wizard PIP',True)]:
            flags[key]=tk.BooleanVar(value=self.config_data.get(key,default));ttk.Checkbutton(packages,text=label,variable=flags[key]).pack(anchor='w',pady=10)
        ttk.Button(packages,text='Apri wizard PIP…',command=self.open_dependencies).pack(anchor='w',pady=12)
        ttk.Label(appearance,text='Scegli un preset oppure personalizza i colori dell’IDE.\nI colori delle finestre create si modificano nel designer.',wraplength=650).pack(anchor='w',pady=15)
        ttk.Button(appearance,text='Temi e colori…',command=self.appearance_settings).pack(anchor='w')
        status=tk.StringVar();ttk.Label(win,textvariable=status,padding=8).pack(fill='x')
        def save():
            try:
                updated={**self.config_data,**{k:v.get() for k,v in fields.items()},**{k:v.get() for k,v in flags.items()}};updated['grid']=int(updated['grid']);updated['font_size']=int(updated['font_size'])
                if not 1<=updated['grid']<=100 or not 8<=updated['font_size']<=32:raise ValueError('Griglia o carattere fuori intervallo.')
                if not Path(updated['python']).is_file():raise ValueError('Interprete inesistente.')
                validate_interpreter(updated['python'])
                (Path.home()/'.visualtkstudio.json').write_text(json.dumps(updated,indent=2),encoding='utf-8');self.config_data=updated;self.code.configure(font=('Menlo',updated['font_size']));self.draw();win.destroy()
            except Exception as exc:status.set(str(exc))
        row=ttk.Frame(win,padding=12);row.pack(fill='x');ttk.Button(row,text='Salva configurazione',command=save,style='Accent.TButton').pack(side='right');ttk.Button(row,text='Annulla',command=win.destroy).pack(side='right',padx=8)
