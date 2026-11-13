"""Inspector documentation and non-blocking environment health center."""
import copy
import sys
import queue
import subprocess
import threading
import webbrowser
from pathlib import Path
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from component_docs import reference, documentation_urls
from components import requirements
from startup_checks import audit
from i18n import tr

class IntelligenceMixin:
    def build_documentation(self,parent):
        notebook=ttk.Notebook(parent);notebook.pack(fill='both',expand=True,pady=8)
        props=ttk.Frame(notebook);docs=ttk.Frame(notebook)
        notebook.add(props,text=tr('Proprietà'));notebook.add(docs,text=tr('Documentazione'))
        bar=ttk.Frame(docs);bar.pack(fill='x')
        self.docs_link=ttk.Button(bar,text=tr('Sito ufficiale'),command=self.open_component_docs);self.docs_link.pack(fill='x')
        ttk.Button(bar,text=tr('API installata (pydoc)'),command=self.load_installed_docs).pack(fill='x')
        self.docs_text=ScrolledText(docs,width=28,wrap='word',font=('Menlo',11));self.docs_text.pack(fill='both',expand=True)
        self.intelligence_results=queue.Queue();self.audit_running=False;self.audit_report=None;self.docs_generation=0
        self.intelligence_alive=True;self.health_cancel=threading.Event()
        self.intelligence_timer=self.after(100,self.poll_intelligence)
        self.bind('<Destroy>',self.intelligence_destroy,add='+')
        self.health_button=ttk.Button(parent,text=tr('Controlli librerie e documentazione…'),command=self.show_health);self.health_button.pack(fill='x')
        return props

    def update_documentation(self,obj):
        self.docs_generation+=1;self.docs_reference=reference(obj,self.project)
        self.docs_link.configure(state='normal' if self.docs_reference['url'] else 'disabled')
        self.set_docs(self.docs_reference['text'])

    def set_docs(self,text):
        self.docs_text.configure(state='normal');self.docs_text.delete('1.0','end');self.docs_text.insert('1.0',text);self.docs_text.configure(state='disabled')

    def open_component_docs(self):
        if self.docs_reference['url']:webbrowser.open(self.docs_reference['url'])

    def load_installed_docs(self):
        ref=dict(self.docs_reference);generation=(self.docs_generation,self.config_data['python']);python=self.config_data['python']
        source_root=Path(__file__).resolve().parent
        project_root=self.path.resolve().parent if self.path else source_root
        self.set_docs(ref['text']+'\n\n'+tr('Caricamento API…'))
        def work():
            try:
                # No event source is executed. pydoc imports only the selected component's module.
                code='import importlib,pydoc,sys; sys.path[:0]=sys.argv[3:]; obj=getattr(importlib.import_module(sys.argv[1]),sys.argv[2]); print(pydoc.render_doc(obj,renderer=pydoc.plaintext))'
                proc=subprocess.run([python,'-c',code,ref['module'],ref['class'],str(project_root),str(source_root)],cwd=str(source_root),capture_output=True,text=True,timeout=12)
                text=proc.stdout[:100000] if proc.returncode==0 else proc.stderr[-2000:]
            except Exception as exc:text=str(exc)
            self.intelligence_results.put(('docs',generation,ref['text']+'\n\n'+text))
        threading.Thread(target=work,daemon=True).start()

    def health_signature(self):
        return self.config_data['python'],tuple(requirements(self.project)),tuple(documentation_urls(self.project))

    def intelligence_destroy(self,event):
        if event.widget is not self:return
        self.intelligence_alive=False;self.health_cancel.set()
        if getattr(self,'intelligence_timer',None):
            try:self.after_cancel(self.intelligence_timer)
            except Exception:pass

    def start_health(self):
        if self.audit_running:return
        python=self.config_data['python'];project=copy.deepcopy(self.project)
        self.health_context=self.health_signature()
        self.audit_running=True;self.health_cancel.clear()
        specs=requirements(project)+['pip','jedi>=0.19,<0.21']
        if Path(python).absolute()==Path(sys.executable).absolute():specs+=['pyinstaller>=6.22.3,<7','packaging>=24,<27','certifi','Pillow>=10']
        urls=documentation_urls(project)
        self.health_text_value=tr('Controllo in background… Puoi continuare a lavorare.')
        self.health_button.configure(text=tr('Controllo in corso…'))
        self.render_health()
        def work():
            try:report=audit(python,specs,urls,self.health_cancel)
            except Exception as exc:report={'error':str(exc),'python':python}
            self.intelligence_results.put(('health',None,report))
        threading.Thread(target=work,daemon=True).start()

    def poll_intelligence(self):
        if not self.intelligence_alive:return
        try:
            while True:
                kind,generation,result=self.intelligence_results.get_nowait()
                if kind=='docs':
                    if generation==(self.docs_generation,self.config_data['python']):self.set_docs(result)
                else:
                    self.audit_running=False;self.audit_report=result
                    self.health_button.configure(text=tr('Risultati controlli iniziali…'))
                    if 'error' in result:self.health_text_value=tr('Controllo non completato: ')+result['error']
                    else:
                        lines=[result['python']+' • Python '+result['version'],tr('Controllo versioni stabili (compatibilità Python e vincoli dichiarati).'),tr('PIP verificherà anche dipendenze e disponibilità di wheel prima di installare.'),'']
                        lines += [f"{r['name']}: {r['installed'] or '—'} → {r['latest'] or '?'} [{r['status']}]"+((' '+r['error']) if r.get('error') else '') for r in result['packages']]
                        lines += ['', 'pip check: '+result.get('consistency',''),'',tr('Documentazione:')]+[f"[{r['status']}] {r['url']}"+((' → '+r['resolved']) if r.get('resolved')!=r['url'] and r.get('resolved') else '') for r in result['links']]
                        self.health_text_value='\n'.join(lines)
                    self.render_health()
        except queue.Empty:pass
        self.intelligence_timer=self.after(100,self.poll_intelligence)

    def show_health(self):
        import tkinter as tk
        if getattr(self,'health_window',None) and self.health_window.winfo_exists():
            self.health_window.lift()
            if not self.audit_running and self.health_context!=self.health_signature():self.start_health()
            return
        win=tk.Toplevel(self);self.health_window=win;win.title(tr('Controlli iniziali'));win.geometry('820x580')
        bar=ttk.Frame(win,padding=8);bar.pack(fill='x')
        ttk.Button(bar,text=tr('Ricontrolla'),command=self.start_health).pack(side='left')
        ttk.Button(bar,text=tr('Aggiorna con wizard PIP…'),command=self.update_health_packages).pack(side='left',padx=8)
        self.health_text=ScrolledText(win,wrap='word');self.health_text.pack(fill='both',expand=True)
        self.render_health()
        if not self.audit_running and (not self.audit_report or self.health_context!=self.health_signature()):self.start_health()

    def render_health(self):
        if getattr(self,'health_window',None) and self.health_window.winfo_exists():
            self.health_text.configure(state='normal');self.health_text.delete('1.0','end');self.health_text.insert('1.0',getattr(self,'health_text_value',tr('Nessun controllo eseguito.')));self.health_text.configure(state='disabled')

    def update_health_packages(self):
        if self.audit_running:return
        if not self.audit_report or 'error' in self.audit_report:self.start_health();return
        if self.health_context!=self.health_signature():
            self.start_health();return
        # Only declared requirements: third-party transitive upgrades need their own resolver context.
        rows=[r for r in self.audit_report['packages'] if r['required'] and r['latest'] and r['status'] in ('missing','update','incompatible')]
        specs=[r['name']+'=='+r['latest'] for r in rows]
        # Keep extras and constraints, e.g. psycopg[binary], pypdf[crypto].
        if specs:self.open_dependencies(specs=specs+self.audit_report['specs'],auto_install=False,on_ready=self.start_health)
