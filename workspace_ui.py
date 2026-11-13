"""Component onboarding, multi-form management and persistent IDE appearance."""
from i18n import tr
import copy
import json
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
from pathlib import Path
from components import BUILTINS, descriptor, registry
from core import KINDS, identifier
from library_explorer import LibraryExplorer
from ux_theme import apply_theme, style_editor,editor_palette
from vb6_ui import CLASSIC

PRESETS = {
    tr('Classico VB6'): CLASSIC,
    tr('Chiaro'): {'background':'#f4f6fa','foreground':'#25324a','surface':'#ffffff','accent':'#2563eb','editor_bg':'#182234','editor_fg':'#dbe6f5','canvas':'#e8edf5'},
    tr('Scuro'): {'background':'#202938','foreground':'#e2e8f0','surface':'#2c384c','accent':'#467df0','editor_bg':'#111827','editor_fg':'#e2e8f0','canvas':'#151e2d'},
    tr('Seppia'): {'background':'#eee7da','foreground':'#453c31','surface':'#fff9ee','accent':'#916333','editor_bg':'#302a24','editor_fg':'#f1e4cf','canvas':'#ddd3c2'},
}

def duplicate_form(project, index):
    """Copy design with project-wide unique names; keep user code verbatim."""
    used={o['name'] for form in project['forms'] for o in [form]+form['widgets']}
    def unique(prefix):
        n=1
        while prefix+str(n) in used:n+=1
        name=prefix+str(n);used.add(name);return name
    form=copy.deepcopy(project['forms'][index])
    form['name']=unique('Form');form['title']+=tr(' (copia)')
    mapping={widget['name']:unique(widget['name']+'_copy') for widget in form['widgets']}
    previous=project['forms'][index]['name']
    for widget in form['widgets']:
        widget['name']=mapping[widget['name']]
        if widget.get('parent')==previous:widget['parent']=form['name']
        elif widget.get('parent') in mapping:widget['parent']=mapping[widget['parent']]
    return form

class WorkspaceMixin:
    def component_wizard(self):
        win=tk.Toplevel(self);win.title(tr('Aggiungi componente visuale'));win.geometry('650x490');win.transient(self)
        ttk.Label(win,text=tr('Crea un controllo riutilizzabile da una classe Tkinter.'),padding=12).pack(anchor='w')
        fields={}
        body=ttk.Frame(win,padding=12);body.pack(fill='x')
        for i,(key,label,value) in enumerate([('name',tr('Nome palette'),'MyWidget'),('module',tr('Modulo Python'),'customtkinter'),('class',tr('Classe widget'),'CTkButton'),('requirements',tr('Pacchetti PyPI (separati da virgola)'),'customtkinter'),('defaults',tr('Proprietà iniziali (JSON)'),'{"text": "Ciao"}')]):
            ttk.Label(body,text=label).grid(row=i,column=0,sticky='w',pady=7)
            fields[key]=tk.StringVar(value=value);ttk.Entry(body,textvariable=fields[key],width=40).grid(row=i,column=1,sticky='ew',padx=8)
        ttk.Label(win,text=tr('La classe deve accettare master e supportare place/bind.\nInstallare un pacchetto non genera automaticamente un widget.\nIl codice esterno viene caricato quando avvii il progetto.'),padding=12).pack(anchor='w')
        def add():
            try:
                name=fields['name'].get().strip()
                if not identifier(name) or name in KINDS or name in registry(self.project):raise ValueError(tr('Nome non valido o già presente'))
                data=descriptor({'module':fields['module'].get().strip(),'class':fields['class'].get().strip(),'requirements':[x.strip() for x in fields['requirements'].get().split(',') if x.strip()],'defaults':json.loads(fields['defaults'].get())})
                self.commit_code();self.checkpoint();self.project.setdefault('components',{})[name]=data;self.palette_query.set('');self.refresh();win.destroy()
                self.status.set(tr('Componente aggiunto: ')+name+tr(' • Librerie → Installa dipendenze progetto dopo averlo inserito nel form'))
            except Exception as exc:messagebox.showerror(tr('Componente'),str(exc),parent=win)
        ttk.Button(win,text=tr('Aggiungi alla palette'),command=add).pack(pady=8)
        ttk.Button(win,text=tr('Importa descrittore JSON…'),command=self.import_component).pack(pady=4)
        ttk.Button(win,text=tr('Esplora pacchetti online — PyPI'),command=lambda:LibraryExplorer(self)).pack(pady=4)

    def manage_forms(self):
        win=tk.Toplevel(self);win.title(tr('Gestione form'));win.geometry('650x440');win.transient(self)
        box=tk.Listbox(win,exportselection=False);box.pack(fill='both',expand=True,padx=12,pady=12)
        def fill(index=None):
            box.delete(0,'end')
            for i,f in enumerate(self.project['forms']):box.insert('end',f['name']+' — '+f['title']+(tr('  [principale]') if i==0 else ''))
            box.selection_set(self.form_index if index is None else index)
        def chosen():return box.curselection()[0] if box.curselection() else None
        def open_form():
            i=chosen()
            if i is None:return
            self.commit_code();self.form_index=i;self.selected=None;self.code_target=None;self.refresh();self.tabs.select(0)
        def duplicate():
            i=chosen()
            if i is None:return
            self.commit_code();self.checkpoint();f=duplicate_form(self.project,i)
            # User code can contain arbitrary references: preserve it verbatim.
            self.project['forms'].append(f);self.form_index=len(self.project['forms'])-1;self.selected=None;self.code_target=None;self.refresh();fill()
            messagebox.showinfo(tr('Form duplicato'),tr('Controlli rinominati. Il codice evento è conservato: aggiorna gli eventuali riferimenti ai controlli originali.'),parent=win)
        def remove():
            i=chosen()
            if i is None:return
            if i==0:return messagebox.showinfo(tr('Form principale'),tr('Il form principale non può essere eliminato.'),parent=win)
            if not messagebox.askyesno(tr('Elimina form'),tr('Eliminare il form e i suoi controlli? Aggiorna gli eventuali riferimenti nel codice.'),parent=win):return
            self.commit_code();self.checkpoint();self.project['forms'].pop(i);self.form_index=0;self.selected=None;self.code_target=None;self.refresh();fill()
        row=ttk.Frame(win,padding=10);row.pack(fill='x')
        def new():self.add_form();fill()
        for label,cmd in [(tr('Apri'),open_form),(tr('Nuovo'),new),(tr('Duplica'),duplicate),(tr('Elimina'),remove)]:ttk.Button(row,text=label,command=cmd).pack(side='left',padx=4)
        ttk.Label(win,text=tr('Nel codice evento: self.show("Form2") / self.hide("Form2").\nIl primo form è quello principale; chiuderlo termina l’app.'),padding=12).pack(anchor='w')
        box.bind('<Double-Button-1>',lambda e:open_form());fill()

    def apply_appearance(self):
        apply_theme(self)
        colors={**PRESETS[tr('Classico VB6')],**self.config_data.get('appearance',{})};style=ttk.Style(self)
        for klass in ('.','TFrame','TLabel','TNotebook','TNotebook.Tab','TPanedwindow'):
            style.configure(klass,background=colors['background'],foreground=colors['foreground'])
        for klass in ('Brand.TLabel','Title.TLabel','Muted.TLabel'):style.configure(klass,foreground=colors['foreground'],background=colors['background'])
        for klass in ('TEntry','TCombobox','Treeview'):style.configure(klass,fieldbackground=colors['surface'],background=colors['surface'],foreground=colors['foreground'])
        style.configure('TButton',background=colors['background'],foreground=colors['foreground'])
        style.configure('Caption.TFrame',background=colors['accent']);style.configure('Caption.TLabel',background=colors['accent'],foreground='white')
        style.configure('PropertyGroup.TLabel',background=colors['background'],foreground=colors['foreground'])
        style.configure('PropertyName.TLabel',background=colors['surface'],foreground=colors['foreground'])
        style.configure('TNotebook.Tab',background=colors['background'])
        style.map('TNotebook.Tab',background=[('selected',colors['surface'])],foreground=[('selected',colors['foreground'])])
        style.configure('Accent.TButton',background=colors['accent'])
        style.map('Accent.TButton',background=[('active',colors['accent']),('!disabled',colors['accent'])])
        style.map('Treeview',background=[('selected',colors['accent'])],foreground=[('selected','white')])
        self.configure(background=colors['background']);self.canvas.configure(bg=colors['canvas'])
        self.propbox.master.configure(bg=colors['background'])
        self.palette.configure(bg=colors['surface'],fg=colors['foreground'],selectbackground=colors['accent'],selectforeground='white')
        self.assist_list.configure(bg=colors['surface'],fg=colors['foreground'],selectbackground=colors['accent'],selectforeground='white')
        for widget in (self.code,self.generated,self.log):
            style_editor(widget);widget.configure(bg=colors['editor_bg'],fg=colors['editor_fg'],insertbackground=colors['editor_fg'],selectbackground=colors['accent'])
        for tag,color in editor_palette(colors['editor_bg']).items():self.code.tag_configure(tag,foreground=color)
        if hasattr(self,'docs_text'):self.docs_text.configure(bg=colors['surface'],fg=colors['foreground'])

    def appearance_settings(self):
        win=tk.Toplevel(self);win.title(tr('Aspetto ambiente di sviluppo'));win.transient(self)
        values={k:tk.StringVar(value=v) for k,v in {**PRESETS[tr('Classico VB6')],**self.config_data.get('appearance',{})}.items()}
        preset=tk.StringVar(value=tr('Classico VB6'));combo=ttk.Combobox(win,values=list(PRESETS),textvariable=preset,state='readonly');combo.grid(row=0,column=1,pady=10)
        combo.bind('<<ComboboxSelected>>',lambda e:[values[k].set(v) for k,v in PRESETS[preset.get()].items()])
        labels=[tr('Sfondo pannelli'),tr('Testo pannelli'),tr('Superficie controlli'),tr('Colore accento'),tr('Sfondo editor'),tr('Testo editor'),tr('Sfondo designer')]
        def choose(key):
            color=colorchooser.askcolor(values[key].get(),parent=win)[1]
            if color:values[key].set(color)
        for i,((key,var),label) in enumerate(zip(values.items(),labels),1):
            ttk.Label(win,text=label).grid(row=i,column=0,padx=12,pady=6,sticky='w');ttk.Entry(win,textvariable=var).grid(row=i,column=1);ttk.Button(win,text=tr('Scegli…'),command=lambda k=key:choose(k)).grid(row=i,column=2,padx=12)
        def save():
            try:
                data={k:v.get() for k,v in values.items()}
                for color in data.values():self.winfo_rgb(color)
                updated={**self.config_data,'appearance':data}
                (Path.home()/'.visualtkstudio.json').write_text(json.dumps(updated,indent=2),encoding='utf-8');self.config_data=updated;self.apply_appearance();win.destroy()
            except Exception as exc:messagebox.showerror(tr('Aspetto'),str(exc),parent=win)
        ttk.Button(win,text=tr('Salva e applica'),command=save).grid(row=8,column=1,pady=16)
