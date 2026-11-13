"""IDE setup for optional services. Only names and settings enter project JSON."""
import copy
from pathlib import Path
import tkinter as tk
from tkinter import ttk,messagebox,filedialog
from i18n import tr
from productivity_specs import PRODUCTIVITY_COMPONENTS,validate_productivity,productivity_requirements

class ProductivityMixin:
    def productivity_setup(self):
        obj=self.selected
        if not obj or obj['kind'] not in PRODUCTIVITY_COMPONENTS:return
        kind=obj['kind'];descriptor=PRODUCTIVITY_COMPONENTS[kind];props={**descriptor['defaults'],**obj.get('props',{})}
        win=tk.Toplevel(self);win.title(tr('Configura servizio')+' • '+kind);win.geometry('850x650');win.transient(self)
        ttk.Label(win,text=descriptor['description'],wraplength=800,padding=12).pack(anchor='w')
        area=ttk.Frame(win);area.pack(fill='both',expand=True);canvas=tk.Canvas(area,highlightthickness=0);scroll=ttk.Scrollbar(area,command=canvas.yview);scroll.pack(side='right',fill='y');canvas.pack(fill='both',expand=True);canvas.configure(yscrollcommand=scroll.set);body=ttk.Frame(canvas,padding=12);canvas.create_window(0,0,window=body,anchor='nw');body.bind('<Configure>',lambda e:canvas.configure(scrollregion=canvas.bbox('all')));fields={};controls={}
        labels={'source':tr('File iniziale (facoltativo)'),'port':tr('Nome uscita MIDI'),'sheet':tr('Foglio iniziale'),'preview_rows':tr('Righe in anteprima'),'provider':tr('Servizio'),'model':tr('ID modello (o selezionalo nell’app)'),'api_key_env':tr('Variabile ambiente della chiave API'),'max_tokens':tr('Limite token di output'),'folder':tr('ID cartella Drive / prefisso S3-WebDAV'),'bucket':tr('Bucket S3'),'auth_mode':tr('Autenticazione Drive'),'scope':tr('Accesso Drive: app o tutti i file'),'client_env':tr('Variabile con percorso JSON OAuth'),'token_env':tr('Variabile con percorso token esterno'),'endpoint_env':tr('Variabile con endpoint S3/MinIO'),'url_env':tr('Variabile con URL WebDAV'),'user_env':tr('Variabile con utente WebDAV'),'password_env':tr('Variabile con password WebDAV'),'printer':tr('Stampante (vuoto = predefinita):'),'copies':tr('Copie:')}
        for index,(key,value) in enumerate(props.items()):
            ttk.Label(body,text=labels.get(key,key)).grid(row=index,column=0,sticky='w',pady=6);var=tk.StringVar(value=str(value));fields[key]=var
            values={'provider':['openai','anthropic','gemini'] if kind=='LLMClient' else ['drive','s3','webdav'],'auth_mode':['desktop','adc'],'scope':['app','all']}.get(key)
            control=ttk.Combobox(body,textvariable=var,values=values,state='readonly',width=40) if values else ttk.Entry(body,textvariable=var,width=43);control.grid(row=index,column=1,padx=10);controls[key]=control
            if key=='source':
                def browse():
                    path=filedialog.askopenfilename(parent=win)
                    if path:
                        root=self.path.resolve().parent if self.path else None;selected=Path(path).resolve();fields['source'].set(selected.relative_to(root).as_posix() if root and selected.is_relative_to(root) else str(selected))
                ttk.Button(body,text=tr('Sfoglia…'),command=browse).grid(row=index,column=2)
        notes={
            'MIDIPlayer':tr('MIDI richiede una porta e un sintetizzatore esterno o virtuale. Il componente non include strumenti audio.'),
            'ExcelWorkbook':tr('XLSX e XLSM: formule conservate, non calcolate. Salva una copia; elementi Excel particolari possono non essere preservati.'),
            'PDFDocument':tr('Funzioni PDF testuali e pagine; niente OCR o rendering grafico. I PDF cifrati richiedono la password in esecuzione.'),
            'PrintDocument':tr('Anteprima e dialogo tramite l’app associata. Invio diretto con conferma; su Windows solo stampante predefinita e una copia.'),
            'CloudStorage':tr('Drive: abilita Drive API e crea un client OAuth Desktop. app limita l’accesso ai file dell’app; all richiede consenso più ampio. S3/WebDAV richiedono il proprio account. Credenziali inseribili anche solo in esecuzione.'),
            'LLMClient':tr('Serve un account API del fornitore, con accesso e fatturazione propri. L’abbonamento ChatGPT/Claude/Gemini non imposta le API. In esecuzione usa Chiave API oppure la variabile ambiente. Nessuna richiesta a pagamento durante il design.'),
        }
        note=tk.StringVar(value=notes[kind]);ttk.Label(win,textvariable=note,wraplength=800,padding=12).pack(fill='x')
        def change(event=None):
            if kind=='LLMClient':fields['api_key_env'].set({'openai':'OPENAI_API_KEY','anthropic':'ANTHROPIC_API_KEY','gemini':'GEMINI_API_KEY'}[fields['provider'].get()]);fields['model'].set('')
            if kind=='CloudStorage':fields['folder'].set('root' if fields['provider'].get()=='drive' else '')
        if 'provider' in controls:controls['provider'].bind('<<ComboboxSelected>>',change)
        def save(prepare=False):
            try:
                updated={key:var.get() for key,var in fields.items()}
                for key in ('preview_rows','copies','max_tokens'):
                    if key in updated:updated[key]=int(updated[key])
                validate_productivity(kind,updated);self.commit_code();self.checkpoint();obj['props']=updated;self.refresh();win.destroy()
                if prepare:self.open_dependencies(kind,updated,auto_install=True)
            except Exception as exc:messagebox.showerror(tr('Configura servizio'),str(exc),parent=win)
        row=ttk.Frame(win,padding=12);row.pack(fill='x');ttk.Button(row,text=tr('Salva configurazione'),command=save).pack(side='right');ttk.Button(row,text=tr('Salva e prepara dipendenze…'),command=lambda:save(True)).pack(side='right',padx=8)
        ttk.Label(win,text=tr('Non inserire segreti nei campi: usa nomi di variabili ambiente. Le credenziali di sessione si inseriscono solo nell’app in esecuzione.'),wraplength=800,padding=8).pack(fill='x')
