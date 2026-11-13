"""Non-modal completions and a contextual examples panel."""
from i18n import tr
import copy
import queue
from pathlib import Path
import re
import tkinter as tk
from tkinter import ttk
from code_assist import examples
from semantic_engine import local_analysis,in_literal
from analysis_client import AnalysisClient

class AssistMixin:
    def build_assistant(self,parent):
        self.assist_popup=None;self.assist_timer=None;self.assist_items=[]
        self.analysis_client=AnalysisClient();self.analysis_requests={};self.assist_generation=0;self.detail_timer=None;self.detail_requested=None;self.local_items=[];self.semantic_state='';self.assist_results_timer=self.after(60,self.poll_analysis)
        self.bind('<Destroy>',self.assist_destroy,add='+')
        self.code.pack_forget()
        panel=ttk.Frame(parent,padding=(10,6));panel.pack(side='bottom',fill='x')
        self.assist_title=tk.StringVar(value=tr('Assistente codice • seleziona un componente e apri un evento'))
        ttk.Label(panel,textvariable=self.assist_title,style='Title.TLabel').pack(anchor='w')
        row=ttk.Frame(panel);row.pack(fill='x',pady=4)
        self.assist_list=tk.Listbox(row,height=4,exportselection=False,font=('Menlo',11));self.assist_list.pack(side='left',fill='x',expand=True)
        self.assist_list.bind('<<ListboxSelect>>',self.assist_describe)
        self.assist_list.bind('<Double-Button-1>',lambda e:self.insert_example())
        ttk.Button(row,text=tr('Inserisci esempio'),command=self.insert_example).pack(side='left',padx=10)
        ttk.Button(row,text=tr('Ctrl+Spazio'),command=self.complete).pack(side='left',padx=2)
        ttk.Button(row,text=tr('Motore…'),command=self.setup_intellisense).pack(side='left',padx=2)
        self.assist_detail=tk.StringVar(value='Scrivi self. per vedere i controlli; dopo il nome scrivi . per i metodi.')
        ttk.Label(panel,textvariable=self.assist_detail,wraplength=660).pack(anchor='w')
        self.signature_var=tk.StringVar();ttk.Label(panel,textvariable=self.signature_var,wraplength=660).pack(anchor='w')
        self.code.bind('<KeyRelease>',self.assist_key)
        self.code.bind('<Down>',self.assist_down)
        self.code.bind('<Up>',self.assist_up)
        self.code.bind('<Escape>',lambda e:self.dismiss_completion())
        self.code.bind('<Button-1>',lambda e:self.dismiss_completion(),add='+')
        self.code.bind('<FocusOut>',lambda e:self.after(80,self.hide_if_unfocused),add='+')
        self.tabs.bind('<<NotebookTabChanged>>',lambda e:self.dismiss_completion(),add='+')
        self.code.pack(fill='both',expand=True)

    def update_assistant(self):
        self.dismiss_completion();self.assist_list.delete(0,'end');self.assist_items=[]
        if self.code_target and not self.code_target[2]:
            obj,event,_=self.code_target;self.assist_items=examples(obj,self.project)
            self.assist_title.set(obj['name']+' • '+event+tr(' — cosa puoi fare'))
            for label,code,doc in self.assist_items:self.assist_list.insert('end',label+'   →   '+code)
            if self.assist_items:self.assist_list.selection_set(0);self.assist_describe()
        else:self.assist_title.set('Codice progetto • usa self. per esplorare i componenti')
        self.signature_var.set('')

    def assist_describe(self,event=None):
        selection=self.assist_list.curselection()
        if selection:self.assist_detail.set(self.assist_items[selection[0]][2])

    def insert_example(self):
        selected=self.assist_list.curselection()
        if not selected or not self.code_target:return
        snippet=self.assist_items[selected[0]][1]
        self.dismiss_completion();self.code.edit_separator()
        try:
            start,end=self.code.tag_ranges('sel');self.code.delete(start,end);self.code.mark_set('insert',start)
        except ValueError:
            if self.code.get('1.0','end-1c').strip()=='pass':self.code.delete('1.0','end')
            elif self.code.get('insert linestart','insert').strip():
                line=self.code.get('insert linestart','insert');indent=re.match(r'\s*',line).group()
                self.code.insert('insert','\n'+indent)
        base_indent=re.match(r'\s*',self.code.get('insert linestart','insert')).group()
        snippet=snippet.replace('\n','\n'+base_indent)
        self.code.insert('insert',snippet);self.code.edit_separator();self.highlight();self.code.focus_set()

    def assist_key(self,event):
        self.highlight()
        if event.keysym in ('Up','Down','Return','Tab','Escape','Control_L','Control_R','Shift_L','Shift_R'):return
        self.dismiss_completion();before=self.code.get('1.0','insert')
        if in_literal(before):
            self.assist_timer=self.after(160,lambda:self.complete(automatic=True,show_popup=False));return
        popup=event.keysym not in ('Left','Right') and (event.char=='.' or bool(re.search(r'(?:\.\w*|\w{2,})$',before)))
        local=local_analysis(before,self.project,self.code.get('1.0','end-1c'));self.signature_var.set(local['calltip'][:350])
        if local['items'] and before.rstrip().endswith(('(',',','=')):popup=True
        self.assist_timer=self.after(40 if event.char=='.' else 160,lambda:self.complete(automatic=True,show_popup=popup))

    def dismiss_completion(self):
        self.assist_generation=getattr(self,'assist_generation',0)+1
        if hasattr(self,'analysis_requests'):self.analysis_requests.clear()
        if getattr(self,'assist_popup',None):self.assist_popup.destroy();self.assist_popup=None
        for name in ('assist_timer','detail_timer'):
            timer=getattr(self,name,None)
            if timer:self.after_cancel(timer);setattr(self,name,None)
        self.detail_requested=None

    def assist_down(self,event=None):return self.move_completion(1)
    def assist_up(self,event=None):return self.move_completion(-1)
    def move_completion(self,delta):
        if not self.assist_popup:return None
        box=self.completion_box;n=box.size();index=box.curselection()[0] if box.curselection() else 0
        index=max(0,min(n-1,index+delta));box.selection_clear(0,'end');box.selection_set(index);box.see(index);self.completion_describe();return 'break'

    def completion_describe(self,event=None):
        selected=self.completion_box.curselection()
        if not selected:return
        item=self.completion_items[selected[0]]
        detail=' • '.join(value for value in (item.get('signature',''),item.get('doc','').split('\n\n')[0]) if value)
        self.assist_detail.set(detail[:420] or item['name'])
        if self.detail_timer:self.after_cancel(self.detail_timer)
        name=item['name'];key=(self.assist_snapshot(),name)
        if self.detail_requested!=key:self.detail_timer=self.after(180,lambda:self.request_detail(name,key))

    def request_detail(self,name,key):
        self.detail_timer=None
        if not self.assist_popup or self.assist_snapshot()!=key[0]:return
        identifier=self.queue_analysis('detail',detail_name=name)
        self.detail_requested=key if identifier is not None else None

    def accept_completion(self,event=None):
        if not self.assist_popup:return None
        selected=self.completion_box.curselection()
        if selected:
            item=self.completion_items[selected[0]];text=item['insert'];length=item['prefix_len'];self.code.edit_separator()
            self.code.delete(f'insert-{length}c','insert');self.code.insert('insert',text);self.code.edit_separator()
        self.dismiss_completion();self.highlight();self.code.focus_set()
        self.assist_timer=self.after(80,lambda:self.complete(automatic=True,show_popup=False))
        return 'break'

    def assist_snapshot(self):
        target=self.code_target;context=(target[0].get('name','project'),target[1],target[2]) if target else None
        return self.code.get('1.0','end-1c'),self.code.index('insert'),context,self.assist_generation,self.config_data['python']

    def queue_analysis(self,action='complete',show_popup=False,detail_name=None):
        snapshot=self.assist_snapshot();body,cursor,context,_,python=snapshot
        mode='imports' if context and context[2] and context[1]=='imports' else 'event'
        request={'body':body,'cursor':cursor,'project':copy.deepcopy(self.project),'mode':mode,'action':action,'cwd':str(self.path.parent if self.path else Path(__file__).resolve().parent)}
        if detail_name:request['detail_name']=detail_name
        identifier=self.analysis_client.submit(python,request)
        if identifier is not None:self.analysis_requests[identifier]=(snapshot,show_popup,detail_name)
        if len(self.analysis_requests)>30:
            for identifier in sorted(self.analysis_requests)[:-15]:self.analysis_requests.pop(identifier,None)
        return identifier

    def complete(self,event=None,automatic=False,show_popup=True):
        self.dismiss_completion()
        if automatic and (self.code.focus_get()!=self.code or self.code.tag_ranges('sel')):return 'break'
        if not automatic:self.code.focus_set()
        before=self.code.get('1.0','insert')
        if in_literal(before):
            self.local_items=[];self.queue_analysis('signature',False);return 'break'
        local=local_analysis(before,self.project,self.code.get('1.0','end-1c'));self.local_items=local['items'];self.signature_var.set(local['calltip'][:350])
        if show_popup and self.local_items:self.show_completions(self.local_items)
        self.queue_analysis('complete' if show_popup else 'signature',show_popup)
        return 'break'

    def show_completions(self,items):
        unique={}
        for item in items:unique.setdefault(item['insert'],item)
        items=sorted(unique.values(),key=lambda item:(item['name'].startswith('_'),item['name'].casefold()))
        if not items:return
        selected_name=None
        if self.assist_popup:
            selection=self.completion_box.curselection()
            if selection:selected_name=self.completion_items[selection[0]]['name']
            self.completion_box.delete(0,'end')
        else:
            # A native Toplevel can take keyboard focus when mapped on macOS.
            # Keep suggestions inside the editor's window instead.
            popup=tk.Frame(self,takefocus=False,borderwidth=1,relief='solid');self.assist_popup=popup
            bounds=self.code.bbox('insert') or (0,0,0,20)
            available_width=max(1,self.winfo_width());available_height=max(1,self.winfo_height())
            width=min(540,available_width);height=min(240,available_height)
            x=max(0,min(self.code.winfo_rootx()-self.winfo_rootx()+bounds[0],available_width-width))
            y=self.code.winfo_rooty()-self.winfo_rooty()+bounds[1]+bounds[3]
            if y+height>available_height:y-=height+bounds[3]
            y=max(0,min(y,available_height-height))
            popup.place(x=x,y=y,width=width,height=height);popup.lift();colors=self.config_data.get('appearance',{})
            scroll=ttk.Scrollbar(popup);scroll.pack(side='right',fill='y')
            self.completion_box=tk.Listbox(popup,exportselection=False,font=('Menlo',12),takefocus=False,bg=colors.get('surface','#ffffff'),fg=colors.get('foreground','#25324a'),selectbackground=colors.get('accent','#2563eb'),selectforeground='white',yscrollcommand=scroll.set)
            self.completion_box.pack(fill='both',expand=True);scroll.configure(command=self.completion_box.yview)
            self.completion_box.bind('<<ListboxSelect>>',self.completion_describe);self.completion_box.bind('<ButtonRelease-1>',self.accept_completion)
        self.completion_items=items
        for item in items:self.completion_box.insert('end',item['name']+'   ['+item.get('kind','member')+']')
        index=next((i for i,item in enumerate(items) if item['name']==selected_name),0)
        self.completion_box.selection_set(index);self.completion_box.see(index);self.completion_describe()

    def poll_analysis(self):
        try:
            while True:
                result=self.analysis_client.results.get_nowait();context=self.analysis_requests.pop(result.get('id'),None)
                if context is None or context[0]!=self.assist_snapshot():continue
                snapshot,show_popup,detail_name=context
                if result.get('error'):
                    self.semantic_state=result['error']
                    if result.get('missing_jedi'):self.assist_detail.set(tr('Attiva Jedi dal pulsante Motore… per analizzare le librerie esterne. I suggerimenti standard restano disponibili.'))
                    elif not self.local_items:self.assist_detail.set(tr('Analisi semantica: ')+result['error'][:250])
                    continue
                self.semantic_state=result.get('engine','Jedi')
                if detail_name:
                    selected=self.completion_box.curselection() if self.assist_popup else ()
                    if selected and self.completion_items[selected[0]]['name']==detail_name and result.get('detail'):
                        detail=result['detail'];self.completion_items[selected[0]].update(signature=detail['signature'],doc=detail['doc']);self.completion_describe()
                    continue
                before=self.code.get('1.0','insert')
                if (result.get('calltip') or result.get('action')=='signature') and not re.search(r'self\.\w+\.(?:configure|config)\(',before):self.signature_var.set(result.get('calltip','')[:350])
                if show_popup and self.code.focus_get()==self.code:
                    items=result.get('items',[])
                    if re.search(r'self\.\w+\.(?:configure|config)\([^()]*$',before):items=[item for item in items if item['name'].endswith('=')]
                    self.show_completions(self.local_items+items)
        except queue.Empty:pass
        self.assist_results_timer=self.after(60,self.poll_analysis)

    def hide_if_unfocused(self):
        try:focus=self.focus_get()
        except tk.TclError:return
        if focus is self.code:return
        if self.assist_popup and focus and (focus is self.assist_popup or str(focus).startswith(str(self.assist_popup)+'.')):return
        self.dismiss_completion()

    def restart_intellisense(self):
        self.dismiss_completion();self.analysis_client.close();self.analysis_client=AnalysisClient();self.semantic_state=''
        self.assist_detail.set(tr('Motore ricaricato: digita un punto oppure premi Ctrl+Spazio.'))
    def setup_intellisense(self):self.open_dependencies(specs=['jedi>=0.19,<0.21'],auto_install=True,on_ready=self.restart_intellisense)
    def assist_destroy(self,event):
        if event.widget is self:
            self.analysis_client.close()
            try:
                self.dismiss_completion()
                if getattr(self,'assist_results_timer',None):self.after_cancel(self.assist_results_timer)
            except tk.TclError:pass
