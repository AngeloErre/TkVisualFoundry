"""Read-only sampled variable inspector for isolated F5/F9 sessions."""
import hashlib
import json
from pathlib import Path
import time
import uuid
import tkinter as tk
from tkinter import ttk
from i18n import tr
from project_files import included_files

class InspectorMixin:
    def build_inspector(self):
        self.inspector_enabled=tk.BooleanVar(value=True);self.inspector_filter=tk.StringVar();self.inspector_data=None;self.inspector_file=None;self.inspector_sequence=None;self.inspector_last_poll=0;self.inspector_process=None
        page=self.inspector_page=ttk.Frame(self.tabs);self.tabs.add(page,text=tr('Variabili / Ispettore'))
        bar=ttk.Frame(page,padding=6);bar.pack(fill='x')
        ttk.Checkbutton(bar,text=tr('Monitoraggio per il prossimo avvio'),variable=self.inspector_enabled).pack(side='left')
        ttk.Label(bar,text=tr('Filtra')).pack(side='left',padx=(12,4));entry=ttk.Entry(bar,textvariable=self.inspector_filter,width=25);entry.pack(side='left');entry.bind('<KeyRelease>',lambda e:self.render_inspector())
        self.inspector_status=tk.StringVar(value=tr('Avvia con F5 o F9 per osservare le variabili.'));ttk.Label(page,textvariable=self.inspector_status,padding=6,wraplength=900).pack(fill='x')
        self.inspector_tree=ttk.Treeview(page,columns=('type','value'),show='tree headings');self.inspector_tree.heading('#0',text=tr('Variabile / ambito'));self.inspector_tree.heading('type',text=tr('Tipo'));self.inspector_tree.heading('value',text=tr('Valore'));self.inspector_tree.column('#0',width=300);self.inspector_tree.column('type',width=120);self.inspector_tree.column('value',width=500)
        scroll=ttk.Scrollbar(page,command=self.inspector_tree.yview);scroll.pack(side='right',fill='y');self.inspector_tree.configure(yscrollcommand=scroll.set);self.inspector_tree.pack(fill='both',expand=True)
        self.inspector_tree.tag_configure('changed',foreground='#b35400')
        ttk.Label(page,text=tr('Campioni ogni 0,5 s. Locali attive o ultima funzione osservata; valori e contenitori limitati. Nessuna espressione o proprietà viene eseguita.'),wraplength=900,padding=6).pack(fill='x')
        self.inspector_previous={}
    def inspector_args(self,path,debug=False):
        self.inspector_process=None
        if not self.inspector_enabled.get():
            self.inspector_file=None;self.inspector_status.set(tr('Monitoraggio disattivato per questo avvio.'));return None
        folder=Path(self.temp.name)/('inspect-'+uuid.uuid4().hex);folder.mkdir(mode=0o700)
        for name in ('inspector_runtime.py','inspector_runner.py'):(folder/name).write_bytes(Path(__file__).with_name(name).read_bytes())
        output=folder/'snapshot.json';tracked=[]
        if self.path:
            tracked=[str(p.resolve()) for p in included_files(self.project,self.path.parent).values() if p.suffix=='.py']
        config=folder/'config.json';config.write_text(json.dumps({'output':str(output),'tracked':tracked}),encoding='utf-8')
        self.inspector_file=output;self.inspector_sequence=None;self.inspector_data=None;self.inspector_previous={};self.inspector_tree.delete(*self.inspector_tree.get_children());self.inspector_status.set(tr('In attesa del primo campione…'))
        return [self.config_data['python'],'-u',str(folder/'inspector_runner.py'),'--config',str(config)]+(['--debug'] if debug else [])+[part for line in (sorted(self.breaks) if debug else []) for part in ('--break',str(line))]+[str(path)]
    def inspector_launched(self,process):
        if not self.inspector_file:return
        if process is None or process.poll() is not None:
            self.inspector_file=None;self.inspector_status.set(tr('Monitoraggio non avviato'));return
        self.inspector_process=process
    def inspector_finished(self,process):
        if process is not self.inspector_process:return
        self.inspector_last_poll=0;self.poll_inspector();self.inspector_file=None;self.inspector_process=None
        if self.inspector_data:
            self.inspector_data['state']='finished';self.render_inspector()
        else:self.inspector_status.set(tr('Terminato prima del primo campione'))
    def poll_inspector(self):
        if not self.inspector_file or time.monotonic()-self.inspector_last_poll<0.5:return
        self.inspector_last_poll=time.monotonic()
        try:
            if self.inspector_file.stat().st_size>2_000_000:raise ValueError('Inspector snapshot exceeds size limit')
            data=json.loads(self.inspector_file.read_text(encoding='utf-8'))
            if data.get('version')!=1 or not isinstance(data.get('groups'),list):return
            stamp=(data.get('sequence'),data.get('state'))
            if stamp==self.inspector_sequence:return
            self.inspector_sequence=stamp;self.inspector_data=data;self.render_inspector()
        except (OSError,ValueError,TypeError):pass
    def render_inspector(self):
        data=self.inspector_data
        if not data:return
        tree=self.inspector_tree;opened=set()
        def remember(parent=''):
            for item in tree.get_children(parent):
                if tree.item(item,'open'):opened.add(item)
                remember(item)
        remember();selection=tree.selection();scroll=tree.yview()[0];tree.delete(*tree.get_children());query=self.inspector_filter.get().casefold();current={}
        def matches(node):return query in str(node.get('name','')).casefold() or any(matches(child) for child in node.get('children',[]))
        def insert(parent,node,key):
            if query and not matches(node):return
            value=str(node.get('value',''));kind=str(node.get('type',''));current[key]=(kind,value)
            changed=key in self.inspector_previous and self.inspector_previous[key]!=(kind,value)
            tree.insert(parent,'end',iid=key,text=node.get('name',''),values=(kind,value),open=key in opened or bool(query),tags=('changed',) if changed else ())
            for i,child in enumerate(node.get('children',[])):insert(key,child,key+'/'+str(i))
        counts={}
        for i,group in enumerate(data.get('groups',[])[:60]):
            identity=json.dumps([group.get(k,'') for k in ('scope','file','name')]);occurrence=counts.get(identity,0);counts[identity]=occurrence+1
            key='g'+hashlib.sha256((identity+str(occurrence)).encode()).hexdigest()[:20];scope=group.get('scope','');title=tr({'locals':'Locali','last locals':'Ultime locali','globals':'Globali','self':'Attributi self'}.get(scope,scope))+' · '+group.get('name','')
            values=group.get('values',[])
            if query and not any(matches(n) for n in values):continue
            tree.insert('','end',iid=key,text=title,values=('',(Path(group.get('file','')).name+':'+str(group.get('line',''))) if group.get('file') else ''),open=key in opened or not self.inspector_previous or bool(query))
            for node in values:insert(key,node,key+'/'+str(node.get('name','')))
        stack=data.get('stack',[])
        if stack and not query:
            tree.insert('','end',iid='stack',text=tr('Stack delle chiamate'),open='stack' in opened)
            for i,frame in enumerate(stack):tree.insert('stack','end',text=frame.get('function',''),values=(str(frame.get('line','')),frame.get('file','')))
        self.inspector_previous=current
        for item in selection:
            if tree.exists(item):tree.selection_add(item)
        tree.yview_moveto(scroll)
        state={'paused':tr('In pausa: valori del punto di arresto'),'running':tr('In esecuzione: valori campionati'),'finished':tr('Terminato: ultimi valori disponibili')}.get(data.get('state'),tr('Valori campionati'))
        self.inspector_status.set(state+' · '+time.strftime('%H:%M:%S',time.localtime(data.get('time',time.time()))))
