"""PyPI metadata browser and explicit interpreter-scoped dependency management."""
import json
import queue
import re
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from urllib.request import Request, urlopen
from urllib.parse import quote, urlencode
import webbrowser
from components import CATALOG, install_args
from runtime_requirements import validate_interpreter

def package_info(name):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*',name):raise ValueError('Inserisci il nome esatto del pacchetto PyPI')
    request=Request('https://pypi.org/pypi/'+quote(name,safe='')+'/json',headers={'User-Agent':'VisualTkStudio/1.1'})
    with urlopen(request,timeout=15) as response:return json.load(response)['info']

class LibraryExplorer(tk.Toplevel):
    def __init__(self,studio):
        super().__init__(studio);self.studio=studio;self.title('Esplora librerie • PyPI');self.geometry('850x650');self.tasks=queue.Queue();self.busy=False;self.info=None;self.timer=None;self.closed=False
        ttk.Label(self,text='Catalogo consigliato + ricerca per nome esatto su PyPI. La ricerca libera apre PyPI nel browser.',padding=10).pack(fill='x')
        row=ttk.Frame(self,padding=5);row.pack(fill='x');self.query=tk.StringVar();ttk.Entry(row,textvariable=self.query).pack(side='left',fill='x',expand=True)
        for label,cmd in [('Filtra catalogo',self.filter),('Dettagli PyPI',self.fetch),('Ricerca web',self.web_search)]:ttk.Button(row,text=label,command=cmd).pack(side='left')
        self.list=ttk.Treeview(self,columns=('category',),show='tree headings',height=9);self.list.heading('#0',text='Pacchetto');self.list.heading('category',text='Categoria');self.list.pack(fill='x',padx=8);self.list.bind('<<TreeviewSelect>>',self.select);self.list.bind('<Double-Button-1>',lambda e:self.fetch());self.filter()
        self.details=ScrolledText(self,height=15,wrap='word');self.details.pack(fill='both',expand=True,padx=8,pady=5)
        row=ttk.Frame(self,padding=5);row.pack(fill='x')
        for label,cmd in [('Installa versione selezionata',self.install),('Aggiungi dipendenza al progetto',self.add),('Dipendenze del progetto',studio.install_project_dependencies),('Pacchetti installati',self.installed),('Pagina PyPI',self.open_page)]:ttk.Button(row,text=label,command=cmd).pack(side='left',padx=2)
        ttk.Button(self,text='Crea componente visuale da una libreria…',command=studio.component_wizard).pack(anchor='w',padx=10,pady=4)
        self.status=tk.StringVar(value='Interprete: '+studio.config_data['python']);ttk.Label(self,textvariable=self.status,padding=8,wraplength=820).pack(fill='x')
        self.protocol('WM_DELETE_WINDOW',self.close);self.timer=self.after(100,self.poll)
    def filter(self):
        self.list.delete(*self.list.get_children());query=self.query.get().lower()
        for name,category in CATALOG:
            if not query or query in (name+' '+category).lower():self.list.insert('','end',iid=name,text=name,values=(category,))
    def select(self,event=None):
        selected=self.list.selection()
        if selected:self.query.set(selected[0])
    def async_task(self,callback):
        if self.busy:return
        self.busy=True;self.status.set('Operazione in corso…')
        def worker():
            try:self.tasks.put(('ok',callback()))
            except Exception as exc:self.tasks.put(('error',str(exc)))
        threading.Thread(target=worker,daemon=True).start()
    def fetch(self):
        name=self.query.get().strip();self.async_task(lambda:('metadata',package_info(name)))
    def poll(self):
        if self.closed:return
        try:
            while True:
                state,result=self.tasks.get_nowait();self.busy=False
                if state=='error':self.status.set('Errore: '+result);continue
                kind,data=result;self.details.delete('1.0','end')
                if kind=='metadata':
                    self.info=data
                    self.details.insert('end',f"{data['name']} {data['version']}\n\n{data.get('summary','')}\n\nPython: {data.get('requires_python','')}\nLicenza: {data.get('license_expression') or data.get('license') or 'Consultare il progetto'}\n\nRepository/documentazione:\n"+json.dumps(data.get('project_urls'),indent=2,ensure_ascii=False)+'\n\n'+(data.get('description') or '')[:20000]);self.status.set('Metadati ricevuti da pypi.org. Nessun pacchetto eseguito.')
                else:self.details.insert('end',data);self.status.set('Operazione terminata')
        except queue.Empty:pass
        self.timer=self.after(100,self.poll)
    def selected_spec(self):
        if not self.info:raise ValueError('Prima consulta Dettagli PyPI per selezionare una versione')
        return self.info['name']+'=='+self.info['version']
    def add(self):
        try:spec=self.selected_spec();install_args(self.studio.config_data['python'],[spec])
        except ValueError as exc:return messagebox.showerror('Dipendenza',str(exc),parent=self)
        self.studio.commit_code();self.studio.checkpoint();specs=self.studio.project.setdefault('requirements',[])
        # Keep one explicitly selected version per distribution.
        name=re.split(r'[<>=!~\[]',spec)[0].lower().replace('_','-')
        specs[:]=[s for s in specs if re.split(r'[<>=!~\[]',s)[0].lower().replace('_','-')!=name];specs.append(spec);self.studio.update_source();self.status.set('Aggiunta al progetto: '+spec)
    def install(self):
        try:spec=self.selected_spec();install_args(self.studio.config_data['python'],[spec])
        except ValueError as exc:return messagebox.showerror('Installazione',str(exc),parent=self)
        self.studio.open_dependencies(specs=[spec],auto_install=True)
    def installed(self):
        python=self.studio.config_data['python']
        def fetch():
            result=subprocess.run([python,'-m','pip','list','--format=json'],capture_output=True,text=True,timeout=30)
            if result.returncode:raise RuntimeError(result.stderr)
            return ('text','\n'.join(f"{p['name']} == {p['version']}" for p in json.loads(result.stdout)))
        self.async_task(fetch)
    def web_search(self):webbrowser.open('https://pypi.org/search/?'+urlencode({'q':self.query.get()}))
    def open_page(self):
        if self.info:webbrowser.open('https://pypi.org/project/'+quote(self.info['name'],safe='')+'/')
    def close(self):
        if self.busy:
            if not messagebox.askyesno('Operazione in corso','L’operazione continuerà in background. Chiudere la finestra?',parent=self):return
        self.closed=True
        if self.timer:self.after_cancel(self.timer)
        self.destroy()
