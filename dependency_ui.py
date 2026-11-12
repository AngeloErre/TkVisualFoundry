"""Guided, asynchronous PIP installation with verification and visible outcomes."""
import json
import queue
import subprocess
import threading
import tkinter as tk
from tkinter import ttk,messagebox
from tkinter.scrolledtext import ScrolledText
from components import registry,install_args
from dependency_manager import dependency_plan,probe_interpreter,pip_install_command,NOTES
from runtime_requirements import validate_interpreter

class DependencyWizard(tk.Toplevel):
    def __init__(self,studio,kind=None,props=None,on_ready=None,allow_skip=False,specs=None):
        super().__init__(studio);self.studio=studio;self.kind=kind;self.props=props;self.on_ready=on_ready;self.events=queue.Queue();self.busy=False;self.closed=False;self.process=None;self.cancelled=False;self.results=[];self.specs=[];self.explicit_specs=specs
        self.title('Configurazione guidata • pacchetti PIP');self.geometry('850x630');self.minsize(700,500);self.transient(studio)
        self.python=studio.config_data['python']
        ttk.Label(self,text='Prepara i componenti prima di usarli',style='Brand.TLabel',padding=12).pack(anchor='w')
        ttk.Label(self,text='1. Requisiti  →  2. Installa  →  3. Verifica finale',padding=(12,0)).pack(anchor='w')
        row=ttk.Frame(self,padding=12);row.pack(fill='x');ttk.Label(row,text='Componente').pack(side='left')
        self.choice=tk.StringVar(value=kind or ('Pacchetti selezionati' if specs is not None else 'Intero progetto'));self.selector=ttk.Combobox(row,textvariable=self.choice,values=['Intero progetto']+list(registry(studio.project)),state='disabled' if kind or specs is not None else 'readonly',width=30);self.selector.pack(side='left',padx=8);self.selector.bind('<<ComboboxSelected>>',lambda e:self.plan())
        ttk.Label(self,text='Interprete di destinazione: '+self.python,padding=(12,0),wraplength=800).pack(anchor='w')
        self.note=tk.StringVar();ttk.Label(self,textvariable=self.note,wraplength=790,padding=12).pack(fill='x')
        self.table=ttk.Treeview(self,columns=('spec','state','version','detail'),show='headings',height=6)
        for key,label,width in [('spec','Requisito',200),('state','Stato',110),('version','Versione',100),('detail','Dettagli',360)]:self.table.heading(key,text=label);self.table.column(key,width=width)
        self.table.pack(fill='x',padx=12)
        self.binary=tk.BooleanVar(value=studio.config_data.get('pip_binary_only',True));self.binary_check=ttk.Checkbutton(self,text='Usa solo pacchetti precompilati (evita compilazioni locali)',variable=self.binary);self.binary_check.pack(anchor='w',padx=12,pady=6)
        self.output=ScrolledText(self,height=7,wrap='word',font=('Menlo',11));self.output.pack(fill='both',expand=True,padx=12,pady=6)
        self.status=tk.StringVar(value='Nessuna installazione avviata.');ttk.Label(self,textvariable=self.status,wraplength=800,padding=(12,6)).pack(fill='x')
        row=ttk.Frame(self,padding=12);row.pack(fill='x')
        self.verify_button=ttk.Button(row,text='1. Verifica requisiti',command=self.verify);self.verify_button.pack(side='left',padx=3)
        self.install_button=ttk.Button(row,text='2. Installa / ripara',command=self.install);self.install_button.pack(side='left',padx=3)
        self.ready_button=ttk.Button(row,text='3. Continua' if on_ready else 'Fine',command=self.finish,state='disabled');self.ready_button.pack(side='right',padx=3)
        self.cancel_button=ttk.Button(row,text='Chiudi',command=self.close);self.cancel_button.pack(side='right',padx=3)
        if allow_skip:ttk.Button(row,text='Solo designer',command=self.skip).pack(side='right',padx=3)
        self.protocol('WM_DELETE_WINDOW',self.close);self.timer=self.after(80,self.poll);self.plan();self.check_timer=self.after(100,self.verify)

    def plan(self):
        if self.busy:return
        kind=None if self.choice.get()=='Intero progetto' else self.choice.get()
        self.specs=list(self.explicit_specs) if self.explicit_specs is not None else dependency_plan(self.studio.project,kind,self.props);
        if self.specs:install_args(self.python,self.specs)
        self.results=[];self.ready_button.configure(state='disabled');self.table.delete(*self.table.get_children())
        for i,spec in enumerate(self.specs):self.table.insert('','end',iid=str(i),values=(spec,'Da verificare','',''))
        self.note.set(NOTES.get(kind,'PIP installerà anche le dipendenze indirette necessarie. I pacchetti vanno installati nell’interprete indicato, non in un altro Python.'))
        if not self.specs:self.note.set((NOTES.get(kind,'Il progetto usa solo moduli inclusi in Python.'))+' Nessun pacchetto PIP richiesto.')

    def work(self,callback):
        if self.busy:return
        self.busy=True;self.cancelled=False
        for button in (self.verify_button,self.install_button,self.ready_button):button.configure(state='disabled')
        self.selector.configure(state='disabled');self.binary_check.configure(state='disabled');self.cancel_button.configure(text='Interrompi')
        def worker():
            try:self.events.put(('result',callback()))
            except Exception as exc:self.events.put(('error',str(exc)))
        threading.Thread(target=worker,daemon=True).start()

    def verify(self):
        timer=getattr(self,'check_timer',None)
        if timer:self.after_cancel(timer);self.check_timer=None
        self.status.set('Verifica in corso…')
        def check():validate_interpreter(self.python);return probe_interpreter(self.python,self.specs)
        self.work(check)

    def install(self):
        specs=list(self.specs);binary=self.binary.get();repair=any(item['state']=='broken' for item in self.results)
        if not specs:return self.verify()
        self.status.set('Installazione in corso. L’output compare qui sotto.')
        def install():
            validate_interpreter(self.python)
            command=pip_install_command(self.python,specs,binary)
            if repair:command.append('--force-reinstall')
            commands=[]
            if subprocess.run([self.python,'-m','pip','--version'],capture_output=True,timeout=15).returncode:commands.append([self.python,'-m','ensurepip','--upgrade'])
            commands += [command,[self.python,'-m','pip','check']]
            for args in commands:
                if self.cancelled:raise RuntimeError('Installazione interrotta. I pacchetti già installati restano disponibili; verifica di nuovo.')
                self.events.put(('log','$ '+' '.join(args)+'\n'))
                process=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
                self.process=process
                if self.cancelled:process.terminate()
                timeout=threading.Timer(600,process.kill);timeout.daemon=True;timeout.start()
                try:
                    for line in process.stdout:self.events.put(('log',line))
                    code=process.wait()
                finally:timeout.cancel();process.stdout.close();self.process=None
                if self.cancelled:raise RuntimeError('Installazione interrotta. Premi Verifica prima di continuare.')
                if code:raise RuntimeError('PIP ha restituito un errore. Consulta il log. Se manca una distribuzione per questo Python, prova un’altra versione del pacchetto; puoi disattivare “solo precompilati” se disponi degli strumenti di compilazione. Nessuna installazione è dichiarata riuscita.')
            return probe_interpreter(self.python,specs)
        self.work(install)

    def poll(self):
        if self.closed:return
        try:
            while True:
                kind,data=self.events.get_nowait()
                if kind=='log':self.output.insert('end',data);self.output.see('end');continue
                self.busy=False;self.cancel_button.configure(text='Chiudi');self.verify_button.configure(state='normal');self.install_button.configure(state='normal');self.binary_check.configure(state='normal')
                if not self.kind and self.explicit_specs is None:self.selector.configure(state='readonly')
                if kind=='error':self.output.insert('end',data+'\n');self.status.set(data);self.ready_button.configure(state='disabled');continue
                self.results=data
                states={'ready':'Pronto','missing':'Mancante','incompatible':'Da aggiornare','broken':'Import fallito'}
                for i,item in enumerate(data):self.table.item(str(i),values=(item['spec'],states[item['state']],item['version'],item['detail']))
                ready=all(i['state']=='ready' for i in data)
                self.ready_button.configure(state='normal' if ready else 'disabled');self.status.set('Pronto: requisiti verificati nell’interprete configurato.' if ready else 'Requisiti mancanti o incompatibili: premi Installa / ripara, poi attendi la verifica finale.')
        except queue.Empty:pass
        self.timer=self.after(80,self.poll)

    def finish(self):
        if self.busy or str(self.ready_button['state'])=='disabled':return
        if self.python!=self.studio.config_data['python']:
            self.status.set('L’interprete è cambiato: chiudi e riapri il wizard per verificarlo.');return
        callback=self.on_ready;self.dispose()
        if callback:callback()
    def skip(self):
        if self.busy:return
        callback=self.on_ready;self.dispose()
        if callback:callback()
    def dispose(self):
        self.closed=True;self.after_cancel(self.timer)
        if getattr(self,'check_timer',None):self.after_cancel(self.check_timer);self.check_timer=None
        self.destroy()
    def close(self):
        if self.busy:
            self.cancelled=True;process=self.process
            if process and process.poll() is None:
                process.terminate()
                def kill():
                    if process.poll() is None:process.kill()
                self.after(2000,kill)
            self.status.set('Interruzione richiesta. Attendi la conclusione prima di chiudere.');return
        self.dispose()
