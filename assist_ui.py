"""Non-modal completions and a contextual examples panel."""
import builtins
import keyword
import re
import tkinter as tk
from tkinter import ttk
from code_assist import completions,examples,signature

class AssistMixin:
    def build_assistant(self,parent):
        self.assist_popup=None;self.assist_timer=None;self.assist_items=[]
        self.code.pack_forget()
        panel=ttk.Frame(parent,padding=(10,6));panel.pack(side='bottom',fill='x')
        self.assist_title=tk.StringVar(value='Assistente codice • seleziona un componente e apri un evento')
        ttk.Label(panel,textvariable=self.assist_title,style='Title.TLabel').pack(anchor='w')
        row=ttk.Frame(panel);row.pack(fill='x',pady=4)
        self.assist_list=tk.Listbox(row,height=4,exportselection=False,font=('Menlo',11));self.assist_list.pack(side='left',fill='x',expand=True)
        self.assist_list.bind('<<ListboxSelect>>',self.assist_describe)
        self.assist_list.bind('<Double-Button-1>',lambda e:self.insert_example())
        ttk.Button(row,text='Inserisci esempio',command=self.insert_example).pack(side='left',padx=10)
        ttk.Button(row,text='Completa  Ctrl+Spazio',command=self.complete).pack(side='left')
        self.assist_detail=tk.StringVar(value='Scrivi self. per vedere i controlli; dopo il nome scrivi . per i metodi.')
        ttk.Label(panel,textvariable=self.assist_detail,wraplength=660).pack(anchor='w')
        self.signature_var=tk.StringVar();ttk.Label(panel,textvariable=self.signature_var,wraplength=660).pack(anchor='w')
        self.code.bind('<KeyRelease>',self.assist_key)
        self.code.bind('<Down>',self.assist_down)
        self.code.bind('<Up>',self.assist_up)
        self.code.bind('<Escape>',lambda e:self.dismiss_completion())
        self.code.bind('<Button-1>',lambda e:self.dismiss_completion(),add='+')
        self.tabs.bind('<<NotebookTabChanged>>',lambda e:self.dismiss_completion(),add='+')
        self.code.pack(fill='both',expand=True)

    def update_assistant(self):
        self.dismiss_completion();self.assist_list.delete(0,'end');self.assist_items=[]
        if self.code_target and not self.code_target[2]:
            obj,event,_=self.code_target;self.assist_items=examples(obj,self.project)
            self.assist_title.set(obj['name']+' • '+event+' — cosa puoi fare')
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
        self.code.insert('insert',snippet);self.code.edit_separator();self.highlight();self.code.focus_set()

    def assist_key(self,event):
        self.highlight()
        if self.assist_timer:self.after_cancel(self.assist_timer);self.assist_timer=None
        before=self.code.get('1.0','insert');self.signature_var.set(signature(before,self.project))
        if event.keysym in ('Up','Down','Return','Tab','Escape','Left','Right','Control_L','Control_R','Shift_L','Shift_R'):return
        self.dismiss_completion()
        if event.char=='.' or (signature(before,self.project) and event.char in ('(',',',' ')) or re.search(r'(?:self\.\w*|self\.\w+\.\w*|\w{2,})$',before):
            self.assist_timer=self.after(300,lambda:self.complete(automatic=True))

    def dismiss_completion(self):
        if getattr(self,'assist_popup',None):
            self.assist_popup.destroy();self.assist_popup=None
        if getattr(self,'assist_timer',None):self.after_cancel(self.assist_timer);self.assist_timer=None

    def assist_down(self,event=None):return self.move_completion(1)
    def assist_up(self,event=None):return self.move_completion(-1)
    def move_completion(self,delta):
        if not self.assist_popup:return None
        box=self.completion_box;n=box.size();index=box.curselection()[0] if box.curselection() else 0
        index=max(0,min(n-1,index+delta));box.selection_clear(0,'end');box.selection_set(index);box.see(index);self.completion_describe();return 'break'

    def completion_describe(self,event=None):
        selected=self.completion_box.curselection()
        if selected:self.assist_detail.set(self.completion_items[selected[0]][1])

    def accept_completion(self,event=None):
        if not self.assist_popup:return None
        selected=self.completion_box.curselection()
        if selected:
            text=self.completion_items[selected[0]][0];self.code.edit_separator()
            self.code.delete('assist_start','assist_end');self.code.insert('assist_start',text);self.code.mark_set('insert','assist_start+'+str(len(text))+'c');self.code.edit_separator()
        self.dismiss_completion();self.highlight();self.code.focus_set();return 'break'

    def complete(self,event=None,automatic=False):
        self.dismiss_completion()
        if self.code.focus_get()!=self.code and automatic:return
        if automatic and self.code.tag_ranges('sel'):return
        before=self.code.get('1.0','insert');prefix,items=completions(before,self.project)
        if not items and not automatic:
            match=re.search(r'[\w.]+$',before);prefix=match.group() if match else ''
            items=[(s,'Python') for s in keyword.kwlist+dir(builtins)+['messagebox','filedialog','tk','ttk'] if s.startswith(prefix)]
            try:
                import jedi
                body=self.code.get('1.0','end-1c');script='class Application:\n    def handler(self, event=None):\n'+'\n'.join('        '+line for line in body.splitlines())
                row,col=map(int,self.code.index('insert').split('.'))
                items.extend((prefix+c.complete,c.description) for c in jedi.Script(script).complete(row+2,col+8))
            except Exception:pass
        if not items:return 'break'
        self.completion_items=list(dict(items).items())[:80]
        self.code.mark_set('assist_start',f'insert-{len(prefix)}c');self.code.mark_gravity('assist_start','left');self.code.mark_set('assist_end','insert')
        popup=tk.Toplevel(self);self.assist_popup=popup;popup.overrideredirect(True);popup.transient(self)
        bounds=self.code.bbox('insert') or (0,0,0,20)
        x=min(self.code.winfo_rootx()+bounds[0],max(0,self.winfo_screenwidth()-440));y=self.code.winfo_rooty()+bounds[1]+bounds[3]
        if y+210>self.winfo_screenheight():y=max(0,y-230)
        popup.geometry(f'440x200+{x}+{y}')
        colors=self.config_data.get('appearance',{})
        self.completion_box=tk.Listbox(popup,exportselection=False,font=('Menlo',12),takefocus=False,bg=colors.get('surface','#ffffff'),fg=colors.get('foreground','#25324a'),selectbackground=colors.get('accent','#2563eb'),selectforeground='white')
        self.completion_box.pack(fill='both',expand=True)
        for text,doc in self.completion_items:self.completion_box.insert('end',text)
        self.completion_box.selection_set(0);self.completion_describe()
        self.completion_box.bind('<<ListboxSelect>>',self.completion_describe)
        self.completion_box.bind('<ButtonRelease-1>',self.accept_completion)
        return 'break'
