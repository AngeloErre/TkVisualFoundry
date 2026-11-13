"""Optional productivity panels. External I/O runs only after explicit operations."""
from i18n import tr
from service_backends import atomic_output,env_value,safe_error,excel_open,excel_save,pdf_open,pdf_extract,pdf_merge,midi_ports,midi_play,open_document,print_document,llm_call,DriveStorage,S3Storage,WebDAVStorage
import tkinter as tk
from tkinter import ttk,filedialog,messagebox,simpledialog
from tkinter.scrolledtext import ScrolledText
from pathlib import Path
import queue
import threading

class _ServicePanel(tk.Frame):
    def __init__(self,master,**kw):
        super().__init__(master,**kw);self.busy=False;self.error='';self._closed=False;self._tasks=queue.Queue();self._secret_names=[];self._secret_values=[]
        self.status=tk.StringVar(value=tr('Pronto'));ttk.Label(self,textvariable=self.status,wraplength=650).pack(side='bottom',fill='x',padx=4,pady=4);self._timer=self.after(80,self._poll)
    def _fail(self,error):
        self.error=safe_error(error,self._secret_names,self._secret_values);self.status.set(tr('Errore: ')+self.error);self.event_generate('<<ServiceError>>',when='tail')
    def _start(self,work,done=None,event=None):
        if self.busy:self.status.set(tr('Attendi il completamento dell’operazione corrente.'));return False
        self.busy=True;self.error='';self.status.set(tr('Operazione in corso…'))
        def run():
            try:self._tasks.put(('done',work(),done,event))
            except Exception as exc:self._tasks.put(('error',safe_error(exc,self._secret_names,self._secret_values),None,None))
        threading.Thread(target=run,daemon=True).start();return True
    def _poll(self):
        if self._closed:return
        try:
            while True:
                state,result,done,event=self._tasks.get_nowait()
                if state=='event':self.event_generate(result,when='tail');continue
                self.busy=False
                if state=='error':self._fail(result);continue
                self.status.set(tr('Operazione terminata'))
                try:
                    if done:done(result)
                    if event:self.event_generate(event,when='tail')
                except Exception as exc:self._fail(exc)
        except queue.Empty:pass
        self._timer=self.after(80,self._poll)
    def destroy(self):
        self._closed=True
        if hasattr(self,'_stop'):self._stop.set()
        try:self.after_cancel(self._timer)
        except tk.TclError:pass
        super().destroy()


class MIDIPlayer(_ServicePanel):
    def __init__(self,master,source='',port='',**kw):
        super().__init__(master,**kw);self.source=source;self._stop=threading.Event();self._pause=threading.Event();self.port_var=tk.StringVar(value=port)
        row=ttk.Frame(self);row.pack(fill='x');ttk.Button(row,text=tr('Apri MIDI…'),command=self.choose).pack(side='left');ttk.Button(row,text=tr('Uscite MIDI'),command=self.refresh_ports).pack(side='left');self.ports=ttk.Combobox(row,textvariable=self.port_var,state='readonly');self.ports.pack(side='left',fill='x',expand=True)
        row=ttk.Frame(self);row.pack(fill='x');ttk.Button(row,text=tr('Riproduci'),command=self.play).pack(side='left');ttk.Button(row,text=tr('Pausa / riprendi'),command=self.pause).pack(side='left');ttk.Button(row,text='Stop',command=self.stop).pack(side='left')
        ttk.Label(self,text=tr('Seleziona un’uscita MIDI collegata a un sintetizzatore. Nessun sintetizzatore audio è incluso.'),wraplength=600).pack(fill='x',padx=5,pady=12)
    def choose(self):
        path=filedialog.askopenfilename(parent=self,filetypes=[('MIDI','*.mid *.midi')])
        if path:self.source=path;self.status.set(path)
    def refresh_ports(self):
        def ready(ports):
            self.ports.configure(values=ports)
            if ports and self.port_var.get() not in ports:self.port_var.set(ports[0])
            self.status.set(tr('Uscite trovate: ')+str(len(ports)))
        return self._start(midi_ports,ready)
    def play(self,path=None):
        if path:self.source=path
        if not self.source:self._fail(tr('Scegli prima un file.'));return False
        if self.busy:return False
        self._stop.clear();self._pause.clear();source=self.source;port=self.port_var.get()
        return self._start(lambda:midi_play(source,port,self._stop,self._pause,lambda:self._tasks.put(('event','<<MidiStarted>>',None,None))),event='<<MidiFinished>>')
    def pause(self):
        if self._pause.is_set():self._pause.clear()
        else:self._pause.set()
    def stop(self):self._stop.set();self._pause.clear()


class ExcelWorkbook(_ServicePanel):
    def __init__(self,master,source='',sheet='',preview_rows=500,**kw):
        super().__init__(master,**kw);self.path=source;self.sheet_name=sheet;self.book=None;self.rows=[];self.preview_rows=max(1,min(2000,int(preview_rows)));self.sheet_var=tk.StringVar()
        row=ttk.Frame(self);row.pack(fill='x')
        for label,command in [('Apri Excel…',self.choose),('Nuovo',self.create),('Salva con nome…',self.save_dialog),('Modifica cella…',self.edit_cell)]:ttk.Button(row,text=tr(label),command=command).pack(side='left')
        self.sheets=ttk.Combobox(self,textvariable=self.sheet_var,state='readonly');self.sheets.pack(fill='x');self.sheets.bind('<<ComboboxSelected>>',lambda e:self._display())
        area=ttk.Frame(self);area.pack(fill='both',expand=True);scroll=ttk.Scrollbar(area);scroll.pack(side='right',fill='y');self.table=ttk.Treeview(area,show='headings',yscrollcommand=scroll.set);horizontal=ttk.Scrollbar(area,orient='horizontal',command=self.table.xview);horizontal.pack(side='bottom',fill='x');self.table.configure(xscrollcommand=horizontal.set);self.table.pack(fill='both',expand=True);scroll.configure(command=self.table.yview);self.table.bind('<Double-1>',lambda e:self.edit_cell())
    def choose(self):
        path=filedialog.askopenfilename(parent=self,filetypes=[('Excel','*.xlsx *.xlsm')])
        if path:self.load(path)
    def load(self,path):
        if self.busy:return False
        def ready(book):self.book=book;self.path=str(path);self.sheets.configure(values=book.sheetnames);self.sheet_var.set(self.sheet_name if self.sheet_name in book.sheetnames else book.sheetnames[0]);self._display()
        return self._start(lambda:excel_open(path),ready,'<<ExcelLoaded>>')
    def create(self,headers=None,rows=None):
        def work():
            from openpyxl import Workbook
            book=Workbook()
            if headers:book.active.append(list(headers))
            for row in rows or []:book.active.append(list(row))
            return book
        def ready(book):self.book=book;self.path='';self.sheets.configure(values=book.sheetnames);self.sheet_var.set(book.sheetnames[0]);self._display()
        return self._start(work,ready,'<<ExcelLoaded>>')
    def _display(self):
        if self.book is None or self.busy:return
        sheet=self.book[self.sheet_var.get()];self.table.delete(*self.table.get_children());columns=list(range(1,min(50,sheet.max_column)+1));self.table.configure(columns=columns)
        from openpyxl.utils import get_column_letter
        for column in columns:self.table.heading(column,text=get_column_letter(column));self.table.column(column,width=100,minwidth=45)
        self.rows=[list(row) for row in sheet.iter_rows(max_row=min(self.preview_rows,sheet.max_row),max_col=len(columns),values_only=True)]
        for index,row in enumerate(self.rows,1):self.table.insert('','end',iid=str(index),values=['' if value is None else str(value) for value in row])
    def get_data(self):return [list(row) for row in self.rows]
    def set_cell(self,row,column,value):
        if self.book is None or self.busy:raise ValueError(tr('Apri un documento e attendi la fine dell’operazione.'))
        if not 1<=int(row)<=1048576 or not 1<=int(column)<=16384:raise ValueError('Invalid Excel cell coordinates')
        self.book[self.sheet_var.get()].cell(int(row),int(column),value);self._display();self.event_generate('<<ExcelChanged>>',when='tail')
    def add_sheet(self,name):
        if self.book is None or self.busy:raise ValueError(tr('Apri un documento e attendi la fine dell’operazione.'))
        self.book.create_sheet(name);self.sheets.configure(values=self.book.sheetnames);self.sheet_var.set(name);self._display();self.event_generate('<<ExcelChanged>>',when='tail')
    def edit_cell(self):
        if self.book is None or self.busy:return
        row=simpledialog.askinteger(tr('Cella Excel'),tr('Riga (da 1):'),parent=self,minvalue=1)
        if row is None:return
        column=simpledialog.askinteger(tr('Cella Excel'),tr('Colonna (da 1):'),parent=self,minvalue=1)
        if column is None:return
        value=simpledialog.askstring(tr('Cella Excel'),tr('Valore (JSON per numeri, booleani o null; altrimenti testo):'),parent=self)
        if value is None:return
        import json
        try:value=json.loads(value)
        except ValueError:pass
        try:self.set_cell(row,column,value)
        except Exception as exc:self._fail(exc)
    def save_dialog(self):
        if self.book is None:return
        suffix='.xlsm' if self.book.vba_archive is not None else '.xlsx';path=filedialog.asksaveasfilename(parent=self,defaultextension=suffix,filetypes=[('Excel','*'+suffix)])
        if path:self.save_as(path)
    def save_as(self,path):
        if self.book is None:self._fail(tr('Scegli prima un file.'));return False
        def ready(result):self.path=result;self._display()
        return self._start(lambda:excel_save(self.book,path),ready,'<<ExcelSaved>>')


class PDFDocument(_ServicePanel):
    def __init__(self,master,source='',**kw):
        super().__init__(master,**kw);self.path=source;self.reader=None;self.page_count=0;self.text='';self.last_path=''
        row=ttk.Frame(self);row.pack(fill='x')
        for label,command in [('Apri PDF…',self.choose),('Estrai testo',self.extract_text),('Unisci PDF…',self.merge_dialog),('Estrai pagine…',self.pages_dialog),('Salva testo…',self.text_dialog)]:ttk.Button(row,text=tr(label),command=command).pack(side='left')
        self.preview=ScrolledText(self,wrap='word',height=7);self.preview.pack(fill='both',expand=True)
    def _text(self,value):self.text=value;self.preview.configure(state='normal');self.preview.delete('1.0','end');self.preview.insert('1.0',value);self.preview.configure(state='disabled')
    def choose(self):
        path=filedialog.askopenfilename(parent=self,filetypes=[('PDF','*.pdf')])
        if path:
            password=simpledialog.askstring('PDF',tr('Password facoltativa (lascia vuoto se non cifrato):'),show='*',parent=self)
            if password is not None:self.load(path,password)
    def load(self,path,password=None):
        def work():
            reader=pdf_open(path,password);return reader,(reader.pages[0].extract_text() or '') if reader.pages else ''
        def ready(result):self.reader,text=result;self.path=str(path);self.page_count=len(self.reader.pages);self._text(text);self.status.set(tr('Pagine: ')+str(self.page_count)+tr(' • anteprima del testo della prima pagina'))
        return self._start(work,ready,'<<PDFLoaded>>')
    def extract_text(self):
        if self.reader is None:self._fail(tr('Scegli prima un file.'));return False
        return self._start(lambda:'\n\n'.join(page.extract_text() or '' for page in self.reader.pages),self._text,'<<PDFTextReady>>')
    def merge(self,paths,destination):
        paths=list(paths)
        def ready(path):self.last_path=path
        return self._start(lambda:pdf_merge(paths,destination),ready,'<<PDFSaved>>')
    def merge_dialog(self):
        paths=filedialog.askopenfilenames(parent=self,filetypes=[('PDF','*.pdf')])
        if not paths:return
        target=filedialog.asksaveasfilename(parent=self,defaultextension='.pdf')
        if target:self.merge(paths,target)
    def extract_pages(self,indexes,destination):
        indexes=list(indexes)
        if self.reader is None:self._fail(tr('Scegli prima un file.'));return False
        def ready(path):self.last_path=path
        return self._start(lambda:pdf_extract(self.reader,indexes,destination),ready,'<<PDFSaved>>')
    def pages_dialog(self):
        if self.reader is None:return
        value=simpledialog.askstring('PDF',tr('Pagine da estrarre, separate da virgola (da 1):'),parent=self)
        if not value:return
        try:pages=[int(v.strip())-1 for v in value.split(',')]
        except ValueError:return self._fail('Invalid page numbers')
        target=filedialog.asksaveasfilename(parent=self,defaultextension='.pdf')
        if target:self.extract_pages(pages,target)
    def save_text(self,path):
        if self.reader is None:self._fail(tr('Scegli prima un file.'));return False
        def work():
            text='\n\n'.join(page.extract_text() or '' for page in self.reader.pages)
            return atomic_output(path,lambda target:target.write_text(text,encoding='utf-8'))
        return self._start(work,lambda result:setattr(self,'last_path',result),'<<PDFSaved>>')
    def text_dialog(self):
        path=filedialog.asksaveasfilename(parent=self,defaultextension='.txt')
        if path:self.save_text(path)


class PrintDocument(_ServicePanel):
    def __init__(self,master,source='',printer='',copies=1,**kw):
        super().__init__(master,**kw);self.path_var=tk.StringVar(value=source);self.printer_var=tk.StringVar(value=printer);self.copies_var=tk.IntVar(value=copies);self.print_job=''
        row=ttk.Frame(self);row.pack(fill='x');ttk.Entry(row,textvariable=self.path_var).pack(side='left',fill='x',expand=True);ttk.Button(row,text=tr('Scegli…'),command=self.choose).pack(side='right')
        row=ttk.Frame(self);row.pack(fill='x');ttk.Label(row,text=tr('Stampante (vuoto = predefinita):')).pack(side='left');ttk.Entry(row,textvariable=self.printer_var,width=18).pack(side='left');ttk.Label(row,text=tr('Copie:')).pack(side='left');ttk.Spinbox(row,from_=1,to=100,textvariable=self.copies_var,width=5).pack(side='left')
        row=ttk.Frame(self);row.pack(fill='x');ttk.Button(row,text=tr('Apri anteprima / dialogo di stampa'),command=self.preview).pack(side='left');ttk.Button(row,text=tr('Invia alla stampa…'),command=self.print_file).pack(side='left')
        ttk.Label(self,text=tr('Per il dialogo nativo apri il documento e usa Stampa nell’app associata. Su Windows invio diretto solo alla stampante predefinita, una copia.'),wraplength=600).pack(fill='x',pady=10)
    def choose(self):
        path=filedialog.askopenfilename(parent=self)
        if path:self.path_var.set(path)
    def preview(self,path=None):
        if path:self.path_var.set(path)
        try:return open_document(self.path_var.get())
        except Exception as exc:self._fail(exc)
    def print_file(self,path=None,confirm=True):
        if path:self.path_var.set(path)
        source=self.path_var.get();printer=self.printer_var.get();copies=self.copies_var.get()
        if not source:self._fail(tr('Scegli prima un file.'));return False
        if confirm and not messagebox.askyesno(tr('Stampa'),tr('Inviare questo documento alla stampa?')+'\n'+source,parent=self):return False
        def ready(result):self.print_job=result;self.status.set(tr('Richiesta affidata al sistema di stampa: ')+result)
        return self._start(lambda:print_document(source,printer,copies),ready,'<<PrintSubmitted>>')


class CloudStorage(_ServicePanel):
    def __init__(self,master,provider='drive',folder='root',bucket='',auth_mode='desktop',scope='app',client_env='GOOGLE_OAUTH_CLIENT_FILE',token_env='GOOGLE_TOKEN_FILE',endpoint_env='S3_ENDPOINT_URL',url_env='WEBDAV_URL',user_env='WEBDAV_USER',password_env='WEBDAV_PASSWORD',**kw):
        super().__init__(master,**kw);self.provider=provider;self.folder_var=tk.StringVar(value=folder);self.bucket=bucket;self.auth_mode=auth_mode;self.scope=scope;self.client_env=client_env;self.token_env=token_env;self.endpoint_env=endpoint_env;self.url_env=url_env;self.user_env=user_env;self.password_env=password_env;self.client=None;self._session_credentials={};self.files=[];self.last_transfer=None;self._secret_names=[password_env,user_env,'AWS_SECRET_ACCESS_KEY','AWS_ACCESS_KEY_ID','AWS_SESSION_TOKEN']
        row=ttk.Frame(self);row.pack(fill='x');ttk.Label(row,text=provider).pack(side='left');ttk.Button(row,text=tr('Credenziali…'),command=self.credentials_dialog).pack(side='left');ttk.Button(row,text=tr('Connetti…'),command=self.connect).pack(side='left');ttk.Button(row,text=tr('Elenca file'),command=self.list_files).pack(side='left');ttk.Button(row,text=tr('Carica file…'),command=self.upload).pack(side='left');ttk.Button(row,text=tr('Scarica file…'),command=self.download).pack(side='left')
        ttk.Entry(self,textvariable=self.folder_var).pack(fill='x');self.table=ttk.Treeview(self,columns=('name','id'),show='headings');self.table.heading('name',text=tr('Nome'));self.table.heading('id',text='ID / Key');self.table.pack(fill='both',expand=True)
    def credentials_dialog(self):
        if self.busy:return
        if self.provider=='drive':
            path=filedialog.askopenfilename(parent=self,title=tr('Client OAuth Desktop di Google (JSON)'),filetypes=[('JSON','*.json')])
            if path:self._session_credentials={'client_file':path};self.status.set(tr('Credenziali solo per questa sessione.'))
            return
        win=tk.Toplevel(self);win.title(tr('Credenziali solo per questa sessione.'));fields={}
        keys=['access_key','secret_key','session_token','endpoint'] if self.provider=='s3' else ['url','username','password']
        for index,key in enumerate(keys):
            ttk.Label(win,text=key).grid(row=index,column=0,padx=8,pady=6);var=tk.StringVar(value=self._session_credentials.get(key,''));fields[key]=var;ttk.Entry(win,textvariable=var,show='*' if key in ('secret_key','session_token','password') else '',width=42).grid(row=index,column=1,padx=8)
        def apply():
            self._session_credentials={key:var.get() for key,var in fields.items() if var.get()};self._secret_values=list(self._session_credentials.values());win.destroy()
        ttk.Button(win,text=tr('Usa per questa sessione'),command=apply).grid(row=len(keys),column=1,pady=10)
    def connect(self):
        provider=self.provider;credentials=dict(self._session_credentials)
        def work():
            if provider=='drive':return DriveStorage(self.client_env,self.token_env,self.auth_mode,self.scope,**credentials)
            if provider=='s3':return S3Storage(self.bucket,self.endpoint_env,**credentials)
            if provider=='webdav':return WebDAVStorage(self.url_env,self.user_env,self.password_env,**credentials)
            raise ValueError('Provider must be drive, s3 or webdav')
        return self._start(work,lambda client:setattr(self,'client',client),'<<CloudConnected>>')
    def _require_client(self):
        if self.client is None:self._fail(tr('Connetti prima il servizio.'));return False
        return True
    def list_files(self,folder=None):
        if not self._require_client():return False
        if folder is not None:self.folder_var.set(folder)
        current=self.folder_var.get()
        def ready(files):
            self.files=files;self.table.delete(*self.table.get_children())
            for index,file in enumerate(files):self.table.insert('','end',iid=str(index),values=(file.get('name',''),file['id']))
        return self._start(lambda:self.client.list_files(current),ready,'<<CloudListed>>')
    def upload(self,path=None,folder=None):
        if not self._require_client():return False
        path=path or filedialog.askopenfilename(parent=self)
        if not path:return False
        current=self.folder_var.get() if folder is None else folder
        return self._start(lambda:self.client.upload(path,current),lambda result:setattr(self,'last_transfer',result),'<<CloudTransferred>>')
    def download(self,file_id=None,destination=None):
        if not self._require_client():return False
        name='download.bin'
        if file_id is None:
            selected=self.table.selection()
            if not selected:return False
            item=self.files[int(selected[0])];file_id=item['id'];name=Path(item.get('name','download.bin')).name
            if item.get('mimeType','').startswith('application/vnd.google-apps.') and not name.lower().endswith('.pdf'):name+='.pdf'
        destination=destination or filedialog.asksaveasfilename(parent=self,initialfile=name)
        if not destination:return False
        return self._start(lambda:self.client.download(file_id,destination),lambda result:setattr(self,'last_transfer',result),'<<CloudTransferred>>')


class LLMClient(_ServicePanel):
    KEYS={'openai':'OPENAI_API_KEY','anthropic':'ANTHROPIC_API_KEY','gemini':'GEMINI_API_KEY'}
    def __init__(self,master,provider='openai',model='',api_key_env='',max_tokens=1024,**kw):
        super().__init__(master,**kw);self.provider=provider;self.api_key_env=api_key_env or self.KEYS.get(provider,'OPENAI_API_KEY');self.max_tokens=int(max_tokens);self.response='';self.usage={};self.last_result={};self._session_key=None;self._secret_names=list(self.KEYS.values())+[self.api_key_env];self.model_var=tk.StringVar(value=model)
        row=ttk.Frame(self);row.pack(fill='x');ttk.Label(row,text=provider).pack(side='left');ttk.Button(row,text=tr('Chiave API…'),command=self.key_dialog).pack(side='left');self.models=ttk.Combobox(row,textvariable=self.model_var);self.models.pack(side='left',fill='x',expand=True);ttk.Button(row,text=tr('Modelli'),command=self.list_models).pack(side='left');ttk.Button(row,text=tr('Invia'),command=self.send).pack(side='right')
        ttk.Label(self,text=tr('API ufficiali: chiave nella variabile ambiente configurata. Puoi anche usare Chiave API per la sola sessione. Il testo viene inviato soltanto con Invia.'),wraplength=650).pack(fill='x')
        self.prompt=ScrolledText(self,height=4,wrap='word');self.prompt.pack(fill='x');self.output=ScrolledText(self,height=7,wrap='word');self.output.pack(fill='both',expand=True)
    def key_dialog(self):
        if self.busy:return
        key=simpledialog.askstring(tr('Chiave API…'),tr('Chiave API solo per questa sessione (non viene salvata):'),show='*',parent=self)
        if key:self._session_key=key.strip();self._secret_values=[self._session_key];self.status.set(tr('Credenziali solo per questa sessione.'))
    def list_models(self):
        provider=self.provider;env=self.api_key_env
        return self._start(lambda:llm_call(provider,'','',env,self.max_tokens,models=True,api_key=self._session_key),lambda names:self.models.configure(values=names),'<<LLMModelsReady>>')
    def send(self,prompt=None):
        text=self.prompt.get('1.0','end-1c') if prompt is None else prompt;provider=self.provider;model=self.model_var.get();env=self.api_key_env;limit=self.max_tokens
        def ready(result):
            self.last_result=result;self.response=result['text'];self.usage=result['usage'];self.output.delete('1.0','end');self.output.insert('1.0',self.response);self.status.set(result['provider']+' • '+result['model'])
        return self._start(lambda:llm_call(provider,model,text,env,limit,api_key=self._session_key),ready,'<<LLMResponse>>')
