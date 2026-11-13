"""Navigable diagnostics, computed off the Tk thread without running project code."""
import copy
import queue
import threading
from tkinter import ttk
from pathlib import Path
from project_problems import project_problems,module_inventory
from i18n import tr

class ProblemsMixin:
    def build_problems(self):
        self.problems_page=ttk.Frame(self.tabs);self.tabs.add(self.problems_page,text=tr('Problemi'))
        bar=ttk.Frame(self.problems_page,padding=5);bar.pack(fill='x')
        ttk.Button(bar,text=tr('Analizza progetto'),command=self.analyze_project).pack(side='left')
        self.problem_status=ttk.Label(bar,text=tr('Analisi statica: nessun codice del progetto viene eseguito.'));self.problem_status.pack(side='left',padx=8)
        self.problem_tree=ttk.Treeview(self.problems_page,columns=('severity','object','event','line','message'),show='headings')
        for key,label,width in [('severity',tr('Tipo'),80),('object',tr('Oggetto'),110),('event',tr('Evento'),100),('line',tr('Riga'),50),('message',tr('Descrizione'),450)]:self.problem_tree.heading(key,text=label);self.problem_tree.column(key,width=width,stretch=key=='message')
        scroll=ttk.Scrollbar(self.problems_page,command=self.problem_tree.yview);scroll.pack(side='right',fill='y');self.problem_tree.configure(yscrollcommand=scroll.set);self.problem_tree.pack(fill='both',expand=True)
        self.problem_tree.bind('<Double-1>',self.open_problem);self.problem_tree.bind('<Return>',self.open_problem)
        self.problem_results=queue.Queue();self.problem_serial=0;self.problem_rows=[];self.problem_alive=True
        self.bind('<Destroy>',self.problems_destroy,add='+');self.problem_timer=self.after(100,self.poll_problems)

    def analyze_project(self):
        self.commit_code();self.tabs.select(self.problems_page);self.problem_serial+=1;serial=self.problem_serial
        project=copy.deepcopy(self.project);python=self.config_data['python'];root=self.path.parent if self.path else None
        self.problem_status.configure(text=tr('Analisi in corso…'))
        def work():
            warning=None
            try:modules=module_inventory(python,root)
            except Exception as exc:modules=None;warning=str(exc)
            rows=project_problems(project,modules);self.problem_results.put((serial,project,python,rows,warning))
        threading.Thread(target=work,daemon=True).start()

    def poll_problems(self):
        if not self.problem_alive:return
        try:
            while True:
                serial,project,python,rows,warning=self.problem_results.get_nowait()
                if serial!=self.problem_serial:continue
                if project!=self.project or python!=self.config_data['python']:
                    self.problem_status.configure(text=tr('Progetto o interprete cambiato: ripeti l’analisi.'));continue
                self.problem_snapshot=project;self.problem_rows=rows;self.problem_tree.delete(*self.problem_tree.get_children())
                for i,row in enumerate(rows):self.problem_tree.insert('','end',iid=str(i),values=(tr('Errore') if row['severity']=='error' else tr('Avviso'),row['object'],row['event'],row['line'],row['message']))
                self.problem_status.configure(text=tr('Problemi rilevati: ')+str(len(rows))+((' • '+tr('Verifica import non disponibile: ')+warning[:120]) if warning else ''))
        except queue.Empty:pass
        self.problem_timer=self.after(100,self.poll_problems)

    def open_problem(self,event=None):
        selection=self.problem_tree.selection()
        if not selection:return
        self.commit_code()
        if getattr(self,'problem_snapshot',None)!=self.project:return self.analyze_project()
        row=self.problem_rows[int(selection[0])]
        if row['object']=='$project':self.global_code(row['event'])
        else:
            names={o['name'] for f in self.project['forms'] for o in [f]+f['widgets']}
            if row['object'] not in names:return
            self.choose_designer_object(row['object']);self.evvar.set(row['event']);self.edit_event()
        index=f"{row['line']}.{row['column']}";self.code.mark_set('insert',index);self.code.see(index);self.code.focus_set()
    def problems_destroy(self,event):
        if event.widget is self:self.problem_alive=False;self.after_cancel(self.problem_timer)
