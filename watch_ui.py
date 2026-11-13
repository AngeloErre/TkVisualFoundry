"""Read-only project watches backed by current-session inspector samples."""
import json
import tkinter as tk
from tkinter import ttk,messagebox
from i18n import tr
from watch_values import parse_watch,resolve_watch

class WatchMixin:
    def build_watches(self):
        self.watch_page=ttk.Frame(self.tabs);self.tabs.add(self.watch_page,text=tr('Watch / Osserva'));self.watch_input=tk.StringVar();self.watch_previous={};self.watch_session=None
        bar=ttk.Frame(self.watch_page,padding=6);bar.pack(fill='x')
        entry=ttk.Entry(bar,textvariable=self.watch_input);entry.pack(side='left',fill='x',expand=True);entry.bind('<Return>',lambda e:self.add_watch())
        ttk.Button(bar,text=tr('Aggiungi Watch'),command=self.add_watch).pack(side='left',padx=4);ttk.Button(bar,text=tr('Rimuovi selezionata'),command=self.remove_watch).pack(side='left')
        ttk.Label(self.watch_page,text=tr("Percorsi: self.contatore, self.samples[0], config['porta'], globals.nome, locals.nome. Nessuna chiamata o espressione aritmetica."),padding=6,wraplength=900).pack(fill='x')
        self.watch_status=tk.StringVar();ttk.Label(self.watch_page,textvariable=self.watch_status,padding=6).pack(fill='x')
        area=ttk.Frame(self.watch_page);area.pack(fill='both',expand=True)
        self.watch_tree=ttk.Treeview(area,columns=('type','value','scope'),show='tree headings',selectmode='browse')
        for key,label,width in [('#0',tr('Percorso'),230),('type',tr('Tipo'),100),('value',tr('Valore'),300),('scope',tr('Ambito'),250)]:self.watch_tree.heading(key,text=label);self.watch_tree.column(key,width=width)
        scroll=ttk.Scrollbar(area,command=self.watch_tree.yview);scroll.pack(side='right',fill='y');self.watch_tree.configure(yscrollcommand=scroll.set);self.watch_tree.pack(fill='both',expand=True);self.watch_tree.tag_configure('changed',foreground='#b35400')
        self.tabs.bind('<<NotebookTabChanged>>',lambda e:self.render_watches(),add='+')
    def add_watch(self):
        expression=self.watch_input.get().strip()
        try:
            parse_watch(expression);paths=self.project.get('watches',[])
            if expression in paths:return
            if len(paths)>=100:raise ValueError(tr('Sono consentite al massimo 100 Watch.'))
            self.commit_code();self.checkpoint();self.project.setdefault('watches',[]).append(expression);self.watch_input.set('');self.watch_previous={};self.update_source();self.render_watches()
        except ValueError as exc:messagebox.showerror(tr('Watch'),str(exc),parent=self)
    def remove_watch(self):
        selected=self.watch_tree.selection()
        if not selected:return
        root=selected[0]
        while self.watch_tree.parent(root):root=self.watch_tree.parent(root)
        index=int(root.split(':')[1]);paths=self.project.get('watches',[])
        if not 0<=index<len(paths):return
        self.commit_code();self.checkpoint();paths.pop(index)
        if not paths:self.project.pop('watches',None)
        self.watch_previous={};self.update_source();self.render_watches()
    def render_watches(self):
        if not hasattr(self,'watch_tree') or self.tabs.select()!=str(self.watch_page):return
        tree=self.watch_tree;opened=set()
        def remember(parent=''):
            for row in tree.get_children(parent):
                if tree.item(row,'open'):opened.add(row)
                remember(row)
        remember();selection=tree.selection();scroll=tree.yview()[0];tree.delete(*tree.get_children());current={};signatures={};budget=[1500]
        snapshot=self.inspector_data if self.watch_session==getattr(self,'history_session',None) else None
        for i,path in enumerate(self.project.get('watches',[])):
            node,origin=resolve_watch(path,snapshot);key='watch:'+str(i)
            if id(node) not in signatures:signatures[id(node)]=json.dumps(node,sort_keys=True,ensure_ascii=True)
            current[path]=signatures[id(node)]
            changed=path in self.watch_previous and self.watch_previous[path]!=current[path]
            tree.insert('','end',iid=key,text=path,values=(node.get('type','') if node else '',node.get('value','') if node else tr('Non disponibile nel campione'),origin),open=key in opened,tags=('changed',) if changed else ())
            def children(parent,items):
                for j,child in enumerate(items):
                    if budget[0]<=0:break
                    budget[0]-=1
                    cid=parent+'/'+str(j);tree.insert(parent,'end',iid=cid,text=child.get('name',''),values=(child.get('type',''),child.get('value',''),''),open=cid in opened);children(cid,child.get('children',[]))
            if node:children(key,node.get('children',[]))
        self.watch_previous=current
        for row in selection:
            if tree.exists(row):tree.selection_add(row)
        tree.yview_moveto(scroll)
        state=tr('Nessun campione della sessione corrente') if not snapshot else {'running':tr('In esecuzione: valori campionati'),'paused':tr('In pausa: valori del punto di arresto'),'finished':tr('Terminato: ultimi valori disponibili')}.get(snapshot.get('state'),tr('Valori campionati'))
        self.watch_status.set(state)
