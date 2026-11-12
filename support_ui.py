"""Help, project themes, font chooser and dependency diagnostics for the IDE."""
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, font as tkfont, messagebox
from tkinter.scrolledtext import ScrolledText
from pathlib import Path
import webbrowser

class SupportMixin:
    def choose_font(self):
        if 'font' not in self.propvars:return messagebox.showinfo('Font','Il componente selezionato non espone la proprietà font.')
        win=tk.Toplevel(self);win.title('Carattere e stile');current=tkfont.Font(self,font=self.propvars['font'].get()).actual()
        family=tk.StringVar(value=current['family']);size=tk.IntVar(value=abs(current['size']));bold=tk.BooleanVar(value=current['weight']=='bold');italic=tk.BooleanVar(value=current['slant']=='italic')
        ttk.Combobox(win,textvariable=family,values=sorted(set(tkfont.families(self))),width=40).pack(padx=12,pady=10)
        ttk.Spinbox(win,from_=6,to=96,textvariable=size).pack(padx=12,pady=5)
        ttk.Checkbutton(win,text='Grassetto',variable=bold).pack(anchor='w',padx=12);ttk.Checkbutton(win,text='Corsivo',variable=italic).pack(anchor='w',padx=12)
        preview_font=tkfont.Font(self,family=family.get(),size=size.get());sample=ttk.Label(win,text='VisualTk Studio — Anteprima 123',font=preview_font);sample.pack(padx=15,pady=15)
        def preview(*args):
            try:preview_font.configure(family=family.get(),size=size.get(),weight='bold' if bold.get() else 'normal',slant='italic' if italic.get() else 'roman')
            except (tk.TclError,ValueError):pass
        for var in (family,size,bold,italic):var.trace_add('write',preview)
        def apply():
            preview();value=self.tk.call('list',family.get(),size.get(),*(['bold'] if bold.get() else []),*(['italic'] if italic.get() else []))
            # Tcl list quoting preserves font family names containing spaces.
            self.propvars['font'].set(self.tk.call('format','%s',value));self.apply_props();win.destroy()
        ttk.Button(win,text='Applica',command=apply).pack(pady=10)
    def choose_theme(self):
        win=tk.Toplevel(self);win.title('Tema del progetto');theme=tk.StringVar(value=self.project.get('theme',''))
        ttk.Label(win,text='Tema ttkbootstrap dell’app generata. Vuoto = standard Tk.').pack(padx=15,pady=10)
        ttk.Combobox(win,textvariable=theme,values=['','litera','flatly','cosmo','minty','darkly','superhero','cyborg','solar'],state='readonly').pack(padx=15,pady=5)
        def apply():self.commit_code();self.checkpoint();self.project['theme']=theme.get();self.update_source();win.destroy()
        ttk.Button(win,text='Salva tema',command=apply).pack(pady=10)
    def diagnostics(self):
        script="""import importlib.util,sys,ctypes.util
print('Python:',sys.version);print('Interprete:',sys.executable)
modules=['tkinter','tkinter.ttk','tkinter.font','tkinter.dnd','PIL','pygame','cv2','usb','serial','tkinterdnd2','tkfilebrowser','tkinterweb','tkhtmlview','webview','vlc','yt_dlp','pytube','pytubefix','customtkinter','ttkbootstrap','tkcalendar','tkVideoPlayer','cefpython3']
for module in modules:
    try:state='PRESENTE' if importlib.util.find_spec(module) else 'MANCANTE'
    except (ModuleNotFoundError,ValueError):state='MANCANTE'
    print(module+': '+state)
print('libusb:',ctypes.util.find_library('usb-1.0') or 'Verificare Homebrew/libusb')
print('libVLC:',ctypes.util.find_library('vlc') or 'Verificare VLC.app / libVLC')
print('La presenza del modulo non certifica compatibilità o funzionamento hardware.')
"""
        self.launch([self.config_data['python'],'-c',script])
    def open_examples(self):
        directory=Path(__file__).resolve().parent/'examples'
        if sys.platform=='darwin':subprocess.Popen(['open',str(directory)])
        else:webbrowser.open(directory.as_uri())
    def help_topic(self,topic='Guida rapida'):
        HELP=getattr(sys.modules[self.__class__.__module__],'HELP','Consulta il Manuale')
        base=Path(__file__).resolve().parent;win=tk.Toplevel(self);win.title('Help — VisualTk Studio 1.6');win.geometry('900x650')
        row=ttk.Frame(win,padding=5);row.pack(fill='x');selection=tk.StringVar(value=topic);query=tk.StringVar()
        box=ttk.Combobox(row,textvariable=selection,values=['Guida rapida','Manuale','Estensioni','Esempi','Compatibilità'],state='readonly');box.pack(side='left');entry=ttk.Entry(row,textvariable=query);entry.pack(side='left',fill='x',expand=True,padx=6)
        text=ScrolledText(win,wrap='word',font=('Helvetica',12));text.pack(fill='both',expand=True)
        files={'Manuale':'README.md','Estensioni':'ESTENSIONI.md','Esempi':'ESEMPI.md','Compatibilità':'COMPATIBILITA.md'}
        def show(event=None):
            path=base/files.get(selection.get(),'README.md');content=HELP if selection.get()=='Guida rapida' else (path.read_text(encoding='utf-8') if path.exists() else 'Documento non disponibile.')
            text.configure(state='normal');text.delete('1.0','end');text.insert('1.0',content);text.configure(state='disabled')
        def find(event=None):
            text.tag_remove('found','1.0','end');term=query.get()
            if not term:return
            index=text.search(term,'1.0',stopindex='end',nocase=True)
            if index:text.tag_add('found',index,index+'+'+str(len(term))+'c');text.tag_configure('found',background='#ffe08a',foreground='black');text.see(index)
        ttk.Button(row,text='Cerca',command=find).pack(side='left');entry.bind('<Return>',find);box.bind('<<ComboboxSelected>>',show);show()
