"""Discoverable configuration center and component-specific setup."""
from library_explorer import LibraryExplorer
from i18n import tr,get_language,LANGUAGES
import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk,filedialog,messagebox,simpledialog
from components import registry,install_args
from dependency_manager import dependency_plan,NOTES
from dependency_ui import DependencyWizard
from runtime_requirements import validate_interpreter

class ConfigurationMixin:
    def open_dependencies(self,kind=None,props=None,on_ready=None,allow_skip=False,specs=None,auto_install=None):
        previous=getattr(self,'dependency_window',None)
        if previous and previous.winfo_exists():
            if specs is not None and not previous.busy and (previous.python!=self.config_data['python'] or list(specs)!=previous.specs):previous.dispose()
            else:previous.lift();return previous
        self.dependency_window=DependencyWizard(self,kind,props,on_ready,allow_skip,specs,auto_install=bool(on_ready) and self.config_data.get('pip_auto_install',True) if auto_install is None else auto_install);return self.dependency_window

    def install_package(self):
        return LibraryExplorer(self)

    def palette_info(self,event=None):
        sel=self.palette.curselection()
        if not sel:self.palette_details.set(tr('Scegli un componente per vedere funzioni e requisiti.'));return
        kind=self.palette.get(sel[0]);desc=registry(self.project).get(kind,{})
        specs=dependency_plan(self.project,kind)
        self.palette_details.set(desc.get('description',tr('Controllo Tkinter standard.'))+'\n'+('PIP: '+', '.join(specs) if specs else tr('Pronto con Python/Tkinter • nessun pacchetto PIP.')))

    def palette_dependencies(self):
        selection=self.palette.curselection()
        if not selection:return messagebox.showinfo(tr('Componente'),tr('Seleziona un componente nella palette.'))
        return self.open_dependencies(self.palette.get(selection[0]),auto_install=True)

    def selected_dependencies(self):
        obj=self.selected
        return self.open_dependencies(obj['kind'],obj.get('props',{}),auto_install=True) if obj else self.palette_dependencies()

    def configure_component(self):
        from productivity_specs import PRODUCTIVITY_COMPONENTS
        if self.selected and self.selected['kind'] in PRODUCTIVITY_COMPONENTS:return self.productivity_setup()
        if self.selected and self.selected['kind']=='DatabaseView':return self.database_setup()
        return self.selected_dependencies()

    def database_setup(self):
        obj=self.selected
        if not obj or obj['kind']!='DatabaseView':return messagebox.showinfo('Database',tr('Inserisci e seleziona DatabaseView dalla palette.'))
        win=tk.Toplevel(self);win.title(tr('Configura componente database'));win.transient(self);win.geometry('720x550')
        ttk.Label(win,text=tr('Connessione e tabella dati'),style='Brand.TLabel',padding=12).pack(anchor='w')
        body=ttk.Frame(win,padding=12);body.pack(fill='x');fields={}
        labels={'backend':tr('Tipo database'),'database':tr('File SQLite / database remoto'),'host':tr('Host remoto'),'port':tr('Porta (0 = predefinita)'),'username':tr('Utente remoto'),'password_env':tr('Variabile ambiente password'),'table':tr('Tabella iniziale (facoltativa)'),'limit':tr('Righe visualizzate (1–5000)')}
        defaults=registry(self.project)['DatabaseView']['defaults']
        for i,(key,label) in enumerate(labels.items()):
            value=obj['props'].get(key,defaults.get(key,''));fields[key]=tk.StringVar(value=str(value));ttk.Label(body,text=label).grid(row=i,column=0,pady=7,sticky='w')
            control=ttk.Combobox(body,textvariable=fields[key],values=['sqlite','postgresql','mysql'],state='readonly',width=35) if key=='backend' else ttk.Entry(body,textvariable=fields[key],width=38)
            control.grid(row=i,column=1,padx=10,sticky='ew')
        def browse():
            path=filedialog.asksaveasfilename(parent=win,defaultextension='.sqlite',filetypes=[('SQLite','*.sqlite *.db'),(tr('Tutti'),'*')])
            if path:fields['database'].set(path)
        ttk.Button(body,text=tr('Scegli…'),command=browse).grid(row=1,column=2)
        note=tk.StringVar();ttk.Label(win,textvariable=note,wraplength=670,padding=12).pack(fill='x')
        def update(*args):
            props={k:v.get() for k,v in fields.items()};specs=dependency_plan(self.project,'DatabaseView',props)
            note.set((tr('Nessun pacchetto necessario: SQLite è incluso in Python.') if not specs else tr('Da installare: ')+', '.join(specs))+tr('\nLa password verrà chiesta alla connessione oppure letta dalla variabile ambiente indicata; non viene salvata nel progetto.'))
        fields['backend'].trace_add('write',update);update()
        def save(install=False):
            try:
                props={k:v.get().strip() for k,v in fields.items()};props['port']=int(props['port']);props['limit']=int(props['limit'])
                if not 0<=props['port']<=65535 or not 1<=props['limit']<=5000:raise ValueError(tr('Porta o limite righe non validi.'))
                if not props['database']:raise ValueError(tr('Indica un file SQLite o un nome database.'))
                if props['password_env'] and not props['password_env'].isidentifier():raise ValueError(tr('Nome della variabile ambiente non valido.'))
                self.commit_code();self.checkpoint();obj['props'].update(props);self.refresh();win.destroy()
                if install:self.open_dependencies('DatabaseView',props,auto_install=True)
            except Exception as exc:messagebox.showerror(tr('Configurazione database'),str(exc),parent=win)
        row=ttk.Frame(win,padding=12);row.pack(fill='x')
        ttk.Button(row,text=tr('Salva configurazione'),command=save).pack(side='right',padx=4);ttk.Button(row,text=tr('Salva e prepara dipendenze…'),command=lambda:save(True)).pack(side='right',padx=4)

    def settings(self):
        win=tk.Toplevel(self);win.title(tr('Configurazione • VisualTk Studio'));win.geometry('760x590');win.minsize(680,510);win.transient(self);win.columnconfigure(0,weight=1);win.rowconfigure(1,weight=1)
        ttk.Label(win,text=tr('Configura il tuo ambiente di lavoro'),style='Brand.TLabel',padding=15).grid(row=0,column=0,sticky='w')
        tabs=ttk.Notebook(win);tabs.grid(row=1,column=0,sticky='nsew',padx=12,pady=8)
        general=ttk.Frame(tabs,padding=15);packages=ttk.Frame(tabs,padding=15);appearance=ttk.Frame(tabs,padding=15)
        tabs.add(general,text=tr('Python e designer'));tabs.add(packages,text=tr('Pacchetti e componenti'));tabs.add(appearance,text=tr('Aspetto'))
        fields={}
        for i,(key,label) in enumerate([('python',tr('Interprete Python dei progetti')),('grid',tr('Griglia designer (1–100 px)')),('font_size',tr('Carattere editor (8–32)'))]):
            fields[key]=tk.StringVar(value=str(self.config_data[key]));ttk.Label(general,text=label).grid(row=i,column=0,sticky='w',pady=12);ttk.Entry(general,textvariable=fields[key],width=43).grid(row=i,column=1,padx=8)
        def browse():
            path=filedialog.askopenfilename(parent=win,title=tr('Seleziona Python con Tkinter'))
            if path:fields['python'].set(path)
        ttk.Button(general,text=tr('Sfoglia…'),command=browse).grid(row=0,column=2)
        ttk.Label(general,text=tr('Tutti i pacchetti del wizard saranno installati in questo Python.\nPuoi scegliere il Python di un ambiente virtuale.'),wraplength=650).grid(row=3,column=0,columnspan=3,sticky='w',pady=16)
        flags={}
        for key,label,default in [('guided_values',tr('Completa automaticamente le virgolette dei valori testuali'),True),('startup_checks',tr('Controlla librerie, PIP e documentazione all’avvio'),True),('dependency_before_insert',tr('Mostra i requisiti prima di aggiungere un componente esterno'),True),('dependency_before_run',tr('Verifica i pacchetti prima di Avvia / Debug'),True),('pip_auto_install',tr('Prepara automaticamente i pacchetti quando inserisci o avvii un componente'),True),('pip_wheels_only',tr('Escludi sorgenti e usa soltanto wheel (avanzato)'),False)]:
            flags[key]=tk.BooleanVar(value=self.config_data.get(key,default));ttk.Checkbutton(packages,text=label,variable=flags[key]).pack(anchor='w',pady=6)
        ttk.Button(packages,text=tr('Apri wizard PIP…'),command=self.open_dependencies).pack(anchor='w',pady=12)
        ttk.Label(appearance,text=tr('Scegli un preset oppure personalizza i colori dell’IDE.\nI colori delle finestre create si modificano nel designer.'),wraplength=650).pack(anchor='w',pady=15)
        ttk.Button(appearance,text=tr('Temi e colori…'),command=self.appearance_settings).pack(anchor='w')
        ttk.Label(appearance,text=tr('Lingua interfaccia')).pack(anchor='w',pady=(14,3))
        language=tk.StringVar(value=LANGUAGES.get(self.config_data.get('language'),LANGUAGES[get_language()]))
        ttk.Combobox(appearance,textvariable=language,values=list(LANGUAGES.values()),state='readonly').pack(anchor='w')
        ttk.Label(appearance,text=tr('Seleziona la lingua dell’interfaccia. Il cambio viene applicato al riavvio.'),wraplength=650).pack(anchor='w',pady=4)
        ttk.Label(appearance,text=tr('Lingua dei componenti generati')).pack(anchor='w',pady=(12,3))
        project_language=tk.StringVar(value=LANGUAGES.get(self.project.get('language'),LANGUAGES['it']))
        ttk.Combobox(appearance,textvariable=project_language,values=list(LANGUAGES.values()),state='readonly').pack(anchor='w')
        status=tk.StringVar();ttk.Label(win,textvariable=status,padding=8,wraplength=650).grid(row=2,column=0,sticky='ew')
        def save():
            try:
                updated={**self.config_data,**{k:v.get() for k,v in fields.items()},**{k:v.get() for k,v in flags.items()}};updated['grid']=int(updated['grid']);updated['font_size']=int(updated['font_size'])
                if not 1<=updated['grid']<=100 or not 8<=updated['font_size']<=32:raise ValueError(tr('Griglia o carattere fuori intervallo.'))
                if not Path(updated['python']).is_file():raise ValueError(tr('Interprete inesistente.'))
                validate_interpreter(updated['python'])
                updated['language']=next(code for code,name in LANGUAGES.items() if name==language.get())
                selected_project_language=next(code for code,name in LANGUAGES.items() if name==project_language.get())
                if selected_project_language!=self.project.get('language','it'):
                    self.commit_code();self.checkpoint();self.project['language']=selected_project_language;self.update_source()
                language_changed=updated['language']!=get_language()
                if updated['python']!=self.config_data['python']:
                    self.commit_code();self.checkpoint();self.project.pop('environment',None);self.global_python=updated['python']
                self.save_ide_settings(updated);self.config_data=updated;self.code.configure(font=('Menlo',updated['font_size']));self.draw()
                if language_changed:messagebox.showinfo(tr('Lingua aggiornata',language=updated['language']),tr('La lingua è stata salvata. Riavvia VisualTk Studio per applicarla a tutte le finestre.',language=updated['language']),parent=win)
                win.destroy()
            except Exception as exc:status.set(str(exc))
        row=ttk.Frame(win,padding=12);row.grid(row=3,column=0,sticky='ew');ttk.Button(row,text=tr('Salva configurazione'),command=save,style='Accent.TButton').pack(side='right');ttk.Button(row,text=tr('Annulla',context='cancel'),command=win.destroy).pack(side='right',padx=8)
