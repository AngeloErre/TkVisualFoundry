"""SQLite/SQLAlchemy data adapter and an asynchronous, editable table component.

No connection is opened during construction; credentials are never component options.
"""
import datetime
import decimal
import os
import queue
import sqlite3
import threading
import tkinter as tk
from tkinter import ttk,filedialog,messagebox,simpledialog

class DatabaseSession:
    """One worker owns a session. All writes use transactions and primary keys."""
    def __init__(self):
        self.connection=None;self.engine=None;self.backend=None;self.table_name=None;self.meta=None;self.column_info=[]

    def connect(self,backend='sqlite',database='visualtk.sqlite',host='localhost',port=0,username='',password='',**ignored):
        self.disconnect();self.backend=backend
        if backend=='sqlite':
            if not database:raise ValueError('Scegli il percorso del database SQLite.')
            self.connection=sqlite3.connect(database,timeout=8)
            self.connection.row_factory=sqlite3.Row
            self.connection.execute('PRAGMA foreign_keys = ON')
        elif backend in ('postgresql','mysql'):
            from sqlalchemy import create_engine
            from sqlalchemy.engine import URL
            driver='postgresql+psycopg' if backend=='postgresql' else 'mysql+pymysql'
            url=URL.create(driver,username=username or None,password=password or None,host=host or None,port=int(port) if port else None,database=database)
            args={'connect_timeout':8} if backend=='postgresql' else {'connect_timeout':8,'read_timeout':15,'write_timeout':15}
            engine=create_engine(url,connect_args=args,pool_pre_ping=True,hide_parameters=True)
            try:
                with engine.connect() as connection:connection.exec_driver_sql('SELECT 1')
            except Exception:
                engine.dispose();raise RuntimeError('Connessione remota non riuscita: verifica server, database, credenziali, rete e driver.') from None
            self.engine=engine
        else:raise ValueError('Backend supportati: sqlite, postgresql, mysql.')
        return self.tables()

    def disconnect(self):
        if self.connection:self.connection.close()
        if self.engine:self.engine.dispose()
        self.connection=None;self.engine=None;self.table_name=None;self.meta=None;self.column_info=[]

    def tables(self):
        if self.connection:
            return [r[0] for r in self.connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
        if self.engine:
            from sqlalchemy import inspect
            return inspect(self.engine).get_table_names()
        raise RuntimeError('Connetti prima il database.')

    @staticmethod
    def quote(name):return '"'+str(name).replace('"','""')+'"'

    def use_table(self,name):
        if name not in self.tables():raise ValueError('Tabella non presente nel database.')
        self.table_name=name
        if self.connection:
            self.column_info=[{'name':r['name'],'type':r['type'],'pk':bool(r['pk']),'nullable':not r['notnull'],'default':r['dflt_value']} for r in self.connection.execute('PRAGMA table_info('+self.quote(name)+')')]
        else:
            from sqlalchemy import MetaData,Table
            self.meta=Table(name,MetaData(),autoload_with=self.engine)
            self.column_info=[{'name':c.name,'type':str(c.type),'pk':bool(c.primary_key),'nullable':c.nullable,'default':str(c.server_default.arg) if c.server_default is not None else None} for c in self.meta.columns]
        return self.column_info

    @property
    def primary_keys(self):return [c['name'] for c in self.column_info if c['pk']]

    def fetch(self,table=None,limit=200):
        if table is not None:self.use_table(table)
        if not self.table_name:raise ValueError('Seleziona una tabella.')
        limit=max(1,min(5000,int(limit)))
        if self.connection:return [dict(r) for r in self.connection.execute('SELECT * FROM '+self.quote(self.table_name)+' LIMIT ?', (limit,))]
        from sqlalchemy import select
        with self.engine.connect() as connection:return [dict(r) for r in connection.execute(select(self.meta).limit(limit)).mappings()]

    def _values(self,values):
        if not self.table_name:raise ValueError('Seleziona una tabella.')
        names={c['name'] for c in self.column_info}
        if not isinstance(values,dict) or any(k not in names for k in values):raise ValueError('Colonne non valide.')
        return values

    def _key(self,key):
        pks=self.primary_keys
        if not pks:raise ValueError('La tabella non ha una chiave primaria: modifica ed eliminazione sono disabilitate.')
        if not isinstance(key,dict) or set(key)!=set(pks) or any(v is None for v in key.values()):raise ValueError('È necessaria la chiave primaria completa e non NULL.')
        return key

    def insert(self,values):
        values=self._values(values)
        if self.connection:
            names=list(values)
            sql=('INSERT INTO '+self.quote(self.table_name)+' ('+', '.join(self.quote(k) for k in names)+') VALUES ('+', '.join('?' for _ in names)+')') if names else 'INSERT INTO '+self.quote(self.table_name)+' DEFAULT VALUES'
            with self.connection:cursor=self.connection.execute(sql,tuple(values.values()));return cursor.lastrowid
        from sqlalchemy import insert
        with self.engine.begin() as connection:
            result=connection.execute(insert(self.meta).values(**values));return tuple(result.inserted_primary_key)

    def update(self,key,values):
        key=self._key(key);values=self._values(values)
        if not values:raise ValueError('Nessuna modifica da salvare.')
        if any(k in self.primary_keys for k in values):raise ValueError('Le chiavi primarie non si modificano dall’editor.')
        if self.connection:
            sql='UPDATE '+self.quote(self.table_name)+' SET '+', '.join(self.quote(k)+'=?' for k in values)+' WHERE '+' AND '.join(self.quote(k)+'=?' for k in key)
            with self.connection:
                result=self.connection.execute(sql,tuple(values.values())+tuple(key.values()))
                if result.rowcount!=1:raise ValueError('Riga non trovata o chiave non univoca; transazione annullata.')
        else:
            from sqlalchemy import update,and_
            with self.engine.begin() as connection:
                result=connection.execute(update(self.meta).where(and_(*(self.meta.c[k]==v for k,v in key.items()))).values(**values))
                if result.rowcount!=1:raise ValueError('Riga non trovata o chiave non univoca; transazione annullata.')
        return 1

    def delete(self,key):
        key=self._key(key)
        if self.connection:
            with self.connection:
                result=self.connection.execute('DELETE FROM '+self.quote(self.table_name)+' WHERE '+' AND '.join(self.quote(k)+'=?' for k in key),tuple(key.values()))
                if result.rowcount!=1:raise ValueError('Riga non trovata o chiave non univoca; transazione annullata.')
        else:
            from sqlalchemy import delete,and_
            with self.engine.begin() as connection:
                result=connection.execute(delete(self.meta).where(and_(*(self.meta.c[k]==v for k,v in key.items()))))
                if result.rowcount!=1:raise ValueError('Riga non trovata o chiave non univoca; transazione annullata.')
        return 1

    def create_demo(self):
        if not self.connection:raise ValueError('L’esempio è disponibile solo con SQLite.')
        with self.connection:self.connection.execute('CREATE TABLE IF NOT EXISTS contatti (id INTEGER PRIMARY KEY, nome TEXT NOT NULL, email TEXT, note TEXT)')
        return self.tables()


def parse_database_value(text,type_name):
    """Typed fields; NULL is handled by an explicit switch, not empty text."""
    kind=type_name.upper()
    if 'BOOL' in kind:
        if text.lower() not in ('true','false','1','0'):raise ValueError('Booleano: usa true, false, 1 o 0.')
        return text.lower() in ('true','1')
    if 'INT' in kind:return int(text)
    if any(s in kind for s in ('REAL','FLOAT','DOUBLE')):return float(text)
    if any(s in kind for s in ('DECIMAL','NUMERIC')):return decimal.Decimal(text)
    if 'TIMESTAMP' in kind or 'DATETIME' in kind:return datetime.datetime.fromisoformat(text)
    if kind=='DATE':return datetime.date.fromisoformat(text)
    if 'BLOB' in kind or 'BINARY' in kind:raise ValueError('I campi binari vanno gestiti da codice.')
    return text


class DatabaseView(tk.Frame):
    def __init__(self,master,backend='sqlite',database='visualtk.sqlite',host='localhost',port=0,username='',password_env='VISUALTK_DB_PASSWORD',table='',limit=200,**kw):
        super().__init__(master,**kw)
        self.backend=backend;self.database=database;self.host=host;self.port=port;self.username=username;self.password_env=password_env;self.table_name=table;self.limit=int(limit)
        self.rows=[];self.columns=[];self.selected_record=None;self.last_error='';self.busy=False;self.closed=False;self.connected=False;self.generation=0
        self.tasks=queue.Queue();self.results=queue.Queue();self.session=DatabaseSession()
        # A single worker owns the DB connection (including SQLite's thread affinity).
        threading.Thread(target=self.worker,daemon=True).start()
        bar=ttk.Frame(self);bar.pack(fill='x');self.connect_button=ttk.Button(bar,text='Connetti…',command=self.connection_dialog);self.connect_button.pack(side='left')
        self.tables_box=ttk.Combobox(bar,state='readonly',width=20);self.tables_box.pack(side='left',padx=4);self.tables_box.bind('<<ComboboxSelected>>',lambda e:self.refresh())
        self.refresh_button=ttk.Button(bar,text='Aggiorna',command=self.refresh);self.refresh_button.pack(side='left')
        self.demo_button=ttk.Button(bar,text='Crea tabella esempio',command=self.create_demo);self.demo_button.pack(side='left')
        actions=ttk.Frame(self);actions.pack(fill='x')
        self.add_button=ttk.Button(actions,text='+ Nuovo record',command=lambda:self.edit_record(False));self.add_button.pack(side='left')
        self.edit_button=ttk.Button(actions,text='Modifica selezionato',command=lambda:self.edit_record(True));self.edit_button.pack(side='left')
        self.delete_button=ttk.Button(actions,text='Elimina selezionato',command=self.delete_selected);self.delete_button.pack(side='left')
        self.state=tk.StringVar(value='Disconnesso • SQLite non richiede PIP. Premi Connetti per iniziare.');ttk.Label(self,textvariable=self.state,wraplength=680).pack(fill='x')
        frame=ttk.Frame(self);frame.pack(fill='both',expand=True)
        self.gridview=ttk.Treeview(frame,show='headings',selectmode='browse');self.gridview.grid(row=0,column=0,sticky='nsew')
        ys=ttk.Scrollbar(frame,orient='vertical',command=self.gridview.yview);ys.grid(row=0,column=1,sticky='ns');xs=ttk.Scrollbar(frame,orient='horizontal',command=self.gridview.xview);xs.grid(row=1,column=0,sticky='ew')
        self.gridview.configure(yscrollcommand=ys.set,xscrollcommand=xs.set);frame.rowconfigure(0,weight=1);frame.columnconfigure(0,weight=1)
        self.gridview.bind('<<TreeviewSelect>>',self.select_record);self.gridview.bind('<Double-Button-1>',lambda e:self.edit_record(True));self.bind('<Destroy>',self.cleanup,add='+');self.timer=self.after(80,self.poll);self.controls()

    def worker(self):
        while True:
            item=self.tasks.get()
            if item is None:break
            generation,kind,callback=item
            try:self.results.put((generation,kind,True,callback()))
            except Exception as exc:self.results.put((generation,kind,False,str(exc)))
        self.session.disconnect()

    def controls(self):
        enabled=self.connected and not self.busy
        self.connect_button.configure(state='disabled' if self.busy else 'normal')
        for button in (self.refresh_button,self.add_button):button.configure(state='normal' if enabled and self.table_name else 'disabled')
        self.demo_button.configure(state='normal' if enabled and self.backend=='sqlite' else 'disabled')
        can_edit=enabled and self.selected_record is not None and any(c['pk'] for c in self.columns)
        self.edit_button.configure(state='normal' if can_edit else 'disabled');self.delete_button.configure(state='normal' if can_edit else 'disabled')
        self.tables_box.configure(state='readonly' if enabled else 'disabled')

    def submit(self,kind,callback):
        if self.closed:return False
        if self.busy:self.state.set('Attendi il completamento dell’operazione corrente.');return False
        self.busy=True;self.state.set('Operazione in corso…');self.controls();self.tasks.put((self.generation,kind,callback));return True

    def connect(self,password=None):
        if self.busy:return False
        self.connected=False;self.columns=[];self.rows=[];self.selected_record=None;self.gridview.delete(*self.gridview.get_children());self.tables_box.set('');self.tables_box['values']=[]
        config={'backend':self.backend,'database':self.database,'host':self.host,'port':self.port,'username':self.username,'password':password if password is not None else os.environ.get(self.password_env,'')}
        return self.submit('connect',lambda:self.session.connect(**config))

    def refresh(self):
        table=self.tables_box.get() or self.table_name;limit=self.limit
        if not table:return
        self.table_name=table
        def fetch():rows=self.session.fetch(table,limit);return self.session.column_info,rows
        return self.submit('rows',fetch)

    def create_demo(self):return self.submit('demo',self.session.create_demo)

    def select_record(self,event=None):
        sel=self.gridview.selection();self.selected_record=dict(self.rows[int(sel[0])]) if sel else None;self.controls()
        if sel:self.event_generate('<<RecordSelected>>',when='tail')

    def insert_record(self,values):
        values=dict(values);return self.submit('write',lambda:self.session.insert(values))
    def update_record(self,key,values):
        key=dict(key);values=dict(values);return self.submit('write',lambda:self.session.update(key,values))
    def delete_record(self,key):
        key=dict(key);return self.submit('write',lambda:self.session.delete(key))

    def poll(self):
        if self.closed:return
        try:
            while True:
                generation,kind,ok,data=self.results.get_nowait()
                if generation!=self.generation:continue
                self.busy=False
                if not ok:
                    self.last_error=data;self.state.set('Errore: '+data);self.controls();self.event_generate('<<DatabaseError>>',when='tail');continue
                if kind in ('connect','demo'):
                    self.connected=True;self.tables_box['values']=data
                    self.tables_box.set(self.table_name if self.table_name in data else (data[0] if data else ''));self.table_name=self.tables_box.get()
                    self.state.set('Connesso • scegli una tabella.' if data else 'Database vuoto. Puoi creare la tabella esempio.')
                    self.controls()
                    if kind=='connect':self.event_generate('<<DatabaseConnected>>',when='tail')
                    if data:self.refresh()
                elif kind=='rows':
                    self.columns,self.rows=data;self.selected_record=None;self.gridview.delete(*self.gridview.get_children());names=[c['name'] for c in self.columns];self.gridview['columns']=names
                    for c in self.columns:self.gridview.heading(c['name'],text=c['name']+(' 🔑' if c['pk'] else ''));self.gridview.column(c['name'],width=150,stretch=False)
                    for i,row in enumerate(self.rows):self.gridview.insert('','end',iid=str(i),values=['NULL' if row.get(k) is None else str(row[k]) for k in names])
                    self.state.set(f'{len(self.rows)} righe visualizzate • limite {self.limit}'+(' • Senza chiave primaria: modifica/eliminazione disabilitate.' if not any(c['pk'] for c in self.columns) else ''));self.controls();self.event_generate('<<DataLoaded>>',when='tail')
                elif kind=='write':self.event_generate('<<DataChanged>>',when='tail');self.refresh()
        except queue.Empty:pass
        self.timer=self.after(80,self.poll)

    def connection_dialog(self):
        if self.busy:return
        win=tk.Toplevel(self);win.title('Connessione database');win.transient(self.winfo_toplevel());vars={}
        fields=[('backend','Tipo',self.backend),('database','File SQLite / nome database',self.database),('host','Host (remoto)',self.host),('port','Porta (0 = predefinita)',self.port),('username','Utente (remoto)',self.username)]
        for i,(key,label,value) in enumerate(fields):
            ttk.Label(win,text=label).grid(row=i,column=0,padx=10,pady=7,sticky='w');vars[key]=tk.StringVar(value=value)
            control=ttk.Combobox(win,textvariable=vars[key],values=['sqlite','postgresql','mysql'],state='readonly') if key=='backend' else ttk.Entry(win,textvariable=vars[key],width=38)
            control.grid(row=i,column=1,padx=10,pady=7,sticky='ew')
        def browse():
            path=filedialog.asksaveasfilename(parent=win,defaultextension='.sqlite',filetypes=[('SQLite','*.sqlite *.db'),('Tutti','*')])
            if path:vars['database'].set(path)
        ttk.Button(win,text='Scegli file SQLite…',command=browse).grid(row=1,column=2,padx=5)
        password=tk.StringVar();ttk.Label(win,text='Password (non salvata)').grid(row=5,column=0,padx=10,pady=7);ttk.Entry(win,textvariable=password,show='•').grid(row=5,column=1,sticky='ew',padx=10)
        ttk.Label(win,text='SQLite: nessuna installazione. Remoto: SQLAlchemy + psycopg o PyMySQL.\nLa connessione usa l’ambiente Python dell’app. Password vuota: variabile '+self.password_env,wraplength=560).grid(row=6,column=0,columnspan=3,padx=10,pady=10)
        def apply():
            try:port=int(vars['port'].get());assert 0<=port<=65535
            except (ValueError,AssertionError):return messagebox.showerror('Porta','Inserisci una porta tra 0 e 65535.',parent=win)
            for key,var in vars.items():setattr(self,key,port if key=='port' else var.get())
            secret=password.get() or None;password.set('');win.destroy();self.connect(secret)
        ttk.Button(win,text='Connetti',command=apply).grid(row=7,column=1,pady=12)

    def edit_record(self,editing):
        if self.busy or not self.connected or not self.table_name:return
        if editing and (self.selected_record is None or not any(c['pk'] for c in self.columns)):return
        record=dict(self.selected_record) if editing else {};key={c['name']:record.get(c['name']) for c in self.columns if c['pk']}
        win=tk.Toplevel(self);win.title('Modifica record' if editing else 'Nuovo record');win.geometry('640x480');win.transient(self.winfo_toplevel())
        ttk.Label(win,text='Attiva i campi da scrivere. NULL è distinto dal testo vuoto. Le chiavi esistenti non si modificano.',wraplength=600,padding=10).pack(fill='x')
        canvas=tk.Canvas(win,highlightthickness=0);scroll=ttk.Scrollbar(win,command=canvas.yview);scroll.pack(side='right',fill='y');canvas.pack(fill='both',expand=True);canvas.configure(yscrollcommand=scroll.set);body=ttk.Frame(canvas);canvas.create_window(0,0,window=body,anchor='nw');body.bind('<Configure>',lambda e:canvas.configure(scrollregion=canvas.bbox('all')))
        fields=[]
        for i,c in enumerate(self.columns):
            if editing and c['pk']:continue
            name=c['name'];value=record.get(name);enabled=tk.BooleanVar(value=editing);is_null=tk.BooleanVar(value=editing and value is None);text=tk.StringVar(value='' if value is None else str(value))
            ttk.Checkbutton(body,text=name+' ('+c['type']+')',variable=enabled).grid(row=i,column=0,sticky='w',padx=8,pady=5);ttk.Entry(body,textvariable=text,width=25).grid(row=i,column=1,padx=5);ttk.Checkbutton(body,text='NULL',variable=is_null).grid(row=i,column=2,padx=5);fields.append((c,enabled,is_null,text))
        def save():
            try:
                values={c['name']:None if null.get() else parse_database_value(text.get(),c['type']) for c,enabled,null,text in fields if enabled.get()}
                # SQLite does not natively bind Decimal/date objects.
                if self.backend=='sqlite':values={k:str(v) if isinstance(v,(decimal.Decimal,datetime.date)) else v for k,v in values.items()}
            except (ValueError,decimal.InvalidOperation) as exc:return messagebox.showerror('Valore non valido',str(exc),parent=win)
            accepted=self.update_record(key,values) if editing else self.insert_record(values)
            if accepted:win.destroy()
        ttk.Button(win,text='Salva modifiche' if editing else 'Aggiungi record',command=save).pack(pady=10)

    def delete_selected(self):
        if self.selected_record is None:return
        key={c['name']:self.selected_record[c['name']] for c in self.columns if c['pk']}
        if key and messagebox.askyesno('Elimina record','Eliminare definitivamente la riga selezionata?\n'+str(key),parent=self):self.delete_record(key)

    def cleanup(self,event):
        if event.widget is self:
            self.closed=True;self.generation+=1;self.after_cancel(self.timer);self.tasks.put(None)
