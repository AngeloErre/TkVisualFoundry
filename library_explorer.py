"""In-app package catalog with cached PyPI names and interpreter-scoped installation."""
from i18n import tr
import json
import queue
import re
import subprocess
import threading
import tkinter as tk
from tkinter import ttk,messagebox
from tkinter.scrolledtext import ScrolledText
from urllib.request import Request,urlopen
from urllib.parse import quote
from components import CATALOG,BUILTINS,install_args
from productivity_specs import PROVIDER_REQUIREMENTS
from packaging.requirements import Requirement
from runtime_requirements import validate_interpreter
from startup_checks import https_context,stable_versions
from packaging.specifiers import SpecifierSet
from packaging.utils import canonicalize_name
from package_catalog import project_names,search_names

def recommended_packages():
    values=dict(CATALOG)
    for kind,spec in BUILTINS.items():
        for requirement in spec.get('requirements',[]):values.setdefault(Requirement(requirement).name,kind)
    for provider,specs in PROVIDER_REQUIREMENTS.items():
        for requirement in specs:values.setdefault(Requirement(requirement).name,provider)
    return sorted(values.items(),key=lambda item:item[0].casefold())

RECOMMENDED=recommended_packages()

def package_info(name,python_version=None):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*',name):raise ValueError(tr('Inserisci il nome esatto del pacchetto PyPI'))
    request=Request('https://pypi.org/pypi/'+quote(name,safe='')+'/json',headers={'User-Agent':'VisualTkStudio/1.17'})
    with urlopen(request,timeout=15,context=https_context()) as response:data=json.load(response)
    info=dict(data['info'])
    if python_version:
        chosen=stable_versions(data,SpecifierSet(),python_version)
        if chosen and chosen!=info.get('version'):
            request=Request('https://pypi.org/pypi/'+quote(name,safe='')+'/'+quote(chosen,safe='')+'/json',headers={'User-Agent':'VisualTkStudio/1.17'})
            with urlopen(request,timeout=15,context=https_context()) as response:info=dict(json.load(response)['info'])
        info['version']=chosen
    return info

class LibraryExplorer(tk.Toplevel):
    def __init__(self,studio):
        super().__init__(studio);self.studio=studio;self.title(tr('Esplora librerie • PyPI'));self.geometry('940x700');self.minsize(760,560)
        self.tasks=queue.Queue();self.info=None;self.timer=None;self.closed=False;self.serial=0;self.detail_serial=0;self.offset=0;self.total=0;self.index=None;self.cancelled=threading.Event()
        self.index_lock=threading.Lock();self.selection_timer=None
        self.python=studio.config_data['python'];self.metadata_python=None
        ttk.Label(self,text=tr('Cerca e installa pacchetti senza uscire dall’app. Tutto PyPI cerca nei nomi; seleziona un risultato per i dettagli.'),padding=8,wraplength=900).pack(fill='x')
        row=ttk.Frame(self,padding=5);row.pack(fill='x')
        self.source=tk.StringVar(value=tr('Consigliati'));box=ttk.Combobox(row,textvariable=self.source,values=[tr('Consigliati'),tr('Tutto PyPI'),tr('Installati')],state='readonly',width=15);box.pack(side='left');box.bind('<<ComboboxSelected>>',lambda e:self.search())
        self.query=tk.StringVar();entry=ttk.Entry(row,textvariable=self.query);entry.pack(side='left',fill='x',expand=True,padx=5);entry.bind('<Return>',lambda e:self.search())
        ttk.Button(row,text=tr('Cerca'),command=self.search).pack(side='left');ttk.Button(row,text=tr('Nome esatto…'),command=self.fetch).pack(side='left',padx=2);ttk.Button(row,text=tr('Aggiorna indice'),command=lambda:self.search(refresh=True)).pack(side='left',padx=3)
        self.pages=ttk.Frame(self,padding=(8,2));self.pages.pack(fill='x')
        self.previous=ttk.Button(self.pages,text=tr('Precedenti'),command=lambda:self.search(offset=max(0,self.offset-100)));self.previous.pack(side='left')
        self.next=ttk.Button(self.pages,text=tr('Successivi'),command=lambda:self.search(offset=self.offset+100));self.next.pack(side='left',padx=3)
        self.count=tk.StringVar();ttk.Label(self.pages,textvariable=self.count).pack(side='left',padx=8)
        self.progress=ttk.Progressbar(self.pages,mode='indeterminate',length=90);self.progress.pack(side='right')
        pane=ttk.Panedwindow(self,orient='vertical');pane.pack(fill='both',expand=True,padx=8,pady=4)
        list_area=ttk.Frame(pane);pane.add(list_area,weight=1)
        self.list=ttk.Treeview(list_area,columns=('category','version'),show='tree headings',height=10)
        for key,label,width in [('#0',tr('Pacchetto'),270),('category',tr('Categoria'),300),('version',tr('Versione installata'),140)]:self.list.heading(key,text=label);self.list.column(key,width=width,minwidth=70)
        scroll=ttk.Scrollbar(list_area,command=self.list.yview);self.list.configure(yscrollcommand=scroll.set);scroll.pack(side='right',fill='y');self.list.pack(fill='both',expand=True)
        self.list.bind('<<TreeviewSelect>>',self.select)
        self.details=ScrolledText(pane,height=12,wrap='word');pane.add(self.details,weight=1)
        actions=ttk.Frame(self,padding=5);actions.pack(fill='x')
        self.install_button=ttk.Button(actions,text=tr('Installa versione selezionata'),command=self.install,state='disabled');self.install_button.pack(side='left',padx=2)
        self.add_button=ttk.Button(actions,text=tr('Aggiungi dipendenza al progetto'),command=self.add,state='disabled');self.add_button.pack(side='left',padx=2)
        ttk.Button(actions,text=tr('Dipendenze del progetto'),command=studio.install_project_dependencies).pack(side='left',padx=2)
        ttk.Button(self,text=tr('Crea componente visuale da una libreria…'),command=studio.component_wizard).pack(anchor='w',padx=10,pady=2)
        self.status=tk.StringVar(value=tr('Interprete: ')+self.python);ttk.Label(self,textvariable=self.status,padding=6,wraplength=900).pack(fill='x')
        self.protocol('WM_DELETE_WINDOW',self.close);self.bind('<Destroy>',self.on_destroy,add='+');self.timer=self.after(100,self.poll);self.search()

    def work(self,kind,token,callback):
        def worker():
            try:self.tasks.put((kind,token,callback(),None))
            except Exception as exc:self.tasks.put((kind,token,None,str(exc)))
        threading.Thread(target=worker,daemon=True).start()

    def clear_details(self):
        if self.selection_timer:self.after_cancel(self.selection_timer);self.selection_timer=None
        self.detail_serial+=1;self.info=None;self.metadata_python=None
        self.install_button.configure(state='disabled');self.add_button.configure(state='disabled')
        self.details.configure(state='normal');self.details.delete('1.0','end');self.details.configure(state='disabled')

    def search(self,refresh=False,offset=0):
        self.serial+=1;token=self.serial;self.offset=offset;self.clear_details()
        source=self.source.get();query=self.query.get().strip();python=self.studio.config_data['python'];self.python=python
        self.progress.start(12);self.status.set(tr('Caricamento catalogo… Il primo accesso a Tutto PyPI scarica l’indice dei nomi.'))
        def run():
            versions={};note=''
            if source==tr('Consigliati'):names=[name for name,_ in RECOMMENDED]
            elif source==tr('Installati'):
                result=subprocess.run([python,'-m','pip','list','--format=json'],capture_output=True,text=True,timeout=30)
                if result.returncode:raise RuntimeError(result.stderr[-1000:])
                versions={p['name']:p['version'] for p in json.loads(result.stdout)};names=sorted(versions,key=str.casefold)
            else:
                with self.index_lock:
                    if self.index is None or refresh:
                        result=project_names(refresh=refresh,cancelled=self.cancelled);self.index=result['names']
                        note=tr('Indice locale') if result['cached'] else tr('Indice aggiornato da PyPI')
                        if result['age']>86400:note+=' • '+tr('Cache oltre 24 ore: usa Aggiorna indice per aggiornarla.')
                    names=self.index
            page=search_names(names,query,offset);page.update(versions=versions,note=note,source=source,python=python);return page
        self.work('search',token,run)

    def select(self,event=None):
        selected=self.list.selection()
        if not selected:return
        self.request_metadata(selected[0])

    def fetch(self):
        self.request_metadata(self.query.get().strip())

    def request_metadata(self,name):
        self.clear_details();token=self.detail_serial;python=self.studio.config_data['python']
        self.status.set(tr('Lettura dettagli: ')+name)
        def fetch():
            version=validate_interpreter(python);info=package_info(name,'.'.join(map(str,version[:3])));return info,python
        self.selection_timer=self.after(220,lambda:self.work('metadata',token,fetch))

    def poll(self):
        if self.closed:return
        try:
            while True:
                kind,token,data,error=self.tasks.get_nowait()
                if token!=(self.serial if kind=='search' else self.detail_serial):continue
                if kind=='search':self.progress.stop()
                if error:self.status.set(tr('Errore: ')+error);continue
                if kind=='search':
                    if data['python']!=self.studio.config_data['python']:self.search();continue
                    self.clear_details();self.list.delete(*self.list.get_children());categories=dict(RECOMMENDED);self.total=data['total']
                    for name in data['names']:self.list.insert('','end',iid=name,text=name,values=(categories.get(name,''),data['versions'].get(name,'')))
                    start=self.offset+1 if self.total else 0;self.count.set(f'{start}–{min(self.offset+100,self.total)} / {self.total}')
                    self.previous.configure(state='normal' if self.offset else 'disabled');self.next.configure(state='normal' if self.offset+100<self.total else 'disabled')
                    self.status.set(data['note'] or tr('Interprete: ')+self.python)
                else:
                    info,python=data
                    if python!=self.studio.config_data['python']:continue
                    self.info=info;self.metadata_python=python
                    version=info.get('version') or tr('Nessuna versione stabile compatibile')
                    text=f"{info['name']} — {version}\n\n{info.get('summary','')}\n\nPython: {info.get('requires_python','')}\n{tr('Licenza')}: {info.get('license_expression') or info.get('license') or tr('Consultare il progetto')}\n\n"+json.dumps(info.get('project_urls'),indent=2,ensure_ascii=False)+'\n\n'+(info.get('description') or '')[:20000]
                    self.details.configure(state='normal');self.details.delete('1.0','end');self.details.insert('1.0',text);self.details.configure(state='disabled')
                    state='normal' if info.get('version') else 'disabled';self.install_button.configure(state=state);self.add_button.configure(state=state)
                    self.status.set(tr('Metadati ricevuti da pypi.org. Nessun pacchetto eseguito.'))
        except queue.Empty:pass
        self.timer=self.after(100,self.poll)

    def selected_spec(self):
        if not self.info or not self.info.get('version'):raise ValueError(tr('Seleziona un pacchetto e attendi i dettagli.'))
        if self.metadata_python!=self.studio.config_data['python']:raise ValueError(tr('Interprete cambiato: seleziona nuovamente il pacchetto.'))
        return self.info['name']+'=='+self.info['version']
    def add(self):
        try:spec=self.selected_spec();install_args(self.studio.config_data['python'],[spec])
        except ValueError as exc:return messagebox.showerror(tr('Dipendenza'),str(exc),parent=self)
        self.studio.commit_code();self.studio.checkpoint();specs=self.studio.project.setdefault('requirements',[])
        name=canonicalize_name(self.info['name']);specs[:]=[s for s in specs if canonicalize_name(re.split(r'[<>=!~\[]',s)[0].strip())!=name];specs.append(spec)
        self.studio.update_source();self.status.set(tr('Aggiunta al progetto: ')+spec)
    def install(self):
        try:spec=self.selected_spec();install_args(self.studio.config_data['python'],[spec])
        except ValueError as exc:return messagebox.showerror(tr('Installazione'),str(exc),parent=self)
        self.studio.open_dependencies(specs=[spec],auto_install=True)
    def shutdown(self):
        if self.closed:return
        self.closed=True;self.cancelled.set();self.serial+=1;self.detail_serial+=1
        for timer in (self.timer,self.selection_timer):
            if timer:
                try:self.after_cancel(timer)
                except tk.TclError:pass
    def on_destroy(self,event):
        if event.widget is self:self.shutdown()
    def close(self):
        self.shutdown();self.destroy()
