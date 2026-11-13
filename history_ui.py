"""Minute-based local backups and explicit compare/open-as-copy recovery."""
import datetime
import hashlib
import json
import queue
import threading
import uuid
import tkinter as tk
from tkinter import ttk,messagebox
from tkinter.scrolledtext import ScrolledText
from local_history import HistoryStore,captured_project,compare_projects,recovered_path
from i18n import tr

class HistoryMixin:
    def init_local_history(self):
        self.history_store=HistoryStore();self.history_session=uuid.uuid4().hex;self.history_last_queued=None
        self.history_jobs=queue.Queue();self.history_results=queue.Queue();self.history_closed=False;self.history_rows=[];self.history_request=0
        self.history_label=tk.StringVar(value=tr('Cronologia locale'))
        ttk.Button(self.statusbar,textvariable=self.history_label,command=self.show_local_history,style='Toolbar.TButton').pack(side='right')
        def worker():
            while True:
                job=self.history_jobs.get()
                if job is None:return
                action,token,args=job
                try:
                    result=self.history_store.save(*args) if action=='save' else self.history_store.index() if action=='index' else self.history_store.read(*args)
                    self.history_results.put((action,token,result,None))
                except Exception as exc:self.history_results.put((action,token,None,str(exc)))
        self.history_thread=threading.Thread(target=worker,daemon=True);self.history_thread.start()
        self.history_poll=self.after(100,self.poll_local_history);self.history_auto=self.after(60000,self.autosave_local_history)
        self.bind('<Destroy>',self.destroy_local_history,add='+');self.history_jobs.put(('index',0,()))

    def history_capture(self):
        target=self.code_target
        context=(target[0].get('name'),target[1],target[2]) if target else None
        return captured_project(self.project,context,self.code.get('1.0','end-1c') if target else None)

    def queue_local_snapshot(self,kind='manual',only_dirty=False):
        if self.history_closed:return
        project=self.history_capture();serialized=json.dumps(project,sort_keys=True);dirty=serialized!=self.saved_state
        if only_dirty and not dirty:return
        identity=(str(self.path) if self.path else self.history_session,hashlib.sha256(serialized.encode()).hexdigest(),dirty)
        if identity==self.history_last_queued:return
        self.history_last_queued=identity
        self.history_jobs.put(('save',0,(project,str(self.path) if self.path else None,self.history_session,dirty,kind)))

    def autosave_local_history(self):
        if self.history_closed:return
        if self.config_data.get('local_history',True):self.queue_local_snapshot('autosave',True)
        self.history_auto=self.after(60000,self.autosave_local_history)

    def refresh_local_history(self):
        self.history_request+=1;self.history_jobs.put(('index',self.history_request,()))

    def show_local_history(self):
        previous=getattr(self,'history_window',None)
        if previous and previous.winfo_exists():previous.lift();self.refresh_local_history();return
        win=tk.Toplevel(self);self.history_window=win;win.title(tr('Cronologia e recupero locale'));win.geometry('940x650');win.minsize(760,480)
        ttk.Label(win,text=tr('Copie ogni 60 secondi delle modifiche al progetto. Recupera apre una copia: il file originale non viene sovrascritto.'),wraplength=900,padding=8).pack(fill='x')
        bar=ttk.Frame(win,padding=5);bar.pack(fill='x')
        ttk.Button(bar,text=tr('Salva punto locale'),command=lambda:self.queue_local_snapshot('manual')).pack(side='left')
        ttk.Button(bar,text=tr('Aggiorna'),command=self.refresh_local_history).pack(side='left')
        tree_area=ttk.Frame(win);tree_area.pack(fill='x',padx=8)
        self.history_tree=ttk.Treeview(tree_area,columns=('time','project','kind'),show='headings',height=9)
        for key,label,width in [('time',tr('Data'),180),('project',tr('Progetto'),550),('kind',tr('Tipo'),100)]:self.history_tree.heading(key,text=label);self.history_tree.column(key,width=width)
        scroll=ttk.Scrollbar(tree_area,command=self.history_tree.yview);scroll.pack(side='right',fill='y');self.history_tree.configure(yscrollcommand=scroll.set);self.history_tree.pack(fill='x')
        self.history_tree.bind('<<TreeviewSelect>>',lambda e:self.read_history_selection())
        self.history_diff=ScrolledText(win,wrap='word',font=('Menlo',11));self.history_diff.pack(fill='both',expand=True,padx=8,pady=5);self.history_diff.configure(state='disabled')
        ttk.Button(win,text=tr('Apri come copia recuperata'),command=lambda:self.read_history_selection(True)).pack(anchor='e',padx=8,pady=8)
        self.refresh_local_history()

    def read_history_selection(self,restore=False):
        if not self.history_tree.winfo_exists():return
        selected=self.history_tree.selection()
        if not selected:return
        row=self.history_rows[int(selected[0])];self.history_request+=1
        self.history_jobs.put(('restore' if restore else 'read',self.history_request,(row['file'],)))

    def poll_local_history(self):
        if self.history_closed:return
        try:
            while True:
                action,token,data,error=self.history_results.get_nowait()
                if action!='save' and token not in (0,self.history_request):continue
                if error:
                    if action=='save':self.history_last_queued=None
                    self.history_label.set(tr('Errore cronologia locale'));self.write_log(tr('Errore cronologia locale')+': '+error+'\n')
                    if action in ('restore','read'):messagebox.showerror(tr('Cronologia locale'),error,parent=self)
                    continue
                if action=='save':self.refresh_local_history()
                elif action=='index':
                    self.history_rows=data;self.history_label.set(tr('Copie locali: ')+str(len(data)))
                    if getattr(self,'history_window',None) and self.history_window.winfo_exists():
                        self.history_tree.delete(*self.history_tree.get_children())
                        for i,row in enumerate(data):
                            timestamp=datetime.datetime.fromtimestamp(row['created']/1e9).astimezone().strftime('%Y-%m-%d %H:%M:%S')
                            self.history_tree.insert('','end',iid=str(i),values=(timestamp,row['project_path'] or tr('Progetto senza nome'),row['kind']))
                elif action=='read':
                    if getattr(self,'history_window',None) and self.history_window.winfo_exists():
                        diff,truncated=compare_projects(self.history_capture(),data['project']);self.history_diff.configure(state='normal');self.history_diff.delete('1.0','end');self.history_diff.insert('1.0',diff or tr('Nessuna differenza.'))
                        if truncated:self.history_diff.insert('end','\n'+tr('Confronto troncato per dimensione.'))
                        self.history_diff.configure(state='disabled')
                elif getattr(self,'history_window',None) and self.history_window.winfo_exists():self.restore_local_snapshot(data)
        except queue.Empty:pass
        self.history_poll=self.after(100,self.poll_local_history)

    def restore_local_snapshot(self,record):
        try:
            path=recovered_path(record['project_path'])
            if path and record['project'].get('environment',{}).get('managed'):
                from project_environment import environment_python
                environment_python(path.parent)
        except Exception as exc:return messagebox.showerror(tr('Recupero'),str(exc),parent=self)
        if not self.dirty_guard():return
        try:path=recovered_path(record['project_path'])
        except Exception as exc:return messagebox.showerror(tr('Recupero'),str(exc),parent=self)
        self.recovery_unsaved=True;self.recovery_original=record['project_path']
        self.project=record['project'];self.path=path;self.form_index=0;self.selected=None;self.selection_names=set();self.code_target=None;self.history=[];self.future=[];self.breaks=set();self.saved_state=''
        self.history_session=uuid.uuid4().hex;self.history_last_queued=None
        self.refresh();self.history_window.lift()

    def finish_local_history(self):
        if self.history_closed:return
        if self.config_data.get('local_history',True):self.queue_local_snapshot('close',True)
        self.history_closed=True;self.history_jobs.put(None);self.history_thread.join(timeout=2)
        for timer in (self.history_auto,self.history_poll):
            try:self.after_cancel(timer)
            except Exception:pass

    def destroy_local_history(self,event):
        if event.widget is self and not self.history_closed:
            self.history_closed=True;self.history_jobs.put(None)
