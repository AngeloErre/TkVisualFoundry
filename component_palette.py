"""Scrollable component palette with native Tk icons and Listbox-compatible access."""
import tkinter as tk
from tkinter import ttk

# Small raster symbols stay sharp on Tk without external image libraries or fonts.
GLYPHS={
 'button':['11111','10001','10101','10001','11111'],
 'text':['11111','00100','00100','00100','00100'],
 'entry':['00000','11111','10000','11111','00000'],
 'lines':['11111','00000','11110','00000','11111'],
 'check':['00001','00010','10100','01000','00000'],
 'radio':['01110','10001','10101','10001','01110'],
 'list':['10111','00000','10111','00000','10111'],
 'down':['11111','00000','10001','01010','00100'],
 'slider':['00100','00100','11111','00100','00100'],
 'updown':['00100','01110','00000','01110','00100'],
 'frame':['11111','10001','10001','10001','11111'],
 'canvas':['00001','00010','00100','01000','11100'],
 'progress':['11111','11100','11100','11100','11111'],
 'tree':['10000','11110','10100','11111','10000'],
 'tabs':['11000','11111','10001','10001','11111'],
 'image':['11111','10101','10001','10111','11111'],
 'audio':['00111','00101','00101','11101','11011'],
 'camera':['01110','11111','10101','11111','00000'],
 'usb':['00100','10101','01110','00100','01100'],
 'terminal':['10000','01000','10000','00111','00000'],
 'file':['11100','10110','10001','10001','11111'],
 'folder':['11000','11111','10001','10001','11111'],
 'message':['11111','10001','11111','01000','10000'],
 'code':['01010','10001','00000','10001','01010'],
 'web':['01110','10101','11111','10101','01110'],
 'play':['10000','11100','11111','11100','10000'],
 'calendar':['10101','11111','10001','10101','11111'],
 'database':['01110','10001','11111','10001','01110'],
 'external':['00100','00100','11111','00100','00100'],
}
KINDS={
 'Button':'button','Label':'text','Entry':'entry','Text':'lines','Checkbutton':'check','Radiobutton':'radio','Listbox':'list','Combobox':'down','Scale':'slider','Spinbox':'updown','Frame':'frame','Canvas':'canvas','Progressbar':'progress','Treeview':'tree','Notebook':'tabs','ScrolledText':'lines','ImageGallery':'image','AudioPlayer':'audio','WebcamView':'camera','USBExplorer':'usb','SerialMonitor':'terminal','FileDropZone':'file','FileBrowserButton':'folder','AdvancedFileBrowser':'folder','MessageButton':'message','HtmlView':'code','WebView':'web','NativeWebButton':'web','VideoPlayer':'play','LegacyVideoPlayer':'play','YouTubePlayer':'play','Calendar':'calendar','DateEntry':'calendar','CTkButton':'button','CTkEntry':'entry','CTkLabel':'text','DatabaseView':'database',
}
COLORS={'camera':'#0e8a78','database':'#7856c9','play':'#d45c45','audio':'#d18a25','image':'#8b5cac','usb':'#60738d','terminal':'#3f7e67','external':'#758092'}


def icon_pixels(kind):
    glyph=KINDS.get(kind,'external');color=COLORS.get(glyph,'#3877c8')
    pixels=[['' for _ in range(20)] for _ in range(20)]
    for y in range(1,19):
        for x in range(1,19):
            if (x in (1,18) and y in (1,18)):continue
            pixels[y][x]=color
    for y,row in enumerate(GLYPHS[glyph]):
        for x,bit in enumerate(row):
            if bit=='1':
                for dy in (0,1):
                    for dx in (0,1):pixels[5+y*2+dy][5+x*2+dx]='#ffffff'
    return pixels


class ComponentPalette(ttk.Frame):
    """Names remain separate from icons, so filtering never changes component IDs."""
    def __init__(self,master,**options):
        super().__init__(master);self.names=[];self.icons={};self.style_name='Palette'+str(id(self))+'.Treeview'
        self.view=ttk.Treeview(self,show='tree',selectmode='browse',height=7,style=self.style_name)
        scrollbar=ttk.Scrollbar(self,orient='vertical',command=self.view.yview);self.view.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right',fill='y');self.view.pack(side='left',fill='both',expand=True)
        self.view.column('#0',width=205,minwidth=140,stretch=True)
        self.configure(bg='#ffffff',fg='#25324a',selectbackground='#dce8ff',selectforeground='#174eb6')
    def image(self,kind):
        if kind not in self.icons:
            image=tk.PhotoImage(master=self,width=20,height=20)
            for y,row in enumerate(icon_pixels(kind)):
                for x,color in enumerate(row):
                    if color:image.put(color,(x,y))
            self.icons[kind]=image
        return self.icons[kind]
    def insert(self,index,kind):
        position=len(self.names) if index=='end' else int(index);self.names.insert(position,kind)
        self.view.insert('',position,iid=kind,text=kind,image=self.image(kind))
    def delete(self,start,end=None):
        first=int(start);last=len(self.names)-1 if end=='end' else (int(end) if end is not None else first)
        for name in self.names[first:last+1]:self.view.delete(name)
        del self.names[first:last+1]
    def get(self,index):return self.names[int(index)]
    def curselection(self):return tuple(self.names.index(name) for name in self.view.selection() if name in self.names)
    def selection_set(self,index,end=None):
        if not self.names:return
        name=self.names[int(index)];self.view.selection_set(name);self.view.focus(name);self.view.see(name)
    def selection_clear(self,start=0,end='end'):self.view.selection_remove(*self.view.selection())
    def bind(self,sequence=None,func=None,add=None):
        return self.view.bind('<<TreeviewSelect>>' if sequence=='<<ListboxSelect>>' else sequence,func,add)
    def configure(self,**options):
        style=ttk.Style(self);values={}
        for key,value in options.items():
            if key=='bg':values.update(background=value,fieldbackground=value)
            elif key=='fg':values['foreground']=value
        style.configure(self.style_name,rowheight=30,**values)
        mappings={}
        if 'selectbackground' in options:mappings['background']=[('selected',options['selectbackground'])]
        if 'selectforeground' in options:mappings['foreground']=[('selected',options['selectforeground'])]
        if mappings:style.map(self.style_name,**mappings)


class LayoutMixin:
    def toggle_log(self):self.show_log(not self.log_visible)
    def show_log(self,visible=True):
        visible=bool(visible)
        if visible and not self.log_visible:
            self.vertical.add(self.log_panel,weight=0);self.log_visible=True;self.after_idle(self.position_log)
        elif not visible and self.log_visible:
            self.vertical.forget(self.log_panel);self.log_visible=False
        self.log_toggle_text.set('Nascondi log' if visible else 'Mostra log')
    def position_log(self):
        if self.log_visible:self.vertical.sashpos(0,max(1,int(self.vertical.winfo_height()*.76)));self.clamp_log()
    def clamp_log(self):
        if not self.log_visible or len(self.vertical.panes())<2:return
        height=self.vertical.winfo_height()
        if height<2:return
        minimum=min(height,max(320,int(height*.65)))
        if self.vertical.sashpos(0)<minimum:self.vertical.sashpos(0,minimum)
    def reset_layout(self):
        self.show_log(False)
        width=self.main_panes.winfo_width()
        if width>800:
            self.main_panes.sashpos(0,240);self.main_panes.sashpos(1,width-285)

    def menus(self):
        import webbrowser
        from tkinter import messagebox
        from library_explorer import LibraryExplorer
        bar=tk.Menu(self);self.config(menu=bar);self.menu_buttons=[]
        definitions=[
            ('File',[('Nuovo progetto',self.new),('Apri progetto…',self.open_project),('Salva',self.save),('Salva con nome…',lambda:self.save(True)),('Esporta Python…',self.export),('Esci',self.close)]),
            ('Modifica',[('Annulla',self.undo),('Ripeti',self.redo),('Duplica componente',self.duplicate),('Elimina selezione',self.delete),('Allinea X',lambda:self.align('x')),('Allinea Y',lambda:self.align('y'))]),
            ('Progetto',[('Gestione form…',self.manage_forms),('Aggiungi finestra',self.add_form),('Codice evento',self.edit_event),('Codice avvio',lambda:self.global_code('startup')),('Import e funzioni globali',lambda:self.global_code('imports')),('Configurazione…',self.settings)]),
            ('Esegui',[('Avvia — F5',self.run),('Debug — F9',self.debug),('Ferma — Shift+F5',self.stop),('Verifica sintassi',self.check),('Crea applicazione',self.package)]),
            ('PIP',[('Prepara automaticamente il progetto…',lambda:self.open_dependencies(auto_install=True)),('Componente del designer…',self.selected_dependencies),('Componente della palette…',self.palette_dependencies),('Installa un pacchetto…',self.install_package),('Verifica requisiti senza installare…',lambda:self.open_dependencies(auto_install=False)),('Esplora PyPI…',lambda:LibraryExplorer(self)),('Impostazioni pacchetti…',self.settings)]),
            ('Componenti',[('Inserisci selezionato',self.add_widget),('Crea componente esterno…',self.component_wizard),('Importa descrittore…',self.import_component),('Componenti del progetto…',self.component_manager),('Configura selezionato…',self.configure_component)]),
            ('Vista',[('Mostra / nascondi log',self.toggle_log),('Ripristina pannelli',self.reset_layout),('Colori ambiente…',self.appearance_settings),('Tema applicazione…',self.choose_theme)]),
            ('Help',[('IntelliSense e completamento',lambda:self.help_topic('IntelliSense')),('Guida rapida — F1',self.help),('Pacchetti PIP',lambda:self.help_topic('Pacchetti PIP')),('Database',lambda:self.help_topic('Database')),('Manuale',lambda:self.help_topic('Manuale')),('Estensioni',lambda:self.help_topic('Estensioni')),('Esempi',self.open_examples),('Compatibilità',lambda:self.help_topic('Compatibilità')),('Diagnostica',self.diagnostics),('Documentazione Tkinter',lambda:webbrowser.open('https://docs.python.org/3/library/tkinter.html')),('Informazioni',lambda:messagebox.showinfo('VisualTk Studio','VisualTk Studio 1.9\nDesigner visuale Python / Tkinter'))]),
        ]
        for title,items in definitions:
            menu=tk.Menu(bar,tearoff=False);bar.add_cascade(label=title,menu=menu)
            for label,command in items:menu.add_command(label=label,command=command)
            button=ttk.Menubutton(self.menu_bar,text=title+' ▾',menu=menu);button.pack(side='left',padx=1);self.menu_buttons.append(button)
