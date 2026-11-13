"""Background project environment onboarding and persistent global settings."""
import json
from pathlib import Path
import queue
import threading
import tkinter as tk
from tkinter import ttk
from project_environment import environment_python,create_environment
from project_files import atomic_write_text
from components import requirements
from i18n import tr

class EnvironmentMixin:
    def save_ide_settings(self,data):
        # Runtime project Python must never become the default for unrelated projects.
        persisted={**data,'python':self.global_python}
        atomic_write_text(Path.home()/'.visualtkstudio.json',json.dumps(persisted,indent=2))

    def activate_project_environment(self):
        python=str(environment_python(self.path.parent)) if self.path and self.project.get('environment',{}).get('managed') else self.global_python
        previous=self.config_data['python'];self.config_data['python']=python
        if previous!=python and hasattr(self,'analysis_client'):self.restart_intellisense()

    def project_environment(self):
        if self.path is None and not self.save():return
        previous=getattr(self,'environment_window',None)
        if previous and previous.winfo_exists():previous.lift();return
        win=tk.Toplevel(self);self.environment_window=win;win.title(tr('Ambiente Python del progetto'));win.geometry('680x330');win.transient(self)
        root=self.path.parent;project=self.project
        ttk.Label(win,text=tr('Ogni progetto può usare una propria .venv: i pacchetti restano separati dagli altri progetti.'),wraplength=640,padding=12).pack(fill='x')
        state=tk.StringVar(value=tr('Interprete: ')+self.config_data['python']);ttk.Label(win,textvariable=state,wraplength=640,padding=12).pack(fill='x')
        events=queue.Queue();busy=[False];timer=[None]
        progress=ttk.Progressbar(win,mode='indeterminate');progress.pack(fill='x',padx=12,pady=5)
        def same_project():return self.project is project and self.path is not None and self.path.parent==root
        def done():
            if busy[0]:return
            if timer[0]:win.after_cancel(timer[0])
            win.destroy()
        win.protocol('WM_DELETE_WINDOW',done)
        def create():
            if busy[0]:return
            if not same_project():state.set(tr('Progetto cambiato: riapri la gestione ambiente.'));return
            busy[0]=True;self.environment_busy=True;button.configure(state='disabled');global_button.configure(state='disabled');progress.start(12);state.set(tr('Creazione ambiente in corso…'))
            base=self.global_python
            def worker():
                try:events.put((create_environment(base,root),None))
                except Exception as exc:events.put((None,str(exc)))
            threading.Thread(target=worker,daemon=True).start()
        def use_global():
            if busy[0]:return
            if not same_project():done();return
            self.commit_code();self.checkpoint();self.project.pop('environment',None);self.activate_project_environment()
            if self.save():done()
        button=ttk.Button(win,text=tr('Crea / usa .venv e prepara pacchetti'),command=create);button.pack(anchor='w',padx=12,pady=6)
        global_button=ttk.Button(win,text=tr('Usa interprete globale'),command=use_global);global_button.pack(anchor='w',padx=12,pady=6)
        def poll():
            if not win.winfo_exists():return
            try:
                python,error=events.get_nowait();busy[0]=False;self.environment_busy=False;progress.stop();button.configure(state='normal');global_button.configure(state='normal')
                if error:state.set(error)
                elif not same_project():state.set(tr('Progetto cambiato: riapri la gestione ambiente.'))
                else:
                    self.commit_code();self.checkpoint();self.project['environment']={'managed':True};self.config_data['python']=python;self.restart_intellisense()
                    if self.save():
                        done();self.open_dependencies(specs=sorted(set(requirements(self.project)+['jedi>=0.19,<0.21'])),auto_install=True);return
            except queue.Empty:pass
            timer[0]=win.after(100,poll)
        timer[0]=win.after(100,poll)
