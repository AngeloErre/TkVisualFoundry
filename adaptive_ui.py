"""Edge-anchor editor, applied as one project-model operation."""
import copy
import tkinter as tk
from tkinter import ttk,messagebox
from core import validate
from i18n import tr

class AdaptiveMixin:
    def configure_anchors(self):
        controls=self.selected_controls()
        if not controls:return messagebox.showinfo(tr('Ancoraggi adattivi'),tr('Seleziona almeno un componente.'),parent=self)
        names=[w['name'] for w in controls];original_project=self.project;original_objects={w['name']:w for w in controls};initial=self.selected.get('layout',{})
        win=tk.Toplevel(self);win.title(tr('Ancoraggi adattivi'));win.geometry('640x410');win.minsize(610,390);win.transient(self)
        ttk.Label(win,text=', '.join(names[:6])+(' … (+'+str(len(names)-6)+')' if len(names)>6 else ''),padding=(12,4),wraplength=570).pack(fill='x')
        ttk.Label(win,text=tr('Scegli i bordi da mantenere. Due bordi opposti allargano il controllo; nessun bordo lo mantiene centrato rispetto alla variazione del contenitore.'),wraplength=570,padding=12).pack(fill='x')
        row=ttk.Frame(win,padding=10);row.pack(fill='x');flags={}
        for edge,label in [('left',tr('Sinistra')),('top',tr('Alto')),('right',tr('Destra')),('bottom',tr('Basso'))]:
            flags[edge]=tk.BooleanVar(value=edge in initial.get('anchors',['left','top']));ttk.Checkbutton(row,text=label,variable=flags[edge]).pack(side='left',padx=8)
        sizes=ttk.Frame(win,padding=10);sizes.pack(fill='x');minimum={}
        for key,label in [('min_width',tr('Larghezza minima')),('min_height',tr('Altezza minima'))]:
            ttk.Label(sizes,text=label).pack(side='left');minimum[key]=tk.StringVar(value=str(initial.get(key,min(10,min(w['width' if key=='min_width' else 'height'] for w in controls)))));ttk.Entry(sizes,textvariable=minimum[key],width=6).pack(side='left',padx=8)
        ttk.Label(win,text=tr('Controlli Tk/ttk su form, frame/canvas e pagine Notebook. CustomTkinter e contenitori scorrevoli interni richiedono ancora layout da codice.'),wraplength=570,padding=12).pack(fill='x')
        def apply(reset=False):
            self.commit_code();probe=copy.deepcopy(self.project);found=[]
            try:
                current={w['name']:w for f in self.project['forms'] for w in f['widgets']}
                if self.project is not original_project or any(current.get(name) is not obj for name,obj in original_objects.items()):raise ValueError(tr('La selezione è cambiata: riapri gli ancoraggi.'))
                spec={} if reset else {'anchors':[edge for edge,var in flags.items() if var.get()],**{key:int(var.get()) for key,var in minimum.items()}}
                for form in probe['forms']:
                    for obj in form['widgets']:
                        if obj['name'] in names:
                            if reset:obj.pop('layout',None)
                            else:obj['layout']=copy.deepcopy(spec)
                            found.append(obj)
                if len(found)!=len(names):raise ValueError(tr('La selezione è cambiata: riapri gli ancoraggi.'))
                validate(probe,code=False)
                self.checkpoint()
                for form in self.project['forms']:
                    for obj in form['widgets']:
                        if obj['name'] in names:
                            if reset:obj.pop('layout',None)
                            else:obj['layout']=copy.deepcopy(spec)
                self.refresh();win.destroy()
            except Exception as exc:messagebox.showerror(tr('Ancoraggi adattivi'),str(exc),parent=win)
        actions=ttk.Frame(win,padding=10);actions.pack(fill='x')
        ttk.Button(actions,text=tr('Ripristina posizione fissa'),command=lambda:apply(True)).pack(side='left')
        ttk.Button(actions,text=tr('Applica'),command=apply,style='Accent.TButton').pack(side='right')
