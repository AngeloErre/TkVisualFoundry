"""Read-only file inspection with isolated project-Python workers and refresh."""
import json
from pathlib import Path
import queue
import subprocess
import threading
import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from data_reader import REQUIREMENTS,difference
from i18n import tr


class DataViewer(tk.Toplevel):
    def __init__(self,studio):
        super().__init__(studio);self.studio=studio;self.title(tr('Visualizzatore dati'));self.geometry('1050x650');self.minsize(700,430)
        self.path='';self.current=None;self.baseline=None;self.process=None;self.sequence=0;self.closed=False;self.busy=False;self.events=queue.Queue();self.after_id=None
        self.path_text=tk.StringVar();self.dataset=tk.StringVar();self.query=tk.StringVar();self.auto=tk.BooleanVar();self.show_baseline=tk.BooleanVar();self.status=tk.StringVar(value=tr('Apri un file dati per controllarne il contenuto.'))
        top=ttk.Frame(self,padding=8);top.pack(fill='x')
        ttk.Button(top,text=tr('Apri file dati…'),command=self.open_file).pack(side='left')
        ttk.Button(top,text=tr('Aggiorna'),command=self.refresh).pack(side='left',padx=5)
        ttk.Checkbutton(top,text=tr('Aggiorna ogni 2 secondi'),variable=self.auto).pack(side='left')
        ttk.Checkbutton(top,text=tr('Mostra riferimento'),variable=self.show_baseline,command=self.render).pack(side='left',padx=5)
        ttk.Button(top,text=tr('Nuovo riferimento'),command=self.reset_baseline).pack(side='right')
        ttk.Label(self,textvariable=self.path_text,padding=8,wraplength=950).pack(fill='x')
        controls=ttk.Frame(self,padding=8);controls.pack(fill='x');ttk.Label(controls,text=tr('Tabella / foglio')).pack(side='left')
        self.selector=ttk.Combobox(controls,textvariable=self.dataset,state='readonly',width=30);self.selector.pack(side='left',padx=5);self.selector.bind('<<ComboboxSelected>>',lambda e:self.refresh())
        ttk.Label(controls,text=tr('Filtra anteprima')).pack(side='left',padx=5);ttk.Entry(controls,textvariable=self.query).pack(side='left',fill='x',expand=True);self.query.trace_add('write',lambda *a:self.render())
        self.packages=ttk.Button(controls,text=tr('Prepara lettore PIP…'),command=self.prepare);self.packages.pack(side='right',padx=5)
        area=ttk.Frame(self);area.pack(fill='both',expand=True,padx=8);area.rowconfigure(0,weight=1);area.columnconfigure(0,weight=1)
        self.table=ttk.Treeview(area,show='headings');self.table.grid(row=0,column=0,sticky='nsew')
        y=ttk.Scrollbar(area,orient='vertical',command=self.table.yview);y.grid(row=0,column=1,sticky='ns');x=ttk.Scrollbar(area,orient='horizontal',command=self.table.xview);x.grid(row=1,column=0,sticky='ew');self.table.configure(yscrollcommand=y.set,xscrollcommand=x.set)
        ttk.Label(self,textvariable=self.status,padding=8,wraplength=1000).pack(fill='x')
        ttk.Label(self,text=tr('Sola lettura • confronto sulla sola anteprima: massimo 500 righe, 80 colonne, 512 caratteri per cella. CSV: prima riga come intestazione. Excel: formule visibili, non calcolate.'),padding=8,wraplength=1000).pack(fill='x')
        self.protocol('WM_DELETE_WINDOW',self.close);self.after_id=self.after(100,self.poll);self.auto_id=self.after(2000,self.tick)
    def open_file(self):
        path=filedialog.askopenfilename(parent=self,title=tr('Apri file dati…'),filetypes=[(tr('File dati'),'*.sqlite *.sqlite3 *.db *.sql *.mdb *.accdb *.dbx *.dbf *.xls *.xlsx *.xlsm *.json *.jsonl *.ndjson *.csv *.tsv *.txt *.parquet'),(tr('Tutti i file'),'*')])
        if not path:return
        self.sequence+=1
        if self.process and self.process.poll() is None:self.process.terminate()
        self.path=path;self.path_text.set(path);self.dataset.set('');self.selector.configure(values=());self.current=None;self.baseline=None;self.show_baseline.set(False);self.render();self.busy=False;self.refresh()
    def refresh(self):
        if self.closed or self.busy or not self.path:return
        self.sequence+=1;token=self.sequence;request={'path':self.path,'dataset':self.dataset.get()};self.busy=True;self.selector.configure(state='disabled')
        self.status.set(tr('Lettura in corso…'))
        python=self.studio.config_data['python']
        def work():
            process=None
            try:
                process=subprocess.Popen([python,'-u',str(Path(__file__).with_name('data_reader.py'))],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8',errors='replace')
                if self.closed or token!=self.sequence:process.terminate()
                else:self.process=process
                output,errors=process.communicate(json.dumps(request),timeout=20)
                if process.returncode:raise RuntimeError(errors[-1000:] or 'Reader process failed')
                result=json.loads(output)
            except Exception as error:
                if process and process.poll() is None:process.kill();process.communicate()
                result={'ok':False,'error':str(error)[:1500]}
            self.events.put((token,result))
        threading.Thread(target=work,daemon=True).start()
    def poll(self):
        if self.closed:return
        try:
            while True:
                token,result=self.events.get_nowait()
                if token!=self.sequence:continue
                self.busy=False;self.selector.configure(state='readonly')
                if not result.get('ok'):
                    self.auto.set(False);self.status.set(tr('Lettura non riuscita: {v0}',v0=result.get('error',''))+(tr(' • Ultima lettura riuscita: {v0}',v0=self.current['read_at']) if self.current else ''));continue
                data=result['data'];self.current=data;self.dataset.set(data['selected']);self.selector.configure(values=data['datasets'])
                if self.baseline is None or difference(self.baseline,data) is None:self.baseline=data
                delta=difference(self.baseline,data)
                self.status.set(tr('Letto: {v0} • Righe nel campione: {v1} • Aggiunte: {v2}, rimosse: {v3} • Colonne cambiate: {v4}',v0=data['read_at'],v1=len(data['rows']),v2=delta['added'],v3=delta['removed'],v4=tr('Sì') if delta['columns_changed'] else tr('No')))
                self.render()
        except queue.Empty:pass
        self.after_id=self.after(100,self.poll)
    def render(self):
        self.table.delete(*self.table.get_children());data=self.baseline if self.show_baseline.get() else self.current
        if not data:self.table.configure(columns=());return
        ids=['c'+str(i) for i in range(len(data['columns']))];self.table.configure(columns=ids)
        for key,label in zip(ids,data['columns']):self.table.heading(key,text=label);self.table.column(key,width=160,minwidth=60,stretch=False)
        query=self.query.get().casefold()
        for row in data['rows']:
            if not query or any(query in value.casefold() for value in row):self.table.insert('','end',values=row)
    def reset_baseline(self):
        if self.current:self.baseline=self.current;self.render();self.status.set(tr('Riferimento aggiornato al campione visualizzato.'))
    def prepare(self):
        specs=REQUIREMENTS.get(Path(self.path).suffix.lower(),[])
        if not specs:return messagebox.showinfo(tr('Visualizzatore dati'),tr('Questo formato non richiede pacchetti PIP oppure non è supportato.'),parent=self)
        from dependency_ui import DependencyWizard
        self.studio.dependency_window=DependencyWizard(self.studio,specs=specs,auto_install=True,on_ready=lambda:self.refresh() if not self.closed else None)
    def tick(self):
        if self.closed:return
        if self.auto.get():self.refresh()
        self.auto_id=self.after(2000,self.tick)
    def close(self):
        self.closed=True;self.sequence+=1
        for timer in (self.after_id,self.auto_id):
            if timer:self.after_cancel(timer)
        if self.process and self.process.poll() is None:self.process.terminate()
        self.destroy()


class DataViewerMixin:
    def open_data_viewer(self):
        win=getattr(self,'data_viewer_window',None)
        if win is not None and win.winfo_exists():win.lift();return
        self.data_viewer_window=DataViewer(self)
