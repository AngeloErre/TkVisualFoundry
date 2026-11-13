"""Container-aware designer helpers; nested coordinates remain relative to their parent."""
import copy
import tkinter as tk
from tkinter import ttk
from hierarchy import CONTAINERS,TABS,ordered_widgets,descendants,widget_origin,visible_widgets
from i18n import tr

class ContainerMixin:
    def current_container_pages(self):
        if not hasattr(self,'container_pages'):self.container_pages={}
        return self.container_pages

    def reveal_widget(self,widget):
        by_name={w['name']:w for w in self.form['widgets']};current=widget;seen=set()
        while current.get('parent') in by_name:
            parent=by_name[current['parent']]
            if parent['name'] in seen:break
            seen.add(parent['name'])
            if parent['kind'] in TABS:self.current_container_pages()[parent['name']]=current.get('page',parent['props']['pages'][0])
            current=parent

    def displayed_widgets(self):return visible_widgets(self.form,self.current_container_pages())

    def container_properties(self,obj,values):
        if obj is not self.form:values.update(parent=obj.get('parent',self.form['name']),page=obj.get('page',''))
        return values

    def container_property_entry(self,key,var,row,obj):
        if obj is self.form or key not in ('parent','page'):return False
        if key=='parent':
            forbidden=descendants(self.form,obj['name'])|{obj['name']}
            values=[self.form['name']]+[w['name'] for w in self.form['widgets'] if w['kind'] in CONTAINERS and w['name'] not in forbidden]
        else:
            parent=next((w for w in self.form['widgets'] if w['name']==obj.get('parent')),None)
            values=['']+(parent.get('props',{}).get('pages',[]) if parent and parent['kind'] in TABS else [])
        entry=ttk.Combobox(self.propbox,textvariable=var,values=values,state='readonly',width=18);entry.grid(row=row,column=1,sticky='ew')
        if key=='parent':
            def change(event=None):
                parent=next((w for w in self.form['widgets'] if w['name']==var.get()),None);pages=parent['props']['pages'] if parent and parent['kind'] in TABS else ['']
                self.propvars['page'].set(pages[0]);self.page_entry.configure(values=pages)
            entry.bind('<<ComboboxSelected>>',change)
        else:self.page_entry=entry
        return True

    def page_preview_selector(self,obj,row):
        if obj.get('kind') not in TABS:return
        values=obj.get('props',{}).get('pages',[])
        if not values:return
        selected=self.current_container_pages().get(obj['name'],values[0]);var=tk.StringVar(value=selected if selected in values else values[0])
        ttk.Label(self.propbox,text=tr('Pagina visibile')).grid(row=row,column=0,sticky='w')
        combo=ttk.Combobox(self.propbox,textvariable=var,values=values,state='readonly',width=18);combo.grid(row=row,column=1)
        def select(event=None):self.current_container_pages()[obj['name']]=var.get();self.draw()
        combo.bind('<<ComboboxSelected>>',select)

    def duplicate_widget_tree(self):
        root=self.selected;names=descendants(self.form,root['name'])|{root['name']};originals=[w for w in ordered_widgets(self.form) if w['name'] in names];mapping={};copies=[]
        used={o['name'] for f in self.project['forms'] for o in [f]+f['widgets']}
        for widget in originals:
            i=1;name=widget['kind']+str(i)
            while name in used:i+=1;name=widget['kind']+str(i)
            used.add(name);mapping[widget['name']]=name
        for widget in originals:
            item=copy.deepcopy(widget);item['name']=mapping[widget['name']]
            if item.get('parent') in mapping:item['parent']=mapping[item['parent']]
            if widget is root:item['x']+=20;item['y']+=20
            copies.append(item)
        self.form['widgets'].extend(copies);self.selected=next(w for w in copies if w['name']==mapping[root['name']])
