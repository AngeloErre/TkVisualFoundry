"""Reviewable rename for named forms and controls."""
import copy
import tkinter as tk
from tkinter import ttk,messagebox,simpledialog
from tkinter.scrolledtext import ScrolledText
from rename_refactor import rename_project
from i18n import tr

class RefactorMixin:
    def rename_selected(self):
        self.commit_code();obj=self.selected if self.selected is not None else self.form;old=obj['name']
        new=simpledialog.askstring(tr('Rinomina intelligente'),tr('Nuovo nome Python:'),initialvalue=old,parent=self)
        if new is None:return
        new=new.strip()
        if new==old:return
        snapshot=copy.deepcopy(self.project)
        try:plan=rename_project(snapshot,old,new.strip())
        except Exception as exc:return messagebox.showerror(tr('Rinomina intelligente'),str(exc),parent=self)
        win=tk.Toplevel(self);win.title(tr('Anteprima della rinomina'));win.geometry('820x580');win.transient(self)
        ttk.Label(win,text=old+' → '+new.strip(),style='Title.TLabel',padding=10).pack(fill='x')
        ttk.Label(win,text=tr('Controlla le modifiche. Testi, commenti e file Python esterni non vengono riscritti.'),wraplength=760,padding=8).pack(fill='x')
        text=ScrolledText(win,wrap='word',font=('Menlo',11));text.pack(fill='both',expand=True,padx=8)
        for row in plan['changes']:text.insert('end',f"{row['scope']} : {row['line']}\n  {row['before']} → {row['after']}\n\n")
        for row in plan['warnings']:text.insert('end',tr('Avviso')+f" — {row['scope']} : {row['line']}\n  {row['message']}\n\n")
        text.insert('end',tr('Riferimenti costruiti dinamicamente o contenuti in stringhe generiche richiedono verifica manuale.'));text.configure(state='disabled')
        def apply():
            self.commit_code()
            if self.project!=snapshot:
                messagebox.showinfo(tr('Rinomina intelligente'),tr('Il progetto è cambiato: ripeti la rinomina.'),parent=win);return
            self.checkpoint();self.project=plan['project'];self.code_target=None;self.selection_names=set()
            self.selected=None
            for index,form in enumerate(self.project['forms']):
                for item in [form]+form['widgets']:
                    if item['name']==new.strip():self.form_index=index;self.selected=None if item is form else item
            pages=self.current_container_pages()
            if old in pages:pages[new.strip()]=pages.pop(old)
            self.refresh();win.destroy()
        actions=ttk.Frame(win,padding=8);actions.pack(fill='x')
        ttk.Button(actions,text=tr('Applica rinomina'),command=apply,style='Accent.TButton').pack(side='right')
        ttk.Button(actions,text=tr('Annulla',context='cancel'),command=win.destroy).pack(side='right',padx=5)
