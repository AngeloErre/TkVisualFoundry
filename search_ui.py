"""Global search snapshots editor buffers on Tk and searches on a cancellable worker."""
import copy
from pathlib import Path
import queue
import threading
import tkinter as tk
from tkinter import ttk,messagebox
from project_files import project_file
from project_search import project_sources,search,digest,read_python
from i18n import tr


def source_index(widget,text,line,column):
    # Tcl 8.6 and Tcl 9 differ in non-BMP character lengths.
    prefix=text.split('\n')[line-1][:column]
    return f"{line}.{widget.tk.call('string','length',prefix)}"


class GlobalSearch(tk.Toplevel):
    def __init__(self,studio):
        super().__init__(studio);self.studio=studio;self.title(tr('Ricerca globale'));self.geometry('1000x600');self.minsize(700,400)
        self.query=tk.StringVar();self.case=tk.BooleanVar();self.word=tk.BooleanVar();self.status=tk.StringVar(value=tr('Cerca negli eventi e nei file Python, inclusi gli editor non salvati.'))
        self.sequence=0;self.closed=False;self.stop=threading.Event();self.results=queue.Queue();self.rows=[];self.owner=None
        top=ttk.Frame(self,padding=8);top.pack(fill='x');self.entry=ttk.Entry(top,textvariable=self.query);self.entry.pack(side='left',fill='x',expand=True)
        ttk.Button(top,text=tr('Cerca nel progetto'),command=self.run).pack(side='left',padx=5);ttk.Button(top,text=tr('Interrompi'),command=self.cancel).pack(side='left')
        options=ttk.Frame(self,padding=8);options.pack(fill='x');ttk.Checkbutton(options,text=tr('Maiuscole/minuscole'),variable=self.case).pack(side='left');ttk.Checkbutton(options,text=tr('Parola intera'),variable=self.word).pack(side='left',padx=10)
        area=ttk.Frame(self);area.pack(fill='both',expand=True,padx=8);area.rowconfigure(0,weight=1);area.columnconfigure(0,weight=1)
        self.tree=ttk.Treeview(area,columns=('source','line','preview'),show='headings')
        for key,label,width in [('source',tr('Componente / file'),300),('line',tr('Riga'),70),('preview',tr('Anteprima'),550)]:self.tree.heading(key,text=label);self.tree.column(key,width=width,stretch=key!='line')
        self.tree.grid(row=0,column=0,sticky='nsew');y=ttk.Scrollbar(area,command=self.tree.yview);y.grid(row=0,column=1,sticky='ns');x=ttk.Scrollbar(area,orient='horizontal',command=self.tree.xview);x.grid(row=1,column=0,sticky='ew');self.tree.configure(yscrollcommand=y.set,xscrollcommand=x.set)
        ttk.Label(self,textvariable=self.status,wraplength=950,padding=8).pack(fill='x')
        ttk.Label(self,text=tr('Doppio clic o Invio apre la riga. Ricerca letterale; nessun file viene salvato. Limiti: 1.000 risultati, 200 file Python, 2 MiB per sorgente, 20 MiB totali.'),wraplength=950,padding=8).pack(fill='x')
        self.entry.bind('<Return>',lambda e:self.run());self.tree.bind('<Return>',self.navigate);self.tree.bind('<Double-1>',self.navigate)
        self.protocol('WM_DELETE_WINDOW',self.close);self.timer=self.after(100,self.poll);self.entry.focus_set()
    def snapshot(self):
        studio=self.studio;project=copy.deepcopy(studio.project);override=None;target=studio.code_target
        if target:
            obj,key,global_=target
            if global_:override=(('global',key),studio.code.get('1.0','end-1c'))
            else:
                for form in studio.project['forms']:
                    if obj is form or any(obj is widget for widget in form['widgets']):override=(('event',form['name'],obj['name'],key),studio.code.get('1.0','end-1c'));break
        root=studio.project_root();buffers={}
        if root:
            for path,win in getattr(studio,'project_editors',{}).items():
                if win.winfo_exists() and path.is_relative_to(root) and path.suffix=='.py' and hasattr(win,'project_text'):buffers[path.relative_to(root).as_posix()]=win.project_text.get('1.0','end-1c')
        return project,override,root,buffers
    def run(self):
        if not self.query.get():self.entry.focus_set();return
        self.stop.set();self.stop=threading.Event();stop=self.stop;self.sequence+=1;serial=self.sequence
        self.owner=self.studio.project;self.root_path=self.studio.project_root();project,override,root,buffers=self.snapshot();query=self.query.get();case=self.case.get();word=self.word.get()
        self.rows=[];self.tree.delete(*self.tree.get_children());self.status.set(tr('Ricerca in corso…'))
        def work():
            try:result=search(project,query,root,buffers,override,case,word,stop)
            except Exception as exc:result={'error':str(exc)}
            self.results.put((serial,result))
        threading.Thread(target=work,daemon=True).start()
    def cancel(self):
        self.stop.set();self.sequence+=1;self.status.set(tr('Ricerca interrotta.'))
    def poll(self):
        if self.closed:return
        try:
            while True:
                serial,result=self.results.get_nowait()
                if serial!=self.sequence:continue
                if self.owner is not self.studio.project or self.root_path!=self.studio.project_root():self.rows=[];self.status.set(tr('Progetto cambiato: ripeti la ricerca.'));continue
                if 'error' in result:self.status.set(tr('Ricerca non riuscita: {v0}',v0=result['error']));continue
                if result['cancelled']:continue
                self.rows=result['rows']
                for i,row in enumerate(self.rows):self.tree.insert('','end',iid=str(i),values=(row['label'],row['line'],row['preview']))
                note=tr(' • Risultati limitati') if result['truncated'] else ''
                if result['warnings']:note+=tr(' • Sorgenti escluse o limiti: {v0}',v0='; '.join(result['warnings'])[:350])
                if self.root_path is None:note+=tr(' • Salva il progetto per cercare anche nei file Python.')
                self.status.set(tr('Risultati: {v0}',v0=len(self.rows))+note)
        except queue.Empty:pass
        self.timer=self.after(100,self.poll)
    def navigate(self,event=None):
        selection=self.tree.selection()
        if not selection:return 'break'
        if self.owner is not self.studio.project or self.root_path!=self.studio.project_root():self.run();return 'break'
        row=self.rows[int(selection[0])];key=row['key'];studio=self.studio
        try:
            project,override,root,buffers=self.snapshot()
            if key[0]=='file':
                relative=key[1];path=project_file(root,relative)
                current=buffers[relative] if relative in buffers else read_python(path)
            else:current=next(source['text'] for source in project_sources(project,override) if source['key']==key)
            if digest(current)!=row['digest']:self.status.set(tr('Sorgente modificata: ripeti la ricerca prima di navigare.'));return 'break'
            if key[0]=='file':target=studio.open_project_file(relative=key[1])
            else:
                studio.commit_code()
                if key[0]=='global':studio.global_code(key[1])
                else:studio.choose_designer_object(key[2]);studio.evvar.set(key[3]);studio.edit_event()
                target=studio.code
            if target is not None:
                opened_text=target.get('1.0','end-1c')
                if digest(opened_text)!=row['digest']:self.status.set(tr('Sorgente modificata: ripeti la ricerca prima di navigare.'));return 'break'
                start=source_index(target,opened_text,row['line'],row['column']);end=source_index(target,opened_text,row['endline'],row['endcolumn']);target.tag_remove('sel','1.0','end');target.tag_add('sel',start,end);target.mark_set('insert',start);target.see(start);target.winfo_toplevel().lift();target.focus_set()
        except (OSError,ValueError,StopIteration) as exc:messagebox.showinfo(tr('Ricerca globale'),tr('Risultato non più disponibile: {v0}',v0=str(exc)),parent=self)
        return 'break'
    def close(self):
        if self.closed:return
        self.closed=True;self.stop.set();self.after_cancel(self.timer);self.destroy()


class SearchMixin:
    def open_global_search(self,event=None):
        win=getattr(self,'global_search_window',None)
        if win is not None and win.winfo_exists():win.lift();win.entry.focus_set()
        else:self.global_search_window=GlobalSearch(self)
        return 'break'
