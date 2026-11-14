"""New-project chooser. Cancel leaves the existing project untouched."""
import tkinter as tk
from tkinter import ttk,messagebox
from project_templates import catalog,instantiate
from components import requirements
from i18n import tr


class TemplateMixin:
    def choose_new_project(self):
        existing=getattr(self,'template_window',None)
        if existing is not None and existing.winfo_exists():existing.lift();return
        win=tk.Toplevel(self);self.template_window=win;win.title(tr('Nuovo progetto • scegli un modello'));win.geometry('780x470');win.minsize(650,400);win.transient(self)
        ttk.Label(win,text=tr('Da quale progetto vuoi partire?'),padding=12,style='Title.TLabel').pack(fill='x')
        area=ttk.Frame(win,padding=10);area.pack(fill='both',expand=True);area.columnconfigure(1,weight=1);area.rowconfigure(0,weight=1)
        entries=catalog();choices=tk.Listbox(area,exportselection=False,width=30);choices.grid(row=0,column=0,sticky='nsew',padx=(0,12))
        for entry in entries:choices.insert('end',entry['title'])
        detail=ttk.Frame(area);detail.grid(row=0,column=1,sticky='nsew');title=tk.StringVar();description=tk.StringVar();packages=tk.StringVar()
        ttk.Label(detail,textvariable=title,style='Title.TLabel',wraplength=370).pack(fill='x',pady=6)
        ttk.Label(detail,textvariable=description,wraplength=370,justify='left').pack(fill='x',pady=8)
        ttk.Label(detail,textvariable=packages,wraplength=370,justify='left').pack(fill='x',pady=8)
        ttk.Label(detail,text=tr('I modelli pronti hanno codice commentato in inglese e controlli modificabili nel designer. Non vengono eseguiti durante la scelta.'),wraplength=370,justify='left').pack(fill='x',pady=8)
        actions=ttk.Frame(win,padding=10);actions.pack(fill='x');ttk.Button(actions,text=tr('Annulla'),command=win.destroy).pack(side='right')
        candidate=[None]
        def select(event=None):
            index=choices.curselection()
            if not index:return
            entry=entries[index[0]];title.set(entry['category']+' • '+entry['title']);description.set(entry['description'])
            try:
                candidate[0]=instantiate(entry['id']);specs=requirements(candidate[0]);packages.set(tr('Pacchetti richiesti: ')+(', '.join(specs) if specs else tr('Nessun PIP aggiuntivo: solo libreria standard.')));create.configure(state='normal')
            except Exception as exc:candidate[0]=None;packages.set(str(exc));create.configure(state='disabled')
        def create_project(event=None):
            if candidate[0] is None:return
            project=candidate[0];win.destroy();self.new_from_template(project)
        create=ttk.Button(actions,text=tr('Crea progetto'),command=create_project);create.pack(side='right',padx=8)
        choices.bind('<<ListboxSelect>>',select);choices.bind('<Double-Button-1>',create_project);choices.bind('<Return>',create_project);win.bind('<Escape>',lambda e:win.destroy())
        choices.selection_set(0);select();win.grab_set();choices.focus_set()
