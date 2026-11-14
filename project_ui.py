"""Project explorer and deployment wizard UI."""
from pathlib import Path
import shutil
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText
from i18n import tr
from project_files import project_file,list_files,rename_file,trash_file,atomic_write_text
from deployment import export_deployment
from deploy_icons import import_icon

class ProjectFilesMixin:
    def build_file_explorer(self,parent):
        actions=ttk.Frame(parent);actions.pack(fill='x')
        menu=tk.Menu(actions,tearoff=False)
        for label,command in [('Nuovo file…',self.new_project_file),('Nuova cartella…',lambda:self.new_project_file(True)),('Importa file…',self.import_project_file),('Rinomina…',self.rename_project_file),('Sposta nel cestino',self.trash_project_file),('Includi / escludi dal deploy',self.toggle_project_file),('Aggiorna',self.refresh_project_files)]:menu.add_command(label=tr(label),command=command)
        ttk.Menubutton(actions,text=tr('File e cartelle ▾'),menu=menu).pack(side='left')
        ttk.Button(actions,text='Deploy…',command=self.deploy_project).pack(side='right')
        tree_area=ttk.Frame(parent);tree_area.pack(fill='both',expand=True)
        scroll=ttk.Scrollbar(tree_area);scroll.pack(side='right',fill='y')
        self.file_tree=ttk.Treeview(tree_area,show='tree',selectmode='browse',yscrollcommand=scroll.set);self.file_tree.pack(fill='both',expand=True);scroll.configure(command=self.file_tree.yview)
        self.file_tree.bind('<Double-1>',self.open_project_file);self.file_tree.bind('<Return>',self.open_project_file)
        self.file_note=tk.StringVar();ttk.Label(parent,textvariable=self.file_note,wraplength=240).pack(fill='x')

    def project_root(self,save=False):
        if self.path is None:
            if not save or not self.save():return None
        return self.path.resolve().parent

    def refresh_project_files(self):
        if not hasattr(self,'file_tree'):return
        tree=self.file_tree;opened={key for key in getattr(self,'file_nodes',{}) if tree.exists(key) and tree.item(key,'open')}
        tree.delete(*tree.get_children());self.file_nodes={};root=self.project_root()
        if root is None:self.file_note.set(tr('Salva il progetto per gestire file e cartelle.'));return
        try:
            items=list_files(root);members=self.project.get('files',[])
            for relative,is_dir in items:
                parent=Path(relative).parent.as_posix();parent='' if parent=='.' else 'file:'+parent
                key='file:'+relative;included=any(relative==m or relative.startswith(m+'/') for m in members)
                tree.insert(parent,'end',iid=key,text=('✓ ' if included else '')+('📁 ' if is_dir else '📄 ')+Path(relative).name,open=key in opened)
                self.file_nodes[key]=relative
            self.file_note.set(tr('✓ = incluso nel deploy. File sul disco; cestino in .visualtk-trash. Limite vista: 1500 elementi.'))
        except Exception as exc:self.file_note.set(str(exc))

    def selected_project_file(self):
        selection=self.file_tree.selection();return self.file_nodes.get(selection[0]) if selection else None

    def file_parent(self):
        relative=self.selected_project_file();root=self.project_root(True)
        if root is None:return None,None
        folder=project_file(root,relative) if relative else root
        return root,folder if folder.is_dir() else folder.parent

    def register_project_file(self,relative):
        self.commit_code();self.checkpoint();members=self.project.setdefault('files',[])
        if relative not in members:members.append(relative)
        self.refresh_project_files();self.update_source()

    def new_project_file(self,folder=False):
        root,parent=self.file_parent()
        if root is None:return
        name=simpledialog.askstring(tr('Nuova cartella…') if folder else tr('Nuovo file…'),tr('Nome relativo alla cartella selezionata:'),parent=self)
        if not name:return
        try:
            path=project_file(root,(parent.relative_to(root)/name).as_posix())
            if path.exists():raise FileExistsError(path)
            if folder:path.mkdir()
            else:
                with path.open('x',encoding='utf-8') as stream:stream.write('')
            self.register_project_file(path.relative_to(root).as_posix())
        except Exception as exc:messagebox.showerror(tr('File di progetto'),str(exc),parent=self)

    def import_project_file(self):
        root,parent=self.file_parent()
        if root is None:return
        source=filedialog.askopenfilename(parent=self)
        if not source:return
        try:
            target=project_file(root,(parent.relative_to(root)/Path(source).name).as_posix())
            if target.exists():raise FileExistsError(target)
            # Exclusive destination creation avoids overwriting a file selected by mistake.
            with open(source,'rb') as src,target.open('xb') as dst:shutil.copyfileobj(src,dst)
            self.register_project_file(target.relative_to(root).as_posix())
        except Exception as exc:messagebox.showerror(tr('File di progetto'),str(exc),parent=self)

    def file_has_editor(self,root,relative):
        path=project_file(root,relative)
        return any(win.winfo_exists() and (opened==path or opened.is_relative_to(path)) for opened,win in getattr(self,'project_editors',{}).items())

    def rename_project_file(self):
        relative=self.selected_project_file();root=self.project_root()
        if not relative or root is None:return
        if self.file_has_editor(root,relative):return messagebox.showinfo(tr('File di progetto'),tr('Chiudi gli editor di questi file prima di rinominare o spostare.'),parent=self)
        if project_file(root,relative)==self.path.resolve():return messagebox.showinfo(tr('File di progetto'),tr('Usa Salva con nome per il file del progetto.'),parent=self)
        name=simpledialog.askstring(tr('Rinomina…'),tr('Nuovo nome. I riferimenti nel codice non vengono modificati:'),initialvalue=Path(relative).name,parent=self)
        if not name:return
        try:
            self.commit_code();self.checkpoint();rename_file(self.project,root,relative,(Path(relative).parent/name).as_posix());self.refresh_project_files();self.update_source()
        except Exception as exc:messagebox.showerror(tr('File di progetto'),str(exc),parent=self)

    def trash_project_file(self):
        relative=self.selected_project_file();root=self.project_root()
        if not relative or root is None:return
        if self.file_has_editor(root,relative):return messagebox.showinfo(tr('File di progetto'),tr('Chiudi gli editor di questi file prima di rinominare o spostare.'),parent=self)
        if project_file(root,relative)==self.path.resolve():return messagebox.showinfo(tr('File di progetto'),tr('Usa Salva con nome per il file del progetto.'),parent=self)
        if not messagebox.askyesno(tr('Sposta nel cestino'),relative+'\n'+tr('Puoi recuperarlo dalla cartella .visualtk-trash. I riferimenti nel codice non vengono modificati.'),parent=self):return
        try:
            self.commit_code();self.checkpoint();trash_file(self.project,root,relative);self.refresh_project_files();self.update_source()
        except Exception as exc:messagebox.showerror(tr('File di progetto'),str(exc),parent=self)

    def toggle_project_file(self):
        relative=self.selected_project_file()
        if not relative:return
        self.commit_code();self.checkpoint();members=self.project.setdefault('files',[])
        if relative in members:members.remove(relative)
        elif any(relative.startswith(m+'/') for m in members):return messagebox.showinfo('Deploy',tr('Escludi prima la cartella contenitore.'),parent=self)
        else:members.append(relative)
        self.refresh_project_files();self.update_source()

    def open_project_file(self,event=None,relative=None):
        relative=relative if relative is not None else self.selected_project_file();root=self.project_root()
        if not relative or root is None:return
        try:
            path=project_file(root,relative)
            editors=getattr(self,'project_editors',{});self.project_editors=editors
            if path in editors and editors[path].winfo_exists():editors[path].lift();return editors[path].project_text
            if path.is_dir():return
            if path==self.path.resolve():return messagebox.showinfo(tr('File di progetto'),tr('Il progetto si modifica nel designer.'),parent=self)
            if path.stat().st_size>2*1024*1024:raise ValueError(tr('Editor limitato a file UTF-8 fino a 2 MB.'))
            original=path.read_text(encoding='utf-8')
            if '\x00' in original:raise ValueError(tr('Editor limitato a file UTF-8 fino a 2 MB.'))
        except Exception as exc:return messagebox.showerror(tr('File di progetto'),str(exc),parent=self)
        editors=getattr(self,'project_editors',{});self.project_editors=editors
        win=tk.Toplevel(self);editors[path]=win;win.title(relative);win.geometry('850x600')
        text=ScrolledText(win,undo=True,font=('Menlo',12),wrap='none');text.pack(fill='both',expand=True);text.insert('1.0',original);text.edit_reset();text.edit_modified(False);win.project_text=text
        stamp=path.stat().st_mtime_ns
        def save(event=None):
            nonlocal stamp
            try:
                if not path.exists() or path.stat().st_mtime_ns!=stamp:raise ValueError(tr('File modificato o spostato sul disco: riaprilo prima di salvare.'))
                project_file(root,path.relative_to(root).as_posix())
                atomic_write_text(path,text.get('1.0','end-1c'));stamp=path.stat().st_mtime_ns;text.edit_modified(False);self.refresh_project_files();return True
            except Exception as exc:messagebox.showerror(tr('File di progetto'),str(exc),parent=win);return False
        def close():
            if text.edit_modified():
                answer=messagebox.askyesnocancel(tr('Salva'),relative,parent=win)
                if answer is None or (answer and not save()):return
            editors.pop(path,None);win.destroy()
        ttk.Button(win,text=tr('Salva'),command=save).pack(anchor='e',padx=8,pady=8)
        def save_shortcut(event):
            save();return 'break'
        win.bind('<Command-s>',save_shortcut);win.bind('<Control-s>',save_shortcut);win.bind('<Command-Shift-F>',self.open_global_search);win.bind('<Control-Shift-F>',self.open_global_search);win.protocol('WM_DELETE_WINDOW',close);win.project_close=close;text.focus_set();return text

    def close_project_editors(self):
        for win in list(getattr(self,'project_editors',{}).values()):
            if win.winfo_exists():win.project_close()
        return not any(win.winfo_exists() for win in getattr(self,'project_editors',{}).values())

    def deploy_project(self):
        if not self.save():return
        if any(win.winfo_exists() for win in getattr(self,'project_editors',{}).values()):
            return messagebox.showinfo('Deploy',tr('Salva e chiudi gli editor dei file prima del deploy.'),parent=self)
        if not self.check():return
        win=tk.Toplevel(self);win.title('Deploy');win.geometry('720x510');win.transient(self)
        body=ttk.Frame(win,padding=18);body.pack(fill='both',expand=True)
        name=tk.StringVar(value='MyApplication');version=tk.StringVar(value='1.0.0');destination=tk.StringVar(value=str(self.path.parent/'deploy'))
        for i,(label,var) in enumerate([('Nome applicazione',name),('Versione',version),('Destinazione',destination)]):
            ttk.Label(body,text=tr(label)).grid(row=i,column=0,sticky='w',pady=8);ttk.Entry(body,textvariable=var,width=43).grid(row=i,column=1,sticky='ew')
        def browse():
            value=filedialog.askdirectory(parent=win)
            if value:destination.set(value)
        ttk.Button(body,text=tr('Sfoglia…'),command=browse).grid(row=2,column=2)
        icon=tk.StringVar(value=self.project.get('deployment',{}).get('icon',''))
        ttk.Label(body,text=tr('Icona applicazione')).grid(row=3,column=0,sticky='w',pady=8)
        ttk.Entry(body,textvariable=icon,state='readonly',width=43).grid(row=3,column=1,sticky='ew')
        preview=ttk.Label(body);preview.grid(row=4,column=0,sticky='w')
        def show_icon():
            preview.configure(image='',text='');preview.image=None
            if icon.get():
                try:
                    image=tk.PhotoImage(master=win,file=str(project_file(self.path.parent,icon.get())))
                    image=image.subsample(max(1,image.width()//48));preview.configure(image=image);preview.image=image
                except (OSError,tk.TclError,ValueError):preview.configure(text=tr('Icona non disponibile: selezionala nuovamente.'))
        def choose_icon():
            source=filedialog.askopenfilename(parent=win,title=tr('Scegli icona applicazione'),filetypes=[('PNG / ICO / ICNS','*.png *.ico *.icns')])
            if not source:return
            try:icon.set(import_icon(source,self.path.parent));show_icon()
            except Exception as exc:messagebox.showerror(tr('Icona applicazione'),str(exc),parent=win)
        icon_actions=ttk.Frame(body);icon_actions.grid(row=3,column=2)
        ttk.Button(icon_actions,text=tr('Sfoglia…'),command=choose_icon).pack(side='left')
        ttk.Button(icon_actions,text=tr('Rimuovi'),command=lambda:(icon.set(''),show_icon())).pack(side='left')
        ttk.Label(body,text=tr('PNG, ICO o ICNS quadrata, almeno 256 px. Consigliata: PNG trasparente 1024 × 1024. Conversione automatica per Mac e Windows.'),wraplength=540).grid(row=4,column=1,columnspan=2,sticky='w')
        show_icon()
        ttk.Label(body,text=tr('Genera un kit Mac + Windows. La compilazione va eseguita sul sistema di destinazione. Include soltanto i file contrassegnati ✓.'),wraplength=590).grid(row=5,column=0,columnspan=3,pady=12)
        build=tk.BooleanVar(value=False);ttk.Checkbutton(body,text=tr('Compila anche su questo computer (installa le dipendenze nel kit)'),variable=build).grid(row=6,column=0,columnspan=3,sticky='w')
        def create():
            try:
                if not destination.get().strip():raise ValueError(tr('Scegli una cartella di destinazione.'))
                if build.get() and self.proc and self.proc.poll() is None:raise ValueError(tr('Arresta prima il processo corrente.'))
                candidate={**self.project,'deployment':{'name':name.get(),'version':version.get(),'icon':icon.get()}}
                target=export_deployment(candidate,self.path,destination.get(),name.get(),version.get())
                self.checkpoint();self.project['deployment']=candidate['deployment']
                self.save();win.destroy();self.refresh_project_files();self.write_log('Deploy: '+str(target)+'\n');self.show_log(True)
                if build.get():self.launch([self.config_data['python'],str(target/'deploy_build.py'),'build'],cwd=str(target))
                else:messagebox.showinfo('Deploy',str(target)+'\n'+tr('Kit pronto. Leggi README_DEPLOY.md e usa gli script del sistema di destinazione.'),parent=self)
            except Exception as exc:messagebox.showerror('Deploy',str(exc),parent=win)
        ttk.Button(body,text=tr('Genera deploy'),command=create,style='Accent.TButton').grid(row=7,column=0,columnspan=3,pady=12)
        name.set(self.project.get('deployment',{}).get('name','MyApplication'));version.set(self.project.get('deployment',{}).get('version','1.0.0'))
