"""Keyboard command discovery, backed by the existing application menu actions."""
import unicodedata
import tkinter as tk
from tkinter import ttk
from i18n import tr,EN_MESSAGES


def normalized(text):
    return ''.join(c for c in unicodedata.normalize('NFKD',text.casefold()) if not unicodedata.combining(c)).replace('…','').strip()


def menu_commands(definitions):
    reverse={}
    for source,target in EN_MESSAGES.items():reverse.setdefault(target,[]).append(source)
    rows=[]
    for category,items in definitions:
        for label,action in items:
            terms=[category,label,EN_MESSAGES.get(category,''),EN_MESSAGES.get(label,''),*reverse.get(category,[]),*reverse.get(label,[])]
            rows.append({'id':len(rows),'category':category,'name':label,'label':category+' → '+label,'search':normalized(' '.join(terms)),'action':action})
    return rows


def matching_commands(rows,query,recent=()):
    query=normalized(query);tokens=query.split();recency={key:i for i,key in enumerate(recent)}
    matches=[row for row in rows if all(token in row['search'] for token in tokens)]
    if not query:return sorted(matches,key=lambda row:(recency.get(row['id'],len(recent)),row['id']))
    def rank(row):
        label=normalized(row['name'])
        return (0 if label==query else 1 if label.startswith(query) else 2 if query in label else 3,row['id'])
    return sorted(matches,key=rank)


class CommandPaletteMixin:
    def open_command_palette(self,event=None):
        existing=getattr(self,'command_palette_window',None)
        if existing is not None and existing.winfo_exists():existing.lift();self.command_palette_entry.focus_set();return 'break'
        grabbed=self.grab_current()
        if grabbed is not None and grabbed is not self:grabbed.lift();return 'break'
        self.dismiss_completion();previous=self.focus_get();win=tk.Toplevel(self);self.command_palette_window=win
        win.title(tr('Palette dei comandi'));win.transient(self);win.geometry('760x440');win.minsize(540,330)
        ttk.Label(win,text=tr('Cerca una funzione, poi premi Invio. Puoi usare termini italiani o inglesi.'),padding=10,wraplength=700).pack(fill='x')
        query=tk.StringVar();entry=self.command_palette_entry=ttk.Entry(win,textvariable=query,font=('TkDefaultFont',13));entry.pack(fill='x',padx=10,pady=(0,8))
        area=ttk.Frame(win);area.pack(fill='both',expand=True,padx=10)
        results=tk.Listbox(area,exportselection=False,activestyle='dotbox');scroll=ttk.Scrollbar(area,command=results.yview);results.configure(yscrollcommand=scroll.set);scroll.pack(side='right',fill='y');results.pack(fill='both',expand=True)
        hint=tk.StringVar();ttk.Label(win,textvariable=hint,padding=8).pack(fill='x')
        ttk.Label(win,text=tr('↑↓ seleziona · Invio esegue · Esc chiude. Senza ricerca, i comandi recenti sono in cima.'),padding=(10,4),wraplength=700).pack(fill='x')
        rows=menu_commands(self.command_definitions);visible=[];closed=[False]
        def close():
            if closed[0]:return 'break'
            closed[0]=True;win.destroy()
            if previous is not None and previous.winfo_exists():previous.focus_set()
            return 'break'
        def refresh(*args):
            visible[:]=matching_commands(rows,query.get(),getattr(self,'command_palette_recent',[]));results.delete(0,'end')
            for row in visible:results.insert('end',row['label'])
            if visible:results.selection_set(0);results.activate(0);results.see(0)
            hint.set(tr('Comandi trovati: {v0}',v0=len(visible)) if visible else tr('Nessun comando trovato.'))
        def move(delta):
            if visible:
                selected=results.curselection();index=max(0,min(len(visible)-1,(selected[0] if selected else 0)+delta));results.selection_clear(0,'end');results.selection_set(index);results.activate(index);results.see(index)
            return 'break'
        def run(event=None):
            selection=results.curselection()
            if closed[0] or not selection:return 'break'
            row=visible[selection[0]];recent=getattr(self,'command_palette_recent',[]);self.command_palette_recent=[row['id']]+[key for key in recent if key!=row['id']][:9]
            close();self.after_idle(row['action']);return 'break'
        query.trace_add('write',refresh);win.protocol('WM_DELETE_WINDOW',close)
        for widget in (entry,results):
            widget.bind('<Return>',run);widget.bind('<Escape>',lambda e:close());widget.bind('<Down>',lambda e:move(1));widget.bind('<Up>',lambda e:move(-1))
        results.bind('<Double-Button-1>',run)
        refresh();win.grab_set();entry.focus_set();return 'break'
