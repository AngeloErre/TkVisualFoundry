"""Prepare a visual-only form snapshot; never carry user event/import/startup code."""
import copy
from components import BUILTINS
from core import KINDS,generate
from i18n import tr

SAFE_MODULES={'tkinter','tkinter.ttk','tkinter.scrolledtext','customtkinter','tkcalendar','Pmw'}
SAFE_ADAPTERS={'Notebook','CTkTabview','Sheet'}

def preview_project(project,form_index,pages=None):
    snapshot=copy.deepcopy(project);form=snapshot['forms'][form_index];snapshot['forms']=[form]
    snapshot['imports']='';snapshot['requirements']=[];snapshot['files']=[];snapshot['components']={}
    form['events']={};form['title']=str(form.get('title',form['name']))+' • '+tr('Anteprima')
    placeholders=[]
    for widget in form['widgets']:
        widget['events']={};kind=widget['kind'];spec=BUILTINS.get(kind,{})
        approved=(kind in KINDS or kind in SAFE_ADAPTERS or spec.get('module') in SAFE_MODULES) and kind not in project.get('components',{})
        if not approved:
            placeholders.append(widget['name']+' ('+kind+')');widget['kind']='Label'
            widget['props']={'text':widget['name']+'\n'+kind+' • '+tr('segnaposto'),'bg':'#e7eaf0','fg':'#344054','relief':'groove'}
        else:
            widget['props']={key:value for key,value in widget.get('props',{}).items() if not key.endswith('command') and key not in ('variable','textvariable','takefocus')}
    startup=[f'self.show({form["name"]!r})']
    for widget in form['widgets']:
        page=(pages or {}).get(widget['name'])
        if page and page in widget.get('props',{}).get('pages',[]):
            if widget['kind']=='Notebook':startup.append(f'self.{widget["name"]}.select(self.{widget["name"]}.pages[{page!r}])')
            elif widget['kind']=='CTkTabview':startup.append(f'self.{widget["name"]}.set({page!r})')
    snapshot['startup']='\n'.join(startup)
    return snapshot,placeholders

def preview_source(project,form_index,pages=None):
    snapshot,placeholders=preview_project(project,form_index,pages)
    return generate(snapshot),snapshot,placeholders
