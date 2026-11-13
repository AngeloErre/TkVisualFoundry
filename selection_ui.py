"""Multiple-selection commands for the canvas designer."""
from tkinter import messagebox
from multi_selection import selected_roots,moved_geometry,layout_geometry
from hierarchy import descendants
from i18n import tr

class SelectionMixin:
    def selected_controls(self):
        names=getattr(self,'selection_names',set())
        if self.selected is None:self.selection_names=set();return []
        if self.selected['name'] not in names:names={self.selected['name']};self.selection_names=names
        return [w for w in self.form['widgets'] if w['name'] in names]

    def select_all_controls(self,event=None):
        widgets=list(self.displayed_widgets());self.selection_names={w['name'] for w in widgets};self.selected=widgets[-1] if widgets else None
        self.draw();self.properties();return 'break'

    def layout_selection(self,operation):
        widgets=self.selected_controls()
        try:changes=layout_geometry(self.form,widgets,self.selected,operation)
        except ValueError as exc:return messagebox.showinfo(tr('Disposizione'),str(exc),parent=self)
        self.commit_code();self.checkpoint()
        for w in widgets:w.update(changes[w['name']])
        self.draw();self.properties();self.update_source()

    def delete_selection(self):
        widgets=self.selected_controls();removed=set()
        for w in widgets:removed|=descendants(self.form,w['name'])|{w['name']}
        self.commit_code();self.checkpoint();self.form['widgets'][:]=[w for w in self.form['widgets'] if w['name'] not in removed]
        self.selected=None;self.selection_names=set();self.code_target=None;self.refresh()

    def duplicate_selection(self):
        roots=selected_roots(self.form,self.selected_controls());self.commit_code();self.checkpoint();copies=[]
        for root in roots:
            self.selected=root;self.duplicate_widget_tree();copies.append(self.selected)
        self.selection_names={w['name'] for w in copies};self.selected=copies[-1] if copies else None;self.refresh()
