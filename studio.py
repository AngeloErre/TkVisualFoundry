#!/usr/bin/env python3
"""TkVisualFoundry: visual Tkinter designer, event IDE and process debugger."""
from i18n import tr,get_language
from runtime_requirements import ensure_current, validate_interpreter
from settings_store import load_settings

if __name__ == "__main__":
    try: ensure_current()
    except RuntimeError as exc: raise SystemExit(str(exc))

import builtins
import webbrowser
from support_ui import SupportMixin
import copy
import io
import json
import keyword
import os
from pathlib import Path
import queue
import re
import subprocess
import sys
import tempfile
import threading
import uuid
import tokenize
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser, simpledialog
from tkinter.scrolledtext import ScrolledText
from core import KINDS, EVENTS, new_project, generate, load, validate, identifier
from components import registry, descriptor, requirements, install_args, design_size
from library_explorer import LibraryExplorer
from ux_theme import apply_theme, style_editor
from workspace_ui import WorkspaceMixin
from local_history import recovered_path
from command_palette import CommandPaletteMixin
from data_viewer_ui import DataViewerMixin
from search_ui import SearchMixin
from template_ui import TemplateMixin
from watch_ui import WatchMixin
from breakpoint_ui import BreakpointMixin
from event_breakpoints import resolve_breakpoints
from inspector_ui import InspectorMixin
from debug_ui import DebugViewMixin
from adaptive_ui import AdaptiveMixin
from history_ui import HistoryMixin
from refactor_ui import RefactorMixin
from preview_ui import PreviewMixin
from environment_ui import EnvironmentMixin
from selection_ui import SelectionMixin
from problems_ui import ProblemsMixin
from multi_selection import selected_roots,moved_geometry
from vb6_ui import VB6Mixin,panel_caption,resize_handle,resized_geometry,ToolTip
from assist_ui import AssistMixin
from intelligence_ui import IntelligenceMixin
from configuration_ui import ConfigurationMixin
from dependency_manager import dependency_plan
from component_palette import ComponentPalette,LayoutMixin
from project_ui import ProjectFilesMixin
from project_files import atomic_write_text
from library_ui import LibraryMixin
from productivity_ui import ProductivityMixin
from library_catalog import component_family
from container_ui import ContainerMixin
from hierarchy import CONTAINERS,TABS,ordered_widgets,descendants,widget_origin

BASE = Path(__file__).resolve().parent
SETTINGS = Path.home()/'.visualtkstudio.json'

class Studio(TemplateMixin,SearchMixin,DataViewerMixin,CommandPaletteMixin,WatchMixin,BreakpointMixin,InspectorMixin,DebugViewMixin,AdaptiveMixin,HistoryMixin,RefactorMixin,PreviewMixin,EnvironmentMixin,ProblemsMixin,SelectionMixin,VB6Mixin,IntelligenceMixin,ProductivityMixin,LibraryMixin,ContainerMixin,ProjectFilesMixin,LayoutMixin,ConfigurationMixin,AssistMixin,WorkspaceMixin,SupportMixin,tk.Tk):
    def __init__(self):
        ensure_current()
        super().__init__()
        self.title('TkVisualFoundry • Python Visual Development')
        self.geometry('1400x900'); self.minsize(1050,650)
        self.project=new_project(); self.path=None; self.selected=None; self.selection_names=set();self.form_index=0
        self.history=[]; self.future=[]; self.proc=None; self.messages=queue.Queue(); self.code_target=None
        self.temp=tempfile.TemporaryDirectory(prefix='visualtk-'); self.config_data={'language':get_language(),'grid':10,'font_size':13,'python':str(Path(sys.executable).with_name('python.exe')) if sys.platform=='win32' and Path(sys.executable).name.lower()=='pythonw.exe' else str(Path.home()/'Applications/VisualTkStudio/.venv/bin/python') if getattr(sys,'frozen',False) else sys.executable}
        self.config_data=load_settings(SETTINGS,self.config_data,self.winfo_rgb)
        self.global_python=self.config_data['python'];self.environment_busy=False
        self.init_preview()
        self.saved_state=json.dumps(self.project,sort_keys=True); self.drag=None; self.breaks=set()
        self.build(); self.apply_appearance(); self.menus(); self.refresh();self.init_local_history(); self.after(70,self.poll)
        if self.config_data.get('startup_checks',True):self.after(600,self.start_health)
        self.protocol('WM_DELETE_WINDOW',self.close)
        self.bind('<F1>',lambda e:self.help())
        self.bind('<F6>',lambda e:self.preview_form())
        for shortcut in ('<Control-Shift-F>','<Command-Shift-F>'):self.bind(shortcut,self.open_global_search)
        for shortcut in ('<Control-Shift-P>','<Command-Shift-P>'):self.bind(shortcut,self.open_command_palette)
        for sequence, action in [('<Command-s>',self.save),('<Control-s>',self.save),('<Command-o>',self.open_project),('<Control-o>',self.open_project),('<Command-z>',self.undo),('<Control-z>',self.undo),('<F5>',self.run),('<Shift-F5>',self.stop),('<F9>',self.debug)]:
            self.bind(sequence,lambda e,a=action:a())

    @property
    def form(self): return self.project['forms'][self.form_index]
    def checkpoint(self):
        self.history.append(copy.deepcopy(self.project)); self.history=self.history[-100:]; self.future.clear()
    def undo(self):
        self.commit_code()
        if self.history:
            self.future.append(copy.deepcopy(self.project)); self.project=self.history.pop(); self.form_index=min(self.form_index,len(self.project['forms'])-1); self.selected=None; self.code_target=None; self.refresh()
    def redo(self):
        self.commit_code()
        if self.future:
            self.history.append(copy.deepcopy(self.project)); self.project=self.future.pop(); self.form_index=min(self.form_index,len(self.project['forms'])-1); self.selected=None; self.code_target=None; self.refresh()
    def build(self):
        apply_theme(self)
        self.log_visible=False;self.log_toggle_text=tk.StringVar(value=tr('Mostra log'))
        self.build_classic_toolbar()
        self.statusbar=statusbar=ttk.Frame(self,relief='sunken',borderwidth=1);statusbar.pack(side='bottom',fill='x')
        self.status=tk.StringVar(value=tr('Pronto'));ttk.Label(statusbar,textvariable=self.status,anchor='w',width=1,padding=(6,3),style='Muted.TLabel').pack(side='left',fill='x',expand=True)
        self.selection_status=tk.StringVar();ttk.Label(statusbar,textvariable=self.selection_status,padding=(6,3),style='Muted.TLabel').pack(side='right')
        self.vertical=vertical=ttk.Panedwindow(self,orient='vertical'); vertical.pack(fill='both',expand=True)
        self.main_panes=main=ttk.Panedwindow(vertical,orient='horizontal'); vertical.add(main,weight=5)
        left=ttk.Frame(main,width=190,padding=3,relief='sunken',borderwidth=1); main.add(left,weight=0)
        panel_caption(left,tr('Casella degli strumenti'))
        palette_area=ttk.Frame(left,padding=3);palette_area.pack(fill='both',expand=True)
        self.right_panel=ttk.Frame(main,width=300,padding=3,relief='sunken',borderwidth=1)
        self.right_panes=ttk.Panedwindow(self.right_panel,orient='vertical');self.right_panes.pack(fill='both',expand=True)
        project_area=ttk.Frame(self.right_panes,height=220);self.right_panes.add(project_area,weight=1)
        inspector_area=ttk.Frame(self.right_panes);self.right_panes.add(inspector_area,weight=3)
        # Reserve the actions before allocating expandable content.
        palette_actions=ttk.Frame(palette_area);palette_actions.pack(side='top',fill='x',pady=(3,5))
        self.insert_button=ttk.Button(palette_actions,text=tr('＋ Inserisci nel form'),command=self.add_widget,style='Accent.TButton');self.insert_button.pack(fill='x')
        other=tk.Menu(palette_actions,tearoff=False)
        other.add_command(label=tr('Crea componente esterno…'),command=self.component_wizard)
        other.add_command(label=tr('Importa descrittore…'),command=self.import_component)
        other.add_command(label=tr('Prepara pacchetti del componente…'),command=self.palette_dependencies)
        ttk.Menubutton(palette_actions,text=tr('Altre opzioni ▾'),menu=other).pack(fill='x',pady=(3,0))
        self.palette_family=tk.StringVar(value=tr('Tutte le famiglie'))
        self.family_box=ttk.Combobox(palette_area,textvariable=self.palette_family,values=[tr('Tutte le famiglie')],state='readonly');self.family_box.pack(fill='x',pady=(2,5));self.family_box.bind('<<ComboboxSelected>>',lambda event:self.filter_palette())
        self.palette_query=tk.StringVar()
        ttk.Label(palette_area,text=tr('Cerca componente'),style='Muted.TLabel').pack(anchor='w')
        search=ttk.Entry(palette_area,textvariable=self.palette_query);search.pack(side='top',fill='x',pady=(2,5))
        self.palette_query.trace_add('write',lambda *_:self.filter_palette())
        self.palette_details=tk.StringVar(value=tr('Seleziona un componente. Doppio clic o Invio per inserirlo.'))
        ttk.Label(palette_area,textvariable=self.palette_details,wraplength=210,style='Muted.TLabel').pack(side='bottom',fill='x',pady=5)
        self.palette=ComponentPalette(palette_area);self.palette.pack(fill='both',expand=True)
        self.kinds=list(KINDS)+list(registry(self.project))
        for k in self.kinds:self.palette.insert('end',k)
        self.palette.bind('<Double-Button-1>',lambda e:self.add_widget())
        self.palette.bind('<Return>',lambda e:self.add_widget())
        self.palette.bind('<<ListboxSelect>>',self.palette_info)
        panel_caption(project_area,tr('Esplora progetto'))
        project_actions=ttk.Frame(project_area);project_actions.pack(fill='x',pady=2)
        ttk.Button(project_actions,text=tr('Designer'),command=lambda:self.tabs.select(0),style='Toolbar.TButton').pack(side='left')
        ttk.Button(project_actions,text=tr('Codice'),command=self.edit_event,style='Toolbar.TButton').pack(side='left')
        project_pages=ttk.Notebook(project_area);project_pages.pack(fill='both',expand=True)
        form_page=ttk.Frame(project_pages);file_page=ttk.Frame(project_pages)
        project_pages.add(form_page,text=tr('Form e componenti'));project_pages.add(file_page,text=tr('File e cartelle'))
        self.tree=ttk.Treeview(form_page,show='tree',selectmode='browse');tree_scroll=ttk.Scrollbar(form_page,command=self.tree.yview);tree_scroll.pack(side='right',fill='y');self.tree.configure(yscrollcommand=tree_scroll.set);self.tree.pack(fill='both',expand=True)
        self.build_file_explorer(file_page)
        self.tree.bind('<<TreeviewSelect>>',self.tree_select)
        center=ttk.Frame(main); main.add(center,weight=4)
        self.tabs=ttk.Notebook(center); self.tabs.pack(fill='both',expand=True)
        design=ttk.Frame(self.tabs); self.tabs.add(design,text=tr('Designer'))
        row=ttk.Frame(design,padding=5); row.pack(fill='x')
        self.formvar=tk.StringVar(); self.formbox=ttk.Combobox(row,textvariable=self.formvar,state='readonly',width=22); self.formbox.pack(side='left'); self.formbox.bind('<<ComboboxSelected>>',self.switch_form)
        ttk.Button(row,text='Form…',command=self.manage_forms).pack(side='left',padx=4)
        ttk.Button(row,text=tr('Anteprima — F6'),command=self.preview_form).pack(side='left',padx=4)
        edit_menu=tk.Menu(row,tearoff=False)
        for label,cmd in [(tr('Codice evento'),self.edit_event),(tr('Duplica'),self.duplicate),(tr('Elimina'),self.delete),(tr('Allinea X'),lambda:self.align('x')),(tr('Allinea Y'),lambda:self.align('y'))]:edit_menu.add_command(label=label,command=cmd)
        for label,operation in [(tr('Allinea a sinistra'),'left'),(tr('Allinea in alto'),'top'),(tr('Allinea a destra'),'right'),(tr('Allinea in basso'),'bottom'),(tr('Stessa larghezza'),'width'),(tr('Stessa altezza'),'height'),(tr('Distribuisci orizzontalmente'),'horizontal'),(tr('Distribuisci verticalmente'),'vertical')]:edit_menu.add_command(label=label,command=lambda op=operation:self.layout_selection(op))
        ttk.Menubutton(row,text=tr('Selezione ▾'),menu=edit_menu).pack(side='left',padx=4)
        self.canvas=tk.Canvas(design,bg='#e8edf5',highlightthickness=0,scrollregion=(0,0,2000,1600))
        xs=ttk.Scrollbar(design,orient='horizontal',command=self.canvas.xview); xs.pack(side='bottom',fill='x')
        ys=ttk.Scrollbar(design,orient='vertical',command=self.canvas.yview); ys.pack(side='right',fill='y')
        self.canvas.pack(fill='both',expand=True); self.canvas.configure(xscrollcommand=xs.set,yscrollcommand=ys.set)
        self.canvas.bind('<Button-1>',self.press); self.canvas.bind('<B1-Motion>',self.motion); self.canvas.bind('<ButtonRelease-1>',self.release); self.canvas.bind('<Double-Button-1>',lambda e:self.edit_event())
        self.canvas.bind('<Motion>',self.designer_cursor)
        for sequence in ('<Control-a>','<Command-a>'):self.canvas.bind(sequence,self.select_all_controls)
        self.canvas.bind('<Delete>',lambda e:self.delete()); self.canvas.bind('<BackSpace>',lambda e:self.delete())
        for key,dx,dy in [('Left',-1,0),('Right',1,0),('Up',0,-1),('Down',0,1)]: self.canvas.bind('<'+key+'>',lambda e,x=dx,y=dy:self.nudge(x,y))
        codeframe=ttk.Frame(self.tabs); self.tabs.add(codeframe,text=tr('Codice eventi'))
        cr=ttk.Frame(codeframe,padding=5); cr.pack(fill='x')
        self.code_label=tk.StringVar(value=tr('Seleziona un componente e un evento'))
        self.code_object_var=tk.StringVar()
        self.code_object=ttk.Combobox(cr,textvariable=self.code_object_var,state='readonly',width=22);self.code_object.pack(side='left',fill='x',expand=True)
        self.code_object.bind('<<ComboboxSelected>>',lambda e:self.choose_designer_object(self.code_object_var.get(),code=True))
        ttk.Label(codeframe,textvariable=self.code_label,style='Muted.TLabel',padding=(6,2)).pack(fill='x')
        self.evvar=tk.StringVar(value='Click'); self.evbox=ttk.Combobox(cr,textvariable=self.evvar,values=['Load']+list(EVENTS),state='readonly',width=14); self.evbox.pack(side='right'); self.evbox.bind('<<ComboboxSelected>>',lambda e:self.edit_event())
        ttk.Button(cr,text=tr('Applica codice'),command=self.commit_code).pack(side='right',padx=5)
        breakpoint_menu=tk.Menu(cr,tearoff=False);breakpoint_menu.add_command(label=tr('Attiva/disattiva riga · ⇧F9'),command=self.toggle_event_breakpoint);breakpoint_menu.add_command(label=tr('Rimuovi breakpoint di questo codice'),command=self.clear_event_breakpoints)
        ttk.Menubutton(cr,text=tr('Breakpoint'),menu=breakpoint_menu).pack(side='right')
        self.code=ScrolledText(codeframe,undo=True,bg='#202633',fg='#e2e8f0',insertbackground='white',font=('Menlo',self.config_data['font_size']),tabs=('32',)); self.code.pack(fill='both',expand=True)
        self.code.tag_configure('event_break',background='#f6a0a0',foreground='#111111')
        self.code.bind('<Shift-F9>',self.toggle_event_breakpoint)
        self.build_assistant(codeframe); self.code.bind('<Control-space>',self.complete); self.code.bind('<Tab>',self.tab_indent); self.code.bind('<Return>',self.autoindent)
        for tag,color in [('kw','#c792ea'),('str','#c3e88d'),('comment','#8796a8'),('num','#f78c6c')]:self.code.tag_configure(tag,foreground=color)
        self.generated=ScrolledText(self.tabs,font=('Menlo',12),wrap='none',undo=False); self.tabs.add(self.generated,text=tr('Python generato / breakpoint'))
        style_editor(self.code)
        style_editor(self.generated)
        self.generated.bind('<Double-Button-1>',self.toggle_break)
        self.generated.tag_configure('break',background='#f6a0a0',foreground='#111111')
        self.generated.tag_configure('debug_current',background='#ffe08a',foreground='#111111')
        self.build_problems();self.build_inspector();self.build_watches()
        main.add(self.right_panel,weight=0);right=inspector_area
        panel_caption(right,tr('Proprietà'))
        self.inspector_object_var=tk.StringVar()
        self.inspector_object=ttk.Combobox(right,textvariable=self.inspector_object_var,state='readonly');self.inspector_object.pack(fill='x',padx=3,pady=3)
        self.inspector_object.bind('<<ComboboxSelected>>',lambda e:self.choose_designer_object(self.inspector_object_var.get()))
        self.inspector_title=tk.StringVar(value=tr('Finestra corrente'))
        ttk.Label(right,textvariable=self.inspector_title,style='Muted.TLabel',wraplength=250).pack(anchor='w',pady=4)
        inspector_actions=ttk.Frame(right);inspector_actions.pack(side='top',fill='x',pady=4)
        self.apply_button=ttk.Button(inspector_actions,text=tr('Applica proprietà'),command=self.apply_props);self.apply_button.pack(side='left')
        actions=tk.Menu(inspector_actions,tearoff=False)
        for label,command in [(tr('Ancoraggi adattivi…'),self.configure_anchors),(tr('Rinomina intelligente…'),self.rename_selected),(tr('Configura componente…'),self.configure_component),(tr('Colore sfondo…'),lambda:self.pick_color('bg')),(tr('Colore testo…'),lambda:self.pick_color('fg')),(tr('Carattere…'),self.choose_font)]:actions.add_command(label=label,command=command)
        ttk.Menubutton(inspector_actions,text=tr('Azioni ▾'),menu=actions).pack(side='right')
        prop_area=self.build_documentation(right)
        property_tools=ttk.Frame(prop_area);property_tools.pack(fill='x',pady=2)
        self.property_order=tk.StringVar(value=tr('Per categoria'))
        order=ttk.Combobox(property_tools,textvariable=self.property_order,values=[tr('Per categoria'),tr('Alfabetico')],state='readonly',width=14);order.pack(side='left')
        order.bind('<<ComboboxSelected>>',lambda e:self.properties())
        self.property_query=tk.StringVar();property_search=ttk.Entry(property_tools,textvariable=self.property_query,width=12);property_search.pack(side='left',fill='x',expand=True,padx=2)
        ToolTip(property_search,tr('Filtra le proprietà per nome'))
        self.property_query.trace_add('write',self.property_filter)
        self.property_help=tk.StringVar(value=tr('Seleziona una proprietà per vedere il valore.'))
        ttk.Label(prop_area,textvariable=self.property_help,wraplength=260,style='PropertyHelp.TLabel',padding=5).pack(side='bottom',fill='x')
        prop_canvas=tk.Canvas(prop_area,width=260,height=320,highlightthickness=0)
        prop_scroll=ttk.Scrollbar(prop_area,command=prop_canvas.yview);prop_scroll.pack(side='right',fill='y');prop_canvas.pack(side='left',fill='both',expand=True);prop_canvas.configure(yscrollcommand=prop_scroll.set)
        self.propbox=ttk.Frame(prop_canvas);prop_window=prop_canvas.create_window(0,0,window=self.propbox,anchor='nw')
        self.propbox.bind('<Configure>',lambda e:prop_canvas.configure(scrollregion=prop_canvas.bbox('all')))
        prop_canvas.bind('<Configure>',lambda e:prop_canvas.itemconfigure(prop_window,width=e.width))
        self.propvars={}
        self.log_panel=bottom=ttk.Frame(vertical)
        bottom.columnconfigure(0,weight=1);bottom.rowconfigure(1,weight=1)
        br=ttk.Frame(bottom,padding=(6,3));br.grid(row=0,column=0,sticky='ew')
        ttk.Label(br,text='OUTPUT / DEBUG',style='Title.TLabel').pack(side='left',padx=5)
        debug_menu=tk.Menu(br,tearoff=False)
        for label,cmd in [(tr('Continua'),lambda:self.debug_cmd('continue')),(tr('Passo'),lambda:self.debug_cmd('next')),(tr('Entra'),lambda:self.debug_cmd('step')),('Stack',lambda:self.debug_cmd('where')),(tr('Locali'),lambda:self.debug_cmd('pp locals()'))]:debug_menu.add_command(label=label,command=cmd)
        debug_menu.add_separator();debug_menu.add_command(label=tr('Watch'),command=lambda:self.tabs.select(self.watch_page))
        ttk.Menubutton(br,text='Debug ▾',menu=debug_menu).pack(side='left')
        self.debug_location=tk.StringVar(value=tr('Debug non avviato'))
        self.debug_jump=ttk.Button(br,text=tr('Mostra riga'),command=self.show_debug_position,state='disabled');self.debug_jump.pack(side='left',padx=4)
        ttk.Button(br,text=tr('Ispettore'),command=lambda:self.tabs.select(self.inspector_page)).pack(side='left')
        ttk.Label(bottom,textvariable=self.debug_location).grid(row=3,column=0,sticky='ew',padx=8)
        ttk.Button(br,text=tr('Chiudi log'),command=lambda:self.show_log(False)).pack(side='right')
        ttk.Button(br,text=tr('Pulisci'),command=self.clear_log).pack(side='right',padx=4)
        self.log=ScrolledText(bottom,height=5,bg='#151a23',fg='#dbe6ef',font=('Menlo',11));self.log.grid(row=1,column=0,sticky='nsew');style_editor(self.log)
        self.command=ttk.Entry(bottom);self.command.grid(row=2,column=0,sticky='ew');self.command.bind('<Return>',self.console_command)
        for sequence in ('<Configure>','<B1-Motion>','<ButtonRelease-1>'):vertical.bind(sequence,lambda e:self.after_idle(self.clamp_log),add='+')
        for sequence in ('<Command-j>','<Control-j>'):self.bind(sequence,lambda e:self.toggle_log())
        self.install_layout_guards()
    def filter_palette(self):
        query=self.palette_query.get().strip().casefold()
        selected=self.palette.get(self.palette.curselection()[0]) if self.palette.curselection() else None
        self.palette.delete(0,'end')
        family=self.palette_family.get();reg=registry(self.project);family_of={kind:component_family(kind,self.project,reg) for kind in self.kinds};families=[tr('Tutte le famiglie')]+sorted(set(family_of.values()))
        self.family_box.configure(values=families)
        if family not in families:family=tr('Tutte le famiglie');self.palette_family.set(family)
        for kind in self.kinds:
            if query in kind.casefold() and (family==tr('Tutte le famiglie') or family_of[kind]==family):self.palette.insert('end',kind)
        if selected in self.palette.names:self.palette.selection_set(self.palette.names.index(selected))

    def refresh(self):
        self.render_watches()
        self.activate_project_environment()
        if self.selected is None:self.selection_names=set()
        if self.code_target is None:self.reset_code_context()
        self.dismiss_completion()
        self.kinds=list(KINDS)+list(registry(self.project))
        self.filter_palette()
        self.formbox['values']=[f['name'] for f in self.project['forms']]; self.formvar.set(self.form['name'])
        self.tree.delete(*self.tree.get_children())
        for i,f in enumerate(self.project['forms']):
            self.tree.insert('','end',iid='f:'+str(i),text=f['name'],image=self.palette.image('Frame'),open=True)
            for w in ordered_widgets(f):
                parent='w:'+w['parent'] if w.get('parent') and w['parent']!=f['name'] else 'f:'+str(i)
                self.tree.insert(parent,'end',iid='w:'+w['name'],text=w['name']+' : '+w['kind']+(' ['+w['page']+']' if w.get('page') else ''),image=self.palette.image(w['kind']),open=True)
        self.refresh_project_files()
        self.draw(); self.properties(); self.update_source()
    def draw(self):
        c=self.canvas; c.delete('all'); f=self.form; ox=30; oy=45
        selected_names={w['name'] for w in self.selected_controls()}
        item=self.selected if self.selected is not None else f
        self.selection_status.set(item['name']+'  •  '+str(item.get('x',0))+', '+str(item.get('y',0))+'  •  '+str(item['width'])+' × '+str(item['height']))
        c.create_rectangle(ox-2,oy-29,ox+f['width']+2,oy-2,fill='#153d73',outline='#404040')
        c.create_text(ox+8,oy-16,text=f['title']+'  ('+f['name']+')',anchor='w',fill='white',font=('Helvetica',11,'bold'))
        c.create_text(ox+f['width']-15,oy-16,text='×',fill='white',font=('Helvetica',14))
        c.create_rectangle(ox+5,oy+6,ox+f['width']+5,oy+f['height']+6,fill='#cfd8e6',outline='')
        c.create_rectangle(ox,oy,ox+f['width'],oy+f['height'],fill=f['bg'],outline='#909baa',tags='form')
        grid=max(1,int(self.config_data['grid']))
        if grid>=5:
            for x in range(ox,ox+min(f['width'],1600),grid):
                for y in range(oy,oy+min(f['height'],1200),grid): c.create_line(x,y,x+1,y,fill='#bfc6ce')
        for w in self.displayed_widgets():
            wx,wy=widget_origin(f,w);x=ox+wx; y=oy+wy; width=w['width']; height=w['height']; p=w['props']; k=w['kind']
            bg=p.get('bg','#ffffff' if k in ('Entry','Text','Listbox','Combobox','Spinbox') else '#e4e8ee')
            try:
                c.create_rectangle(x,y,x+width,y+height,fill=bg,outline='#8190a1',tags=('widget',w['name']))
                text=p.get('text',k if k not in ('Entry','Text','Canvas','Frame') else '')
                if k in ('Checkbutton','Radiobutton'):text=('☐ ' if k=='Checkbutton' else '○ ')+text
                c.create_text(x+7,y+height/2,text=text,anchor='w',width=max(1,width-12),fill=p.get('fg','#1c2430'),font=p.get('font','Helvetica 12'),tags=('widget',w['name']))
            except tk.TclError: pass
            if k=='DatabaseView':
                c.create_rectangle(x,y,x+width,y+32,fill='#dce8ff',outline='#8190a1')
                c.create_text(x+8,y+16,text='Database • '+str(p.get('backend','sqlite')).upper()+tr(' • anteprima'),anchor='w',fill='#243b63')
                for col,title in enumerate(('id','nome','valore')):
                    cx=x+col*width/3;c.create_text(cx+8,y+48,text=title,anchor='w',fill='#455574')
                    c.create_line(cx,y+32,cx,y+height,fill='#c8d2df')
                for row in range(3):c.create_line(x,y+62+row*28,x+width,y+62+row*28,fill='#c8d2df')
                c.create_text(x+8,y+height-15,text=tr('Connetti e scegli la tabella durante l’esecuzione'),anchor='w',width=max(1,width-16),fill='#62718a')
            if k in TABS:
                pages=p.get('pages',[tr('Pagina 1'),tr('Pagina 2')]);active=self.current_container_pages().get(w['name'],pages[0])
                c.create_rectangle(x,y,x+width,y+26,fill='#dce8ff',outline='#8190a1')
                c.create_text(x+8,y+13,text=' | '.join(('['+page+']' if page==active else page) for page in pages),anchor='w',fill='#243b63',width=max(1,width-16))
            if w['name'] in selected_names:
                c.create_rectangle(x-2,y-2,x+width+2,y+height+2,outline='#202020',width=1,dash=(2,2))
                if self.selected is not w:continue
                for hx,hy in ((x,y),(x+width/2,y),(x+width,y),(x,y+height/2),(x+width,y+height/2),(x,y+height),(x+width/2,y+height)):
                    c.create_rectangle(hx-3,hy-3,hx+3,hy+3,fill='#202020',outline='white')
                c.create_rectangle(x+width-5,y+height-5,x+width+5,y+height+5,fill='#202020',outline='white',tags='handle')
    def tree_select(self,event=None):
        ids=self.tree.selection()
        if not ids:return
        self.selection_names=set()
        self.commit_code(); ident=ids[0]
        if ident.startswith('f:'):self.form_index=int(ident[2:]); self.selected=None
        else:
            for i,f in enumerate(self.project['forms']):
                for w in f['widgets']:
                    if 'w:'+w['name']==ident:self.form_index=i; self.selected=w
        if self.selected:self.reveal_widget(self.selected)
        self.formvar.set(self.form['name']); self.draw(); self.properties()
    def switch_form(self,event=None):
        self.selection_names=set()
        self.commit_code(); self.form_index=self.formbox.current(); self.selected=None; self.draw(); self.properties()
    def properties(self):
        for w in self.propbox.winfo_children():w.destroy()
        self.propvars={}; obj=self.selected if self.selected is not None else self.form
        self.inspector_title.set(obj['name']+' • '+obj.get('kind',tr('Finestra'))+(' • '+str(len(self.selected_controls()))+tr(' selezionati') if len(self.selected_controls())>1 else ''))
        self.update_documentation(obj)
        names=[item['name'] for form in self.project['forms'] for item in [form]+form['widgets']]
        self.inspector_object.configure(values=names);self.inspector_object_var.set(obj['name'])
        self.code_object.configure(values=names)
        if self.code_target and not self.code_target[2]:self.code_object_var.set(self.code_target[0]['name'])
        values={k:obj[k] for k in ('name','x','y','width','height','title','bg') if k in obj}
        values=self.container_properties(obj,values)
        if self.selected is not None:values.update(obj['props'])
        self.property_rows={};self.property_headers=[]
        groups={tr('Identità'):('name','title','text'),tr('Disposizione'):('parent','page','x','y','width','height'),tr('Aspetto e comportamento'):()}
        ordered=list(values)
        categorized=self.property_order.get()==tr('Per categoria')
        if not categorized:ordered=sorted(ordered,key=str.casefold)
        else:ordered=[key for keys in groups.values() for key in keys if key in values]+[key for key in values if all(key not in keys for keys in groups.values())]
        row=0;previous=None
        for key in ordered:
            val=values[key];category=next((title for title,keys in groups.items() if key in keys),tr('Aspetto e comportamento'))
            if categorized and category!=previous:
                header=ttk.Label(self.propbox,text=category,style='PropertyGroup.TLabel',padding=(4,3));header.grid(row=row,column=0,columnspan=2,sticky='ew');self.property_headers.append(header);row+=1;previous=category
            label=ttk.Label(self.propbox,text=key,width=11,style='PropertyName.TLabel',padding=(4,2));label.grid(row=row,column=0,sticky='nsew')
            var=tk.StringVar(value=json.dumps(val,ensure_ascii=False) if isinstance(val,(list,dict)) else str(val));self.propvars[key]=var
            if self.container_property_entry(key,var,row,obj):entry=self.propbox.grid_slaves(row=row,column=1)[0]
            else:
                entry=ttk.Entry(self.propbox,textvariable=var,width=16);entry.grid(row=row,column=1,sticky='ew');entry.bind('<Return>',lambda e:self.apply_props())
            if key=='name':entry.configure(state='readonly')
            entry.bind('<FocusIn>',lambda e,k=key:self.describe_property(k),add='+')
            self.property_rows[key]=(label,entry);row+=1
        self.page_preview_selector(obj,row)
        self.property_help.set(tr('Seleziona una proprietà per vedere il valore.'))
        self.property_filter()
        self.propbox.columnconfigure(1,weight=1)
    def apply_props(self):
        obj=self.selected if self.selected is not None else self.form; candidate=copy.deepcopy(obj)
        try:
            for k,v in self.propvars.items():
                value=v.get()
                if k in ('x','y','width','height'):candidate[k]=int(value)
                elif k in ('parent','page') and self.selected is not None:candidate[k]=value
                elif k in candidate:candidate[k]=value
                else:
                    previous=candidate['props'].get(k)
                    if isinstance(previous,bool):value=value.lower() in ('true','1','yes')
                    elif isinstance(previous,int):value=int(value)
                    elif isinstance(previous,float):value=float(value)
                    elif isinstance(previous,(list,dict)):value=json.loads(value)
                    if k in ('bg','fg','activebackground','selectbackground'):self.winfo_rgb(value)
                    if k=='values' and isinstance(value,str):value=json.loads(value)
                    candidate['props'][k]=value
            if 'bg' in candidate:self.winfo_rgb(candidate['bg'])
            if candidate['name']!=obj['name']:
                raise ValueError(tr('Per rinominare usa Azioni → Rinomina intelligente…'))
            probe=copy.deepcopy(self.project)
            if self.selected is None:probe['forms'][self.form_index]=candidate
            else:probe['forms'][self.form_index]['widgets'][self.form['widgets'].index(obj)]=candidate
            validate(probe)
            if self.selected is not None and candidate['kind'] in KINDS:
                cls=getattr(ttk if candidate['kind'] in ('Combobox','Progressbar') else tk,candidate['kind'])
                test=cls(self,**candidate['props']); test.destroy()
            self.checkpoint(); obj.clear(); obj.update(candidate)
            if self.selected:self.reveal_widget(self.selected)
            self.refresh()
        except Exception as exc:messagebox.showerror(tr('Proprietà non valide'),str(exc))
    def pick_color(self,key):
        if key in self.propvars:
            value=colorchooser.askcolor(parent=self)[1]
            if value:self.propvars[key].set(value); self.apply_props()
    def unique(self,prefix):
        names={o['name'] for f in self.project['forms'] for o in [f]+f['widgets']}; n=1
        while prefix+str(n) in names:n+=1
        return prefix+str(n)
    def add_widget(self,dependencies_checked=False,kind_override=None):
        selection=self.palette.curselection()
        if not selection and not kind_override:return
        k=kind_override or self.palette.get(selection[0])
        if not dependencies_checked and self.config_data.get('dependency_before_insert',True) and dependency_plan(self.project,k):
            return self.open_dependencies(k,on_ready=lambda:self.add_widget(True,k),allow_skip=True)
        name=simpledialog.askstring(tr('Nome componente'),tr('Nome Python del componente:'),initialvalue=self.unique(k),parent=self)
        if name is None:return
        names={o['name'] for f in self.project['forms'] for o in [f]+f['widgets']}
        if not identifier(name) or name in names:return messagebox.showerror(tr('Nome'),tr('Nome Python non valido o già utilizzato.'))
        props={}
        if k in ('Button','Label','Checkbutton','Radiobutton'):props['text']=name
        if k not in ('Combobox','Progressbar'):props.update(bg='#ffffff' if k in ('Entry','Text','Listbox','Spinbox') else '#e4e8ee')
        if k not in ('Frame','Canvas','Progressbar','Combobox'):props.update(fg='#182230',font='Helvetica 12')
        if k=='Combobox':props={'values':[tr('Prima'),tr('Seconda')],'state':'readonly'}
        if k=='Progressbar':props={'value':40,'maximum':100}
        if k in ('Button','Entry','Text','Checkbutton','Radiobutton','Listbox','Combobox','Scale','Spinbox'):props['state']='normal' if k!='Combobox' else 'readonly'
        if k in registry(self.project):props=copy.deepcopy(registry(self.project)[k].get('defaults',{}))
        container=self.selected if self.selected and self.selected['kind'] in CONTAINERS else None
        width,height=design_size(k,external=k in registry(self.project))
        self.checkpoint(); self.selected={'name':name,'kind':k,'x':30,'y':30,'width':width,'height':height,'props':props,'events':{}}
        if container:
            if container['kind'] in TABS:container['props'].setdefault('pages',copy.deepcopy(registry(self.project)[container['kind']]['defaults']['pages']))
            self.selected['parent']=container['name']
            if container['kind'] in TABS:self.selected['page']=self.current_container_pages().get(container['name'],container['props']['pages'][0])
        self.form['widgets'].append(self.selected); self.refresh()
    def add_form(self):
        name=simpledialog.askstring(tr('Nuova finestra'),tr('Nome Python:'),initialvalue=self.unique('Form'),parent=self)
        if name is None:return
        if not identifier(name) or any(name==o['name'] for f in self.project['forms'] for o in [f]+f['widgets']):return messagebox.showerror(tr('Nome'),tr('Nome non valido o duplicato'))
        self.commit_code(); self.checkpoint(); self.project['forms'].append({'name':name,'title':name,'width':640,'height':440,'bg':'#f0f0f0','widgets':[],'events':{}}); self.form_index=len(self.project['forms'])-1; self.selected=None; self.refresh()
    def press(self,e):
        self.canvas.focus_set(); self.commit_code(); x=self.canvas.canvasx(e.x)-30; y=self.canvas.canvasy(e.y)-45
        resize=False; target=None
        if self.selected:
            w=self.selected
            wx,wy=widget_origin(self.form,w)
            resize=resize_handle(wx,wy,w['width'],w['height'],x,y)
            if resize:target=w
        if target is None:
            for w in reversed(self.displayed_widgets()):
                wx,wy=widget_origin(self.form,w)
                if wx<=x<=wx+w['width'] and wy<=y<=wy+w['height']:target=w; break
        names={w['name'] for w in self.selected_controls()}
        if target and e.state&1:
            if target['name'] in names:names.remove(target['name']);target=next((w for w in self.form['widgets'] if w['name'] in names),None)
            else:names.add(target['name'])
            resize=False
        elif not target:names=set()
        elif target['name'] not in names:names={target['name']}
        self.selected=target;self.selection_names=names
        self.group_drag=[copy.deepcopy(w) for w in selected_roots(self.form,self.selected_controls())]
        if target:self.drag=(x,y,copy.deepcopy(target),resize);self.drag_checkpoint=False
        self.draw(); self.properties()
    def motion(self,e):
        if not self.drag or not self.selected:return
        x,y,original,resize=self.drag; dx=self.canvas.canvasx(e.x)-30-x; dy=self.canvas.canvasy(e.y)-45-y; grid=max(1,int(self.config_data['grid']))
        if not dx and not dy:return
        if not self.drag_checkpoint:self.checkpoint();self.drag_checkpoint=True
        def snap(n):return round(n/grid)*grid
        if resize:self.selected.update(resized_geometry(original,resize,dx,dy,grid))
        else:
            changes=moved_geometry(self.group_drag,snap(dx),snap(dy))
            for w in self.form['widgets']:
                if w['name'] in changes:w.update(changes[w['name']])
        self.draw()
    def release(self,e):
        if self.drag:self.drag=None; self.properties(); self.update_source()
    def nudge(self,x,y):
        widgets=selected_roots(self.form,self.selected_controls())
        if widgets:
            changes=moved_geometry(widgets,x,y);self.checkpoint()
            for w in widgets:w.update(changes[w['name']])
            self.draw();self.properties();self.update_source()
    def duplicate(self):
        if self.selected:self.duplicate_selection()
    def delete(self):
        if self.selected:self.delete_selection()
        elif len(self.project['forms'])>1 and messagebox.askyesno(tr('Elimina finestra'),tr('Eliminare la finestra e tutti i suoi componenti?')):
            self.commit_code();self.checkpoint();del self.project['forms'][self.form_index];self.form_index=0;self.code_target=None;self.refresh()
    def align(self,axis):
        if self.selected:
            self.checkpoint(); self.selected[axis]=0; self.draw(); self.properties(); self.update_source()
    def commit_code(self):
        if not self.code_target:return
        obj,key,global_=self.code_target; value=self.code.get('1.0','end-1c')
        dest=obj if global_ else obj.setdefault('events',{})
        if value!=dest.get(key,''):
            self.checkpoint();self.remap_event_breakpoints(obj,key,global_,dest.get(key,''),value);dest[key]=value
        self.paint_event_breakpoints();self.update_source()
    def edit_event(self):
        self.commit_code(); obj=self.selected if self.selected is not None else self.form; event=self.evvar.get()
        self.code.configure(state='normal');self.code_target=(obj,event,False);self.code_object_var.set(obj['name']); self.code_label.set(obj['name']+' → '+event+'(self, event=None)')
        self.code.delete('1.0','end'); self.code.insert('1.0',obj.get('events',{}).get(event,'pass')); self.code.edit_reset();self.tabs.select(1); self.highlight(); self.code.focus_set(); self.update_assistant()
    def global_code(self,key):
        self.commit_code();self.code.configure(state='normal');self.code_object_var.set(tr('Codice progetto')); self.code_target=(self.project,key,True); self.code_label.set(tr('Progetto → ')+key); self.code.delete('1.0','end'); self.code.insert('1.0',self.project.get(key,'')); self.code.edit_reset();self.tabs.select(1); self.highlight(); self.update_assistant()
    def highlight(self,widget=None):
        target=self.code if widget is None else widget
        for tag in ('kw','str','comment','num'):target.tag_remove(tag,'1.0','end')
        try:
            for tok in tokenize.generate_tokens(io.StringIO(target.get('1.0','end-1c')).readline):
                tag='kw' if keyword.iskeyword(tok.string) else {tokenize.STRING:'str',tokenize.COMMENT:'comment',tokenize.NUMBER:'num'}.get(tok.type)
                if tag:target.tag_add(tag,f'{tok.start[0]}.{tok.start[1]}',f'{tok.end[0]}.{tok.end[1]}')
        except (tokenize.TokenError,IndentationError,SyntaxError):pass
        if target is self.code:self.paint_event_breakpoints()
        else:
            for tag in ('break','debug_current','sel'):target.tag_raise(tag)
    def tab_indent(self,event):
        if self.assist_popup:return self.accept_completion()
        self.code.insert('insert','    '); return 'break'
    def autoindent(self,event):
        if self.assist_popup:return self.accept_completion()
        line=self.code.get('insert linestart','insert'); indent=re.match(r'\s*',line).group(); self.code.insert('insert','\n'+indent+('    ' if line.rstrip().endswith(':') else '')); return 'break'
    def update_source(self):
        try:
            source=getattr(self,'debug_source',None) or generate(self.project)
            if self.generated.get('1.0','end-1c')!=source:
                self.generated.configure(state='normal');self.generated.delete('1.0','end');self.generated.insert('1.0',source);self.highlight(self.generated)
            self.generated.tag_remove('break','1.0','end')
            markers=getattr(self,'session_breaks',self.breaks) if getattr(self,'debug_source',None) else set(self.breaks)|resolve_breakpoints(self.project,source)[0]
            for line in markers:self.generated.tag_add('break',f'{line}.0',f'{line}.end')
            self.generated.configure(state='disabled');self.paint_debug_position(); self.status.set(tr('Pronto • ')+(tr('* modificato • ') if json.dumps(self.project,sort_keys=True)!=self.saved_state else '')+(str(self.path) if self.path else tr('Progetto senza nome')))
        except Exception as exc:self.status.set(tr('Codice da correggere: ')+str(exc))
    def toggle_break(self,e):
        if getattr(self,'debug_source',None):
            self.write_log(tr('Arresta il debug prima di cambiare i breakpoint.')+'\n');return 'break'
        line=int(self.generated.index('@%s,%s'%(e.x,e.y)).split('.')[0])
        if line in self.breaks:self.breaks.remove(line)
        else:self.breaks.add(line)
        self.update_source(); return 'break'
    def dirty_guard(self):
        if not self.close_project_editors():return False
        self.commit_code()
        if json.dumps(self.project,sort_keys=True)==self.saved_state:return True
        answer=messagebox.askyesnocancel(tr('Modifiche non salvate'),tr('Salvare le modifiche prima di proseguire?'))
        if answer is None:return False
        if not answer and hasattr(self,'history_jobs') and self.config_data.get('local_history',True):self.queue_local_snapshot('discarded')
        return self.save() if answer else True
    def new(self):
        self.choose_new_project()
    def new_from_template(self,project):
        if not self.dirty_guard():return
        self.project=copy.deepcopy(project); self.path=None;
        self.history_session=uuid.uuid4().hex;self.history_last_queued=None;self.recovery_unsaved=False
        self.form_index=0; self.selected=None; self.code_target=None; self.history=[]; self.future=[]; self.breaks=set(); self.saved_state=json.dumps(new_project(),sort_keys=True); self.code.delete('1.0','end'); self.refresh()
    def open_project(self):
        if not self.dirty_guard():return
        path=filedialog.askopenfilename(filetypes=[('TkVisualFoundry project','*.vtk.json'),('JSON','*.json')])
        if not path:return
        try:
            p=load(path)
            if p.get('environment',{}).get('managed'):
                from project_environment import environment_python
                environment_python(Path(path).parent)
        except Exception as exc:return messagebox.showerror(tr('Apertura'),str(exc))
        self.recovery_unsaved=False
        self.history_session=uuid.uuid4().hex;self.history_last_queued=None
        self.project=p; self.path=Path(path); self.form_index=0; self.selected=None; self.code_target=None; self.history=[]; self.future=[]; self.breaks=set(); self.saved_state=json.dumps(p,sort_keys=True); self.code.delete('1.0','end'); self.refresh()
    def save(self,as_new=False):
        self.commit_code()
        path=self.path
        if as_new or path is None:
            s=filedialog.asksaveasfilename(defaultextension='.vtk.json',filetypes=[('TkVisualFoundry project','*.vtk.json')]); path=Path(s) if s else None
        if path is None:return False
        if not as_new and getattr(self,'recovery_unsaved',False) and path==self.path and path.exists():path=recovered_path(self.recovery_original)
        if self.path and path.resolve().parent!=self.path.resolve().parent and (self.project.get('files') or self.project.get('deployment',{}).get('icon') or self.project.get('environment',{}).get('managed')):
            messagebox.showinfo(tr('File di progetto'),tr('Per mantenere i percorsi relativi, copia prima la cartella del progetto nella nuova destinazione e aprila da lì.'));return False
        try:
            # Save even unfinished code, allowing recovery after syntax errors.
            atomic_write_text(path,json.dumps(self.project,indent=2,ensure_ascii=False))
            self.path=path;self.recovery_unsaved=False; self.saved_state=json.dumps(self.project,sort_keys=True);
            if hasattr(self,'history_jobs') and self.config_data.get('local_history',True):self.queue_local_snapshot('saved')
            self.update_source(); self.refresh_project_files(); return True
        except OSError as exc:messagebox.showerror(tr('Salvataggio'),str(exc)); return False
    def check(self):
        self.show_log(True)
        self.commit_code()
        try:compile(generate(self.project),'application.py','exec'); self.write_log(tr('✓ Sintassi e modello validi.\n')); return True
        except Exception as exc:self.write_log(tr('ERRORE: ')+str(exc)+'\n'); messagebox.showerror(tr('Verifica'),str(exc)); return False
    def export(self):
        if not self.check():return
        p=filedialog.asksaveasfilename(defaultextension='.py',initialfile='application.py')
        if p:
            try:
                Path(p).write_text(generate(self.project),encoding='utf-8'); self.write_requirements(Path(p).parent); self.write_log(tr('Esportato: ')+p+'\n')
            except OSError as exc:messagebox.showerror(tr('Esportazione'),str(exc))
    def write_log(self,s):self.log.insert('end',s); self.log.see('end')
    def clear_log(self):self.log.delete('1.0','end')
    def launch(self,args,cwd=None):
        if self.proc and self.proc.poll() is None:return messagebox.showwarning(tr('Processo attivo'),tr('Arresta il processo corrente prima di avviarne un altro.'))
        try:
            validate_interpreter(args[0])
            self.proc=subprocess.Popen(args,cwd=cwd,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,bufsize=0,env={**os.environ,'PYTHONUNBUFFERED':'1'})
        except (OSError,ValueError) as exc:return messagebox.showerror(tr('Avvio'),str(exc))
        self.show_log(True)
        proc=self.proc; self.write_log('\n$ '+ ' '.join(map(str,args))+'\n')
        def read():
            import codecs
            decoder=codecs.getincrementaldecoder('utf-8')('replace')
            while True:
                data=os.read(proc.stdout.fileno(),4096)
                if not data:break
                self.messages.put((proc,decoder.decode(data),False))
            self.messages.put((proc,decoder.decode(b'',final=True),False)); self.messages.put((proc,tr('\n[Processo terminato: {v0}]\n', v0=f'{proc.wait()}'),True))
        threading.Thread(target=read,daemon=True).start()
    def poll(self):
        try:
            while True:
                process,text,finished=self.messages.get_nowait();self.write_log(text);self.observe_debug(process,text,finished)
                if finished:self.inspector_finished(process)
        except queue.Empty:pass
        self.poll_inspector();self.after(70,self.poll)
    def runtime_file(self):
        path=Path(self.temp.name)/'application.py';source=generate(self.project)
        if self.path:source=source.replace(source.splitlines()[0], 'import sys; sys.path.insert(0, '+repr(str(self.path.resolve().parent))+')',1)
        path.write_text(source,encoding='utf-8');return path
    def run(self,dependencies_checked=False):
        if not dependencies_checked and self.config_data.get('dependency_before_run',True) and dependency_plan(self.project):
            return self.open_dependencies(on_ready=lambda:self.run(True))
        if self.proc and self.proc.poll() is None:return messagebox.showwarning(tr('Processo attivo'),tr('Arresta prima il processo corrente.'))
        if self.check():
            try:
                path=self.runtime_file();args=self.inspector_args(path) or [self.config_data['python'],'-u',str(path)]
            except (OSError,ValueError) as exc:return messagebox.showerror(tr('Ispettore'),str(exc))
            self.launch(args,cwd=str(self.path.parent if self.path else BASE));self.inspector_launched(self.proc)
    def debug(self,dependencies_checked=False):
        if not dependencies_checked and self.config_data.get('dependency_before_run',True) and dependency_plan(self.project):
            return self.open_dependencies(on_ready=lambda:self.debug(True))
        if self.proc and self.proc.poll() is None:return messagebox.showwarning(tr('Processo attivo'),tr('Arresta prima il processo corrente.'))
        if not self.check():return
        args=[self.config_data['python'],'-u','-m','pdb']
        try:
            path=self.runtime_file();self.prepare_session_breakpoints(path.read_text(encoding='utf-8'));instrumented=self.inspector_args(path,debug=True)
            for line in sorted(self.session_breaks):args+=['-c',f'break {line}']
        except (OSError,ValueError) as exc:return messagebox.showerror(tr('Ispettore'),str(exc))
        self.start_debug_view(path);args.append(str(path));self.launch(instrumented or args,cwd=str(self.path.parent if self.path else BASE));self.debug_process=self.proc;self.inspector_launched(self.proc)
        if self.proc is None or self.proc.poll() is not None:
            self.debug_source=None;self.debug_output=None;self.debug_process=None;self.debug_location.set(tr('Debug non avviato'))
        else:self.update_source()
        self.write_log(tr('Debug pdb: continue, next, step, pp espressione, where, break N, quit.\nLa GUI si blocca intenzionalmente ai breakpoint.\n')); self.command.focus_set()
    def debug_cmd(self,text):
        if self.proc and self.proc.poll() is None:
            try:
                self.proc.stdin.write((text+'\n').encode()); self.proc.stdin.flush()
                if getattr(self,'debug_process',None) is self.proc:self.debug_resuming(text)
            except (OSError,ValueError):pass
    def console_command(self,event=None):
        command=self.command.get(); self.command.delete(0,'end'); self.write_log('> '+command+'\n'); self.debug_cmd(command)
    def stop(self):
        if self.proc and self.proc.poll() is None:
            proc=self.proc; proc.terminate()
            def kill():
                if proc.poll() is None:proc.kill()
            self.after(1500,kill)
    def package(self,dependencies_checked=False):
        return self.deploy_project()
    def write_requirements(self,directory):
        (directory/'requirements-visualtk.txt').write_text('\n'.join(requirements(self.project))+'\n',encoding='utf-8')
    def install_project_dependencies(self):
        self.commit_code();return self.open_dependencies()
    def import_component(self):
        path=filedialog.askopenfilename(title=tr('Descrittore componente visuale'),filetypes=[('TkVisualFoundry component','*.vtk-component.json'),('JSON','*.json')])
        if not path:return
        try:
            data=json.loads(Path(path).read_text(encoding='utf-8'));name=data['name'];desc=descriptor(data)
            if name in registry(self.project):return messagebox.showinfo(tr('Componente'),tr('Componente già disponibile nella palette.'))
            if not identifier(name) or name in KINDS:raise ValueError(tr('Nome componente non valido'))
            self.commit_code();self.checkpoint();self.project.setdefault('components',{})[name]=desc;self.refresh()
            messagebox.showinfo(tr('Componente aggiunto'),tr('Il componente è nella palette. Installa le sue dipendenze prima di avviarlo. Il modulo non viene importato durante il design.'))
        except Exception as exc:messagebox.showerror(tr('Importazione componente'),str(exc))
    def component_manager(self):
        win=tk.Toplevel(self);win.title(tr('Componenti visuali'));win.geometry('720x450');text=ScrolledText(win,wrap='word');text.pack(fill='both',expand=True)
        for name,desc in registry(self.project).items():
            text.insert('end',name+' — '+desc.get('description','')+'\n'+desc['module']+'.'+desc['class']+tr('\nDipendenze: ')+', '.join(desc.get('requirements',[]))+'\n\n')
        text.insert('end',tr('Per aggiungere un widget di una libreria esterna importa un descrittore JSON. Esempio in examples/CTkButton.vtk-component.json. La classe deve accettare master e le proprietà defaults, e supportare place e bind. Le dipendenze sono installate solo su richiesta.'));text.configure(state='disabled')

    def help(self):self.help_topic(tr('Guida rapida'))
    def close(self):
        if self.environment_busy:
            self.environment_window.lift();return
        wizard=getattr(self,'dependency_window',None)
        if wizard and wizard.winfo_exists() and wizard.busy:
            wizard.lift();return messagebox.showinfo(tr('Installazione in corso'),tr('Interrompi o attendi il wizard PIP prima di chiudere l’IDE.'))
        if not self.dirty_guard():return
        self.stop()
        if self.proc and self.proc.poll() is None:
            try:self.proc.wait(timeout=2)
            except subprocess.TimeoutExpired:self.proc.kill(); self.proc.wait()
        search_window=getattr(self,'global_search_window',None)
        if search_window is not None and search_window.winfo_exists():search_window.close()
        viewer=getattr(self,'data_viewer_window',None)
        if viewer is not None and viewer.winfo_exists():viewer.close()
        self.finish_local_history();self.stop_preview();self.temp.cleanup(); self.destroy()

HELP=tr('TKVISUALFOUNDRY — Guida rapida\n\n1. Inserisci un controllo dalla palette, con doppio clic o Invio.\n2. Modifica le proprietà e premi Applica proprietà.\n3. Doppio clic sul controllo per aprire il codice evento.\n4. Digita messagebox., tk. o self. per i suggerimenti.\n5. Salva il progetto e premi F5.\n\nPIP prepara automaticamente i pacchetti necessari.\nProgetto → Configurazione consente di scegliere lingua, Python e preferenze.\nVista gestisce log e colori. Help contiene le guide dettagliate.\n\nLa lingua dell’interfaccia cambia dopo il riavvio. Il codice e i testi dei progetti restano invariati.')

if __name__=='__main__':
    Studio().mainloop()
