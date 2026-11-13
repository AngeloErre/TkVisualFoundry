"""Compact VB-style desktop chrome, tooltips and object navigation."""
import tkinter as tk
from tkinter import ttk
from i18n import tr

CLASSIC={'background':'#d4d0c8','foreground':'#202020','surface':'#ffffff','accent':'#153d73',
         'editor_bg':'#ffffff','editor_fg':'#202020','canvas':'#808080'}

def panel_caption(parent,text):
    bar=ttk.Frame(parent,style='Caption.TFrame');bar.pack(fill='x')
    ttk.Label(bar,text=text,style='Caption.TLabel',padding=(6,4)).pack(side='left')
    return bar

class ToolTip:
    def __init__(self,widget,text):
        self.widget=widget;self.text=text;self.timer=None;self.tip=None
        widget.bind('<Enter>',self.schedule,add='+');widget.bind('<Leave>',self.hide,add='+')
        widget.bind('<ButtonPress>',self.hide,add='+');widget.bind('<Destroy>',self.hide,add='+')
    def schedule(self,event=None):
        self.hide();self.timer=self.widget.after(650,self.show)
    def show(self):
        self.timer=None
        if not self.widget.winfo_exists():return
        root=self.widget.winfo_toplevel()
        self.tip=tk.Label(root,text=self.text,padx=6,pady=4,background='#ffffdf',foreground='#202020',relief='solid',borderwidth=1,takefocus=False)
        self.tip.update_idletasks()
        x=min(self.widget.winfo_rootx()-root.winfo_rootx(),root.winfo_width()-self.tip.winfo_reqwidth()-8)
        y=min(self.widget.winfo_rooty()-root.winfo_rooty()+self.widget.winfo_height()+3,root.winfo_height()-self.tip.winfo_reqheight()-8)
        self.tip.place(x=max(0,x),y=max(0,y));self.tip.lift()
    def hide(self,event=None):
        if self.timer:
            try:self.widget.after_cancel(self.timer)
            except tk.TclError:pass
            self.timer=None
        if self.tip:
            try:self.tip.destroy()
            except tk.TclError:pass
            self.tip=None

TOOL_GLYPHS={
    'new':('11110','10011','10001','10001','11111'),
    'open':('11000','11111','10001','10001','11111'),
    'save':('11111','10101','11111','10001','11111'),
    'undo':('01000','11110','01001','00001','00110'),
    'redo':('00010','01111','10010','10000','01100'),
    'design':('11111','10101','11111','10001','11111'),
    'code':('01010','10001','00000','10001','01010'),
}


def tool_icon(master,name):
    image=tk.PhotoImage(master=master,width=14,height=14)
    for y,row in enumerate(TOOL_GLYPHS[name]):
        for x,bit in enumerate(row):
            if bit=='1':image.put('#295282',to=(2+x*2,2+y*2,4+x*2,4+y*2))
    return image


class VB6Mixin:
    def build_classic_toolbar(self):
        toolbar=ttk.Frame(self,padding=(4,3),relief='raised',borderwidth=1);toolbar.pack(fill='x')
        actions=[(tr('Nuovo'),self.new,tr('Nuovo progetto')),(tr('Apri'),self.open_project,tr('Apri progetto…')+' • Ctrl/Cmd+O'),(tr('Salva'),self.save,tr('Salva')+' • Ctrl/Cmd+S'),None,
                 (tr('Annulla'),self.undo,'Ctrl/Cmd+Z'),(tr('Ripeti'),self.redo,tr('Ripeti')),None,
                 (tr('Designer'),lambda:self.tabs.select(0),'Shift+F7'),(tr('Codice'),self.edit_event,'F7'),None]
        self.toolbar_icons=[];symbols=iter(('new','open','save','undo','redo','design','code'))
        for item in actions:
            if item is None:ttk.Separator(toolbar,orient='vertical').pack(side='left',fill='y',padx=5);continue
            label,command,help_=item
            image=tool_icon(toolbar,next(symbols));self.toolbar_icons.append(image)
            button=ttk.Button(toolbar,text=label,image=image,compound='left',command=command,style='Toolbar.TButton');button.pack(side='left',padx=1);ToolTip(button,help_)
        for label,command,help_ in [('▶ F5',self.run,tr('Avvia — F5')),('■',self.stop,tr('Ferma — Shift+F5')),('Deploy…',self.deploy_project,tr('File e deploy'))]:
            button=ttk.Button(toolbar,text=label,command=command,style='Toolbar.TButton');button.pack(side='left',padx=1);ToolTip(button,help_)
        ttk.Button(toolbar,textvariable=self.log_toggle_text,command=self.toggle_log,style='Toolbar.TButton').pack(side='right',padx=2)
        self.bind('<F7>',lambda e:self.edit_event());self.bind('<Shift-F7>',lambda e:self.tabs.select(0))

    def use_classic_appearance(self):
        import json
        from pathlib import Path
        from tkinter import messagebox
        try:
            updated={**self.config_data,'appearance':dict(CLASSIC)}
            self.save_ide_settings(updated)
            self.config_data=updated;self.apply_appearance();self.draw()
        except OSError as exc:messagebox.showerror(tr('Aspetto'),str(exc),parent=self)

    def designer_cursor(self,event):
        if self.drag:return
        handle=''
        if self.selected:
            from hierarchy import widget_origin
            x,y=widget_origin(self.form,self.selected)
            handle=resize_handle(x,y,self.selected['width'],self.selected['height'],self.canvas.canvasx(event.x)-30,self.canvas.canvasy(event.y)-45)
        cursor={'nw':'top_left_corner','ne':'top_right_corner','sw':'bottom_left_corner','se':'bottom_right_corner','n':'sb_v_double_arrow','s':'sb_v_double_arrow','w':'sb_h_double_arrow','e':'sb_h_double_arrow'}.get(handle,'arrow')
        try:self.canvas.configure(cursor=cursor)
        except tk.TclError:self.canvas.configure(cursor='crosshair' if handle else 'arrow')

    def choose_designer_object(self,name,code=False):
        self.selection_names=set();self.commit_code()
        for index,form in enumerate(self.project['forms']):
            for obj in [form]+form['widgets']:
                if obj['name']==name:
                    self.form_index=index;self.selected=None if obj is form else obj
                    if self.selected:self.reveal_widget(self.selected)
                    self.formvar.set(form['name']);self.draw();self.properties()
                    self.tree.selection_set(('w:' if self.selected else 'f:')+(name if self.selected else str(index)))
                    if code:self.edit_event()
                    return

    def property_filter(self,*args):
        query=self.property_query.get().strip().casefold()
        for key,(label,entry) in getattr(self,'property_rows',{}).items():
            visible=not query or query in key.casefold()
            for widget in (label,entry):
                if visible:widget.grid()
                else:widget.grid_remove()
        for label in getattr(self,'property_headers',[]):
            if query:label.grid_remove()
            else:label.grid()

    def describe_property(self,key):
        value=self.propvars[key].get()
        self.property_help.set(key+'\n'+value[:180])


def resize_handle(x,y,width,height,px,py,radius=7):
    handles=(('nw',x,y),('n',x+width/2,y),('ne',x+width,y),('w',x,y+height/2),
             ('e',x+width,y+height/2),('sw',x,y+height),('s',x+width/2,y+height),('se',x+width,y+height))
    return next((name for name,hx,hy in handles if abs(px-hx)<=radius and abs(py-hy)<=radius),'')


def resized_geometry(original,handle,dx,dy,grid):
    result={k:original[k] for k in ('x','y','width','height')}
    def snap(value):return round(value/max(1,grid))*max(1,grid)
    if 'e' in handle:result['width']=max(10,snap(original['width']+dx))
    if 's' in handle:result['height']=max(10,snap(original['height']+dy))
    if 'w' in handle:
        right=original['x']+original['width'];result['x']=max(0,min(right-10,snap(original['x']+dx)));result['width']=right-result['x']
    if 'n' in handle:
        bottom=original['y']+original['height'];result['y']=max(0,min(bottom-10,snap(original['y']+dy)));result['height']=bottom-result['y']
    return result
