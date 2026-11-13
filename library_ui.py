"""Library catalog, isolated checks and project theme configuration."""
import copy
from pathlib import Path
import queue
import shutil
import threading
import time
import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from i18n import tr
from library_catalog import LIBRARIES,theme_config
from library_checks import check_library
from components import registry
from project_files import list_files,project_file

class LibraryMixin:
    def library_manager(self):
        win=tk.Toplevel(self);win.title(tr('Librerie e temi'));win.geometry('1000x600');win.transient(self)
        ttk.Label(win,text=tr('Installazione, prova grafica e deploy sono verifiche distinte.'),padding=12).pack(anchor='w')
        body=ttk.Frame(win,padding=10);body.pack(fill='both',expand=True)
        tree=ttk.Treeview(body,columns=('kind','support','check'),show='tree headings');tree.heading('#0',text=tr('Libreria'));tree.heading('kind',text=tr('Tipo'));tree.heading('support',text=tr('Integrazione'));tree.heading('check',text=tr('Ultima verifica'));tree.column('#0',width=180);tree.column('kind',width=90);tree.column('support',width=110);tree.column('check',width=200);tree.pack(fill='both',expand=True)
        detail=tk.StringVar();ttk.Label(win,textvariable=detail,wraplength=950,padding=10).pack(fill='x')
        tasks=queue.Queue();busy=False
        state_labels={'installed':tr('Installata'),'unchecked':tr('Da verificare'),'runtime_ok':tr('Prova grafica superata'),'missing':tr('Da preparare'),'unsupported':tr('Non supportata'),'separate':tr('Motore separato'),'assets':tr('Risorse locali'),'adapter':tr('Adattatore'),'experimental':tr('Sperimentale'),'error':tr('Errore')}
        kind_labels={'standard':'Standard','widgets':tr('Controlli'),'theme':tr('Temi'),'legacy':'Legacy','framework':'Framework'}
        def fill():
            previous=tree.selection();tree.delete(*tree.get_children())
            for name,kind,specs,module,support,note in LIBRARIES:
                record=self.project.get('library_checks',{}).get(name,{})
                state=record.get('state','unchecked') if record.get('python')==self.config_data['python'] and (kind!='theme' or record.get('theme')==theme_config(self.project)) else 'unchecked'
                tree.insert('','end',iid=name,text=name,values=(kind_labels.get(kind,kind),state_labels.get(support,support),(state_labels.get(state,state)+(' • '+time.strftime('%d/%m %H:%M',time.localtime(record['checked_at'])) if state!='unchecked' and record.get('checked_at') else ''))))
            if previous:tree.selection_set(previous)
        def selected():return next((row for row in LIBRARIES if tree.selection() and row[0]==tree.selection()[0]),None)
        def describe(event=None):
            row=selected()
            if not row:return
            controls=[kind for kind,data in registry(self.project).items() if data.get('family')==row[0] or data['module']==row[3]] if row[3] else []
            if row[0] in ('Google Drive','S3 / MinIO','WebDAV'):controls=['CloudStorage']
            if row[0] in ('OpenAI','Claude','Gemini'):controls=['LLMClient']
            detail.set(row[5]+'\nPIP: '+(', '.join(row[2]) or '—')+'\n'+tr('Controlli: ')+', '.join(controls)+'\n'+tr('Deploy della libreria: non verificato automaticamente.'))
            state='disabled' if busy or row[4] in ('unsupported','separate') else 'normal'
            install.configure(state=state if row[2] else 'disabled');probe.configure(state=state);runtime.configure(state=state)
        def install_selected():
            row=selected()
            if row and row[2]:self.open_dependencies(specs=row[2],auto_install=True)
        def check(runtime_test=False):
            nonlocal busy
            row=selected()
            if not row or busy:return
            busy=True;describe();detail.set(tr('Verifica in un processo separato…'))
            python=self.config_data['python'];name=row[0];config=copy.deepcopy(theme_config(self.project));root=str(self.path.parent) if self.path else None;project=self.project
            def worker():
                try:result=check_library(python,name,runtime_test,config,root)
                except Exception as exc:result={'state':'error','detail':str(exc),'python':python}
                tasks.put((name,result,project))
            threading.Thread(target=worker,daemon=True).start()
        def poll():
            nonlocal busy
            if not win.winfo_exists():return
            try:
                name,result,project=tasks.get_nowait();busy=False
                if project is self.project:
                    self.commit_code();self.checkpoint();project.setdefault('library_checks',{})[name]=result;self.update_source();fill();detail.set(result['state']+'\n'+result['detail'])
                describe_state=selected()
                if describe_state:
                    state='disabled' if describe_state[4] in ('unsupported','separate') else 'normal';probe.configure(state=state);runtime.configure(state=state);install.configure(state=state if describe_state[2] else 'disabled')
            except queue.Empty:pass
            win.after(100,poll)
        row=ttk.Frame(win,padding=10);row.pack(fill='x')
        install=ttk.Button(row,text=tr('Prepara con PIP…'),command=install_selected);install.pack(side='left',padx=3)
        probe=ttk.Button(row,text=tr('Verifica installazione'),command=check);probe.pack(side='left',padx=3)
        runtime=ttk.Button(row,text=tr('Prova grafica isolata'),command=lambda:check(True));runtime.pack(side='left',padx=3)
        ttk.Button(row,text=tr('Tema del progetto…'),command=self.configure_project_theme).pack(side='right')
        tree.bind('<<TreeviewSelect>>',describe);fill();tree.selection_set('tkinter');describe();win.after(100,poll)

    def configure_project_theme(self):
        current=theme_config(self.project);win=tk.Toplevel(self);win.title(tr('Tema del progetto'));win.geometry('710x460');win.transient(self)
        body=ttk.Frame(win,padding=15);body.pack(fill='both',expand=True)
        provider=tk.StringVar(value=current['provider']);name=tk.StringVar(value=current.get('name','litera'));mode=tk.StringVar(value=current.get('mode','light'));file=tk.StringVar(value=current.get('file',''));appearance=tk.StringVar(value=self.project.get('appearance_mode','System'))
        selectors=[]
        for i,(label,var,choices) in enumerate([('Motore tema ttk',provider,['none','ttkbootstrap','ttkthemes','sv-ttk','azure','forest']),('Nome tema',name,['litera','darkly','cosmo','minty','arc','plastik','clearlooks']),('Modalità tema',mode,['light','dark']),('Aspetto CustomTkinter',appearance,['System','Light','Dark'])]):
            ttk.Label(body,text=tr(label)).grid(row=i,column=0,sticky='w',pady=9);combo=ttk.Combobox(body,textvariable=var,values=choices,state='readonly' if i!=1 else 'normal',width=35);combo.grid(row=i,column=1,sticky='ew');selectors.append(combo)
        def theme_options(event=None):
            choices={'ttkbootstrap':['litera','darkly','cosmo','minty','flatly','solar'],'ttkthemes':['arc','plastik','clearlooks','breeze','radiance','equilux']}.get(provider.get(),[])
            selectors[1].configure(values=choices,state='normal' if choices else 'disabled')
            if event and choices and name.get() not in choices:name.set(choices[0])
            selectors[2].configure(state='readonly' if provider.get() in ('sv-ttk','azure','forest') else 'disabled')
        selectors[0].bind('<<ComboboxSelected>>',theme_options);theme_options()
        ttk.Label(body,text=tr('File Tcl relativo')).grid(row=4,column=0,sticky='w');ttk.Entry(body,textvariable=file,width=40).grid(row=4,column=1)
        ttk.Label(body,text=tr('Il tema ttk non modifica i controlli Tk classici o CustomTkinter. Anteprima del designer schematica; usa la prova grafica isolata.'),wraplength=650).grid(row=5,column=0,columnspan=3,pady=15)
        def import_folder():
            if provider.get() not in ('azure','forest'):return messagebox.showinfo(tr('Tema del progetto'),tr('Seleziona Azure o Forest prima di importare.'),parent=win)
            root=self.project_root(True)
            if root is None:return
            source=filedialog.askdirectory(parent=win,title=tr('Cartella del tema con Tcl e immagini'))
            if not source:return
            target=None;created=False
            try:
                source=Path(source).resolve();items=list_files(source,limit=None);entry='azure.tcl' if provider.get()=='azure' else 'forest-'+mode.get()+'.tcl'
                if not (source/entry).is_file() or (source/entry).is_symlink():raise ValueError('Missing '+entry)
                files=[relative for relative,is_dir in items if not is_dir]
                if len(files)>2000 or sum((source/relative).stat().st_size for relative in files)>50*1024*1024:raise ValueError('Theme folder limit: 2000 files / 50 MB')
                parent=project_file(root,'themes');parent.mkdir(exist_ok=True);target=parent/provider.get();n=1
                while target.exists():n+=1;target=parent/(provider.get()+'-'+str(n))
                target.mkdir();created=True
                for relative in files:
                    dest=target/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source/relative,dest)
                self.register_project_file(target.relative_to(root).as_posix());file.set((target/entry).relative_to(root).as_posix())
            except Exception as exc:
                if created and target and target.exists():shutil.rmtree(target)
                messagebox.showerror(tr('Tema del progetto'),str(exc),parent=win)
        def save():
            try:
                config={'provider':provider.get(),'name':name.get(),'mode':mode.get()}
                if provider.get() in ('azure','forest'):
                    root=self.project_root(True)
                    if root is None:return
                    relative=file.get()
                    if provider.get()=='forest':relative=(Path(relative).parent/('forest-'+mode.get()+'.tcl')).as_posix()
                    asset=project_file(root,relative)
                    if not asset.is_file():raise ValueError('Missing theme file: '+relative)
                    config['file']=relative
                    if not any(relative==item or relative.startswith(item+'/') for item in self.project.get('files',[])):raise ValueError('Include the theme folder in project files before deployment.')
                probe={**self.project,'theme_config':config};theme_config(probe)
                self.commit_code();self.checkpoint();self.project.pop('theme',None);self.project['theme_config']=config
                if appearance.get()!='System' or any(w['kind'].startswith('CTk') for f in self.project['forms'] for w in f['widgets']):self.project['appearance_mode']=appearance.get()
                else:self.project.pop('appearance_mode',None)
                self.update_source();win.destroy()
            except Exception as exc:messagebox.showerror(tr('Tema del progetto'),str(exc),parent=win)
        ttk.Button(body,text=tr('Importa cartella tema…'),command=import_folder).grid(row=6,column=0,pady=10)
        ttk.Button(body,text=tr('Salva tema'),command=save).grid(row=6,column=1,sticky='e')
