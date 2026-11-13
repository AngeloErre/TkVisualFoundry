"""Automatic preparation of component dependencies with an always-visible footer."""
from i18n import tr
import queue
import threading
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from components import registry,install_args
from dependency_manager import dependency_plan,probe_interpreter,install_dependencies,preparation_action,NOTES
from runtime_requirements import validate_interpreter

class DependencyWizard(tk.Toplevel):
    def __init__(self,studio,kind=None,props=None,on_ready=None,allow_skip=False,specs=None,auto_install=False):
        super().__init__(studio);self.studio=studio;self.kind=kind;self.props=props;self.on_ready=on_ready;self.events=queue.Queue();self.busy=False;self.closed=False;self.process=None;self.cancelled=False;self.results=[];self.specs=[];self.explicit_specs=specs;self.ready=False;self.install_attempted=False;self.check_timer=None;self.auto_timer=None
        self.title(tr('Pacchetti PIP • preparazione automatica'));self.geometry('800x540');self.minsize(640,420);self.transient(studio);self.python=studio.config_data['python']
        self.columnconfigure(0,weight=1);self.rowconfigure(1,weight=1)
        header=ttk.Frame(self,padding=12);header.grid(row=0,column=0,sticky='ew');header.columnconfigure(0,weight=1)
        ttk.Label(header,text=tr('Prepara il componente'),style='Title.TLabel').grid(row=0,column=0,sticky='w')
        ttk.Label(header,text='Python: '+self.python,wraplength=740).grid(row=1,column=0,sticky='w',pady=(5,0))
        self.pages=ttk.Notebook(self);self.pages.grid(row=1,column=0,sticky='nsew',padx=12)
        requirements=ttk.Frame(self.pages,padding=8);requirements.columnconfigure(0,weight=1);requirements.rowconfigure(3,weight=1)
        logs=ttk.Frame(self.pages);self.pages.add(requirements,text=tr('Requisiti e opzioni'));self.pages.add(logs,text=tr('Log installazione'))
        self.choice=tk.StringVar(value=kind or (tr('Pacchetti selezionati') if specs is not None else tr('Intero progetto')))
        self.selector=ttk.Combobox(requirements,textvariable=self.choice,values=[tr('Intero progetto')]+list(registry(studio.project)),state='disabled' if kind or specs is not None or on_ready else 'readonly');self.selector.grid(row=0,column=0,sticky='ew');self.selector.bind('<<ComboboxSelected>>',self.change_plan)
        self.note=tk.StringVar();ttk.Label(requirements,textvariable=self.note,wraplength=700).grid(row=1,column=0,sticky='ew',pady=8)
        options=ttk.Frame(requirements);options.grid(row=2,column=0,sticky='ew')
        self.automatic=tk.BooleanVar(value=auto_install);self.auto_check=ttk.Checkbutton(options,text=tr('Installa automaticamente i requisiti mancanti'),variable=self.automatic,command=self.auto_changed);self.auto_check.pack(anchor='w')
        self.binary=tk.BooleanVar(value=studio.config_data.get('pip_wheels_only',False));self.binary_check=ttk.Checkbutton(options,text=tr('Solo wheel (opzione avanzata: escludi pacchetti sorgenti)'),variable=self.binary);self.binary_check.pack(anchor='w')
        area=ttk.Frame(requirements);area.grid(row=3,column=0,sticky='nsew',pady=6);area.rowconfigure(0,weight=1);area.columnconfigure(0,weight=1)
        self.table=ttk.Treeview(area,columns=('spec','state','version','detail'),show='headings',height=5)
        for key,label,width in [('spec',tr('Pacchetto'),190),('state',tr('Stato'),100),('version',tr('Versione'),85),('detail',tr('Dettagli'),310)]:self.table.heading(key,text=label);self.table.column(key,width=width,minwidth=65)
        self.table.grid(row=0,column=0,sticky='nsew');scroll=ttk.Scrollbar(area,command=self.table.yview);scroll.grid(row=0,column=1,sticky='ns');self.table.configure(yscrollcommand=scroll.set)
        self.output=ScrolledText(logs,wrap='word',font=('Menlo',11));self.output.pack(fill='both',expand=True)
        footer=ttk.Frame(self,padding=12);footer.grid(row=2,column=0,sticky='ew');footer.columnconfigure(0,weight=1)
        self.status=tk.StringVar(value=tr('Verifica automatica in corso…'));ttk.Label(footer,textvariable=self.status,wraplength=730).grid(row=0,column=0,sticky='ew')
        self.progress=ttk.Progressbar(footer,mode='indeterminate');self.progress.grid(row=1,column=0,sticky='ew',pady=6)
        actions=ttk.Frame(footer);actions.grid(row=2,column=0,sticky='ew')
        self.install_button=ttk.Button(actions,text=tr('Installa / ripara'),command=self.install,style='Accent.TButton');self.install_button.pack(side='left',padx=(0,4))
        self.verify_button=ttk.Button(actions,text=tr('Verifica'),command=self.verify);self.verify_button.pack(side='left')
        self.ready_button=ttk.Button(actions,text=tr('Continua') if on_ready else tr('Fine'),command=self.finish,state='disabled');self.ready_button.pack(side='right',padx=(4,0))
        self.cancel_button=ttk.Button(actions,text=tr('Chiudi'),command=self.close);self.cancel_button.pack(side='right')
        self.skip_button=None
        if allow_skip:self.skip_button=ttk.Button(actions,text=tr('Solo designer'),command=self.skip);self.skip_button.pack(side='right',padx=4)
        self.protocol('WM_DELETE_WINDOW',self.close);self.timer=self.after(80,self.poll);self.plan();self.check_timer=self.after(100,self.verify)

    def plan(self):
        if self.busy:return
        self.cancel_pending();kind=None if self.choice.get()==tr('Intero progetto') else self.choice.get()
        self.specs=list(self.explicit_specs) if self.explicit_specs is not None else dependency_plan(self.studio.project,kind,self.props)
        if self.specs:install_args(self.python,self.specs)
        self.results=[];self.ready=False;self.install_attempted=False;self.ready_button.configure(state='disabled');self.table.delete(*self.table.get_children())
        for i,spec in enumerate(self.specs):self.table.insert('','end',iid=str(i),values=(spec,tr('Da verificare'),'',''))
        self.note.set(NOTES.get(kind,tr('Installazione nel Python indicato. PIP sceglie versioni compatibili e prepara anche le dipendenze indirette.')))
        if not self.specs:self.note.set(tr('Nessun pacchetto PIP richiesto. È sufficiente Python con Tkinter.'))
    def change_plan(self,event=None):self.plan();self.verify()
    def auto_changed(self):
        if self.busy:return
        self.cancel_pending()
        if self.automatic.get() and not self.ready:self.install_attempted=False;self.verify()
    def cancel_pending(self):
        for name in ('check_timer','auto_timer'):
            timer=getattr(self,name,None)
            if timer:self.after_cancel(timer);setattr(self,name,None)
    def controls(self):
        state='disabled' if self.busy else 'normal'
        for control in (self.verify_button,self.install_button,self.binary_check,self.auto_check):control.configure(state=state)
        if self.skip_button:self.skip_button.configure(state=state)
        self.ready_button.configure(state='normal' if self.ready and not self.busy else 'disabled')
        self.cancel_button.configure(text=tr('Interrompi') if self.busy else tr('Chiudi'))
        self.selector.configure(state='disabled' if self.busy or self.kind or self.explicit_specs is not None or self.on_ready else 'readonly')
        if self.busy:self.progress.start(12)
        else:self.progress.stop()
    def work(self,callback):
        if self.busy or self.closed:return
        self.busy=True;self.cancelled=False;self.ready=False;self.controls()
        def worker():
            try:
                data=callback()
                self.events.put(('cancelled' if self.cancelled else 'result',data))
            except Exception as exc:self.events.put(('cancelled' if self.cancelled else 'error',str(exc)))
        threading.Thread(target=worker,daemon=True).start()
    def verify(self):
        if self.busy or self.closed:return
        self.cancel_pending();self.status.set(tr('1/3 • Verifica dei requisiti…'));self.phase='verify'
        def check():validate_interpreter(self.python);return probe_interpreter(self.python,self.specs)
        self.work(check)
    def install(self):
        if self.busy or self.closed:return
        self.cancel_pending();specs=list(self.specs);binary=self.binary.get();repair=any(item['state']=='broken' for item in self.results)
        if not specs:return self.verify()
        self.install_attempted=True;self.phase='install';self.status.set(tr('2/3 • Installazione in corso. Puoi seguirla nella scheda Log.'));self.pages.select(1)
        def install():
            validate_interpreter(self.python)
            return install_dependencies(self.python,specs,binary,repair,on_output=lambda line:self.events.put(('log',line)),cancelled=lambda:self.cancelled,process_changed=lambda process:setattr(self,'process',process))
        self.work(install)
    def poll(self):
        if self.closed:return
        try:
            while True:
                kind,data=self.events.get_nowait()
                if kind=='log':self.output.insert('end',data);self.output.see('end');continue
                self.busy=False
                if kind in ('error','cancelled'):
                    self.ready=False;self.controls();text=str(data) if kind=='error' else tr('Operazione interrotta. Premi Verifica per controllare lo stato dei pacchetti.')
                    self.output.insert('end',text+'\n');self.pages.select(1)
                    self.status.set(text.splitlines()[0][:220])
                    if kind=='error' and getattr(self,'phase','')=='verify' and self.automatic.get() and not self.install_attempted and self.specs:
                        self.status.set(tr('Preparo PIP e i requisiti, poi ripeto la verifica…'));self.auto_timer=self.after(100,self.install)
                    continue
                self.results=data;states={'ready':tr('Pronto'),'missing':tr('Mancante'),'incompatible':tr('Incompatibile'),'broken':tr('Import fallito')}
                for i,item in enumerate(data):self.table.item(str(i),values=(item['spec'],states[item['state']],item['version'],item['detail']))
                action=preparation_action(data,self.automatic.get(),self.install_attempted,bool(self.on_ready))
                self.ready=action in ('ready','continue');self.controls()
                if self.ready:
                    if self.install_attempted and hasattr(self.studio,'restart_intellisense'):self.studio.restart_intellisense()
                    self.status.set(tr('3/3 • Componente pronto. Requisiti verificati.'));self.pages.select(0)
                    if action=='continue':self.auto_timer=self.after(200,self.finish)
                elif action=='install':self.auto_timer=self.after(100,self.install)
                else:self.status.set(tr('Requisiti da preparare: premi Installa / ripara. Gli errori dettagliati sono nella scheda Log.'))
        except queue.Empty:pass
        self.timer=self.after(80,self.poll)
    def finish(self):
        if self.busy or not self.ready or self.closed:return
        if self.python!=self.studio.config_data['python']:
            self.status.set(tr('Interprete cambiato: riapri la preparazione dei pacchetti.'));return
        callback=self.on_ready;self.dispose()
        if callback:callback()
    def skip(self):
        if self.busy:return
        callback=self.on_ready;self.dispose()
        if callback:callback()
    def dispose(self):
        self.closed=True;self.cancel_pending();self.after_cancel(self.timer);self.destroy()
    def close(self):
        self.cancel_pending()
        if self.busy:
            self.cancelled=True;process=self.process
            if process and process.poll() is None:
                process.terminate()
                def kill():
                    if process.poll() is None:process.kill()
                self.after(2000,kill)
            self.status.set(tr('Interruzione richiesta. Attendi il termine prima di chiudere.'));return
        self.dispose()
