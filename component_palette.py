"""Scrollable component palette with native Tk icons and Listbox-compatible access."""
from i18n import tr
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
KINDS.update({'MIDIPlayer':'audio','ExcelWorkbook':'tree','PDFDocument':'file','PrintDocument':'file','CloudStorage':'web','LLMClient':'message','Sheet':'tree','MapView':'web','LabelFrame':'frame','CTkTabview':'tabs','CTkFrame':'frame','CTkScrollableFrame':'frame','CTkTextbox':'lines','CTkSlider':'slider','CTkProgressBar':'progress','CTkSwitch':'check','CTkCheckBox':'check','CTkRadioButton':'radio','CTkOptionMenu':'down','CTkComboBox':'down','CTkSegmentedButton':'tabs'})
for name,glyph in list(KINDS.items()):
    if not name.startswith(('T','CTk')):KINDS.setdefault('T'+name,glyph)

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
        style.configure(self.style_name,rowheight=24,**values)
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
        self.log_toggle_text.set(tr('Nascondi log') if visible else tr('Mostra log'))
    def position_log(self):
        if self.log_visible:self.vertical.sashpos(0,max(1,int(self.vertical.winfo_height()*.76)));self.clamp_log()
    def clamp_log(self):
        if not self.log_visible or len(self.vertical.panes())<2:return
        height=self.vertical.winfo_height()
        if height<2:return
        minimum=min(height,max(320,int(height*.65)))
        if self.vertical.sashpos(0)<minimum:self.vertical.sashpos(0,minimum)
    def install_layout_guards(self):
        self.layout_initialized=False;self.right_layout_initialized=False;self.layout_guard_timer=None
        for pane in (self.main_panes,self.right_panes):
            for sequence in ('<Configure>','<Map>','<ButtonRelease-1>'):
                pane.bind(sequence,self.schedule_layout_guard,add='+')
        self.schedule_layout_guard()

    def schedule_layout_guard(self,event=None):
        if self.layout_guard_timer is None:self.layout_guard_timer=self.after_idle(self.ensure_layout_visible)

    def ensure_layout_visible(self):
        self.layout_guard_timer=None
        width=self.main_panes.winfo_width()
        if width>=800:
            if not self.layout_initialized:
                self.main_panes.sashpos(0,205);self.main_panes.sashpos(1,width-340);self.layout_initialized=True
            else:
                left=max(170,min(self.main_panes.sashpos(0),width-620))
                right=max(left+320,min(self.main_panes.sashpos(1),width-300))
                if self.main_panes.sashpos(0)!=left:self.main_panes.sashpos(0,left)
                if self.main_panes.sashpos(1)!=right:self.main_panes.sashpos(1,right)
        height=self.right_panes.winfo_height()
        if height>=250:
            low=min(150,max(80,height-180));high=max(low,height-170)
            position=max(low,min(260,round(height*.36))) if not self.right_layout_initialized else self.right_panes.sashpos(0)
            position=max(low,min(high,position));self.right_layout_initialized=True
            if self.right_panes.sashpos(0)!=position:self.right_panes.sashpos(0,position)

    def reset_layout(self):
        self.show_log(False)
        self.layout_initialized=False;self.right_layout_initialized=False
        self.schedule_layout_guard()

    def menus(self):
        import webbrowser
        from tkinter import messagebox
        from library_explorer import LibraryExplorer
        bar=tk.Menu(self);self.config(menu=bar);self.menu_buttons=[]
        definitions=[
            ('File',[(tr('Nuovo progetto'),self.new),(tr('Apri progetto…'),self.open_project),(tr('Salva'),self.save),(tr('Salva con nome…'),lambda:self.save(True)),(tr('Cronologia e recupero locale'),self.show_local_history),(tr('Esporta Python…'),self.export),(tr('Esci'),self.close)]),
            (tr('Modifica'),[(tr('Annulla'),self.undo),(tr('Ripeti'),self.redo),(tr('Ancoraggi adattivi…'),self.configure_anchors),(tr('Rinomina intelligente…'),self.rename_selected),(tr('Duplica componente'),self.duplicate),(tr('Elimina selezione'),self.delete),(tr('Allinea X'),lambda:self.align('x')),(tr('Allinea Y'),lambda:self.align('y'))]),
            (tr('Progetto'),[(tr('Ambiente Python del progetto'),self.project_environment),(tr('Gestione form…'),self.manage_forms),(tr('Aggiungi finestra'),self.add_form),(tr('Codice evento'),self.edit_event),(tr('Codice avvio'),lambda:self.global_code('startup')),(tr('Import e funzioni globali'),lambda:self.global_code('imports')),(tr('Configurazione…'),self.settings)]),
            (tr('Esegui'),[(tr('Anteprima — F6'),self.preview_form),(tr('Chiudi anteprima'),self.stop_preview),(tr('Avvia — F5'),self.run),('Debug — F9',self.debug),(tr('Ferma — Shift+F5'),self.stop),(tr('Problemi'),self.analyze_project),(tr('Verifica sintassi'),self.check),('Deploy…',self.deploy_project)]),
            ('PIP',[(tr('Controlli iniziali'),self.show_health),(tr('Prepara automaticamente il progetto…'),lambda:self.open_dependencies(auto_install=True)),(tr('Componente del designer…'),self.selected_dependencies),(tr('Componente della palette…'),self.palette_dependencies),(tr('Installa un pacchetto…'),self.install_package),(tr('Verifica requisiti senza installare…'),lambda:self.open_dependencies(auto_install=False)),(tr('Catalogo pacchetti…'),lambda:LibraryExplorer(self)),(tr('Impostazioni pacchetti…'),self.settings)]),
            (tr('Componenti'),[(tr('Librerie e temi…'),self.library_manager),(tr('Inserisci selezionato'),self.add_widget),(tr('Crea componente esterno…'),self.component_wizard),(tr('Importa descrittore…'),self.import_component),(tr('Componenti del progetto…'),self.component_manager),(tr('Configura selezionato…'),self.configure_component)]),
            (tr('Vista'),[(tr('Classico VB6'),self.use_classic_appearance),(tr('Mostra / nascondi log'),self.toggle_log),(tr('Ripristina pannelli'),self.reset_layout),(tr('Colori ambiente…'),self.appearance_settings),(tr('Tema applicazione…'),self.choose_theme)]),
            ('Help',[(tr('Documenti, cloud e LLM'),lambda:self.help_topic(tr('Documenti, cloud e LLM'))),(tr('Librerie e temi'),lambda:self.help_topic(tr('Librerie e temi'))),(tr('File e deploy'),lambda:self.help_topic(tr('File e deploy'))),(tr('IntelliSense e completamento'),lambda:self.help_topic('IntelliSense')),(tr('Guida rapida — F1'),self.help),(tr('Pacchetti PIP'),lambda:self.help_topic(tr('Pacchetti PIP'))),('Database',lambda:self.help_topic('Database')),(tr('Manuale'),lambda:self.help_topic(tr('Manuale'))),(tr('Estensioni'),lambda:self.help_topic(tr('Estensioni'))),(tr('Esempi'),self.open_examples),(tr('Compatibilità'),lambda:self.help_topic(tr('Compatibilità'))),(tr('Diagnostica'),self.diagnostics),(tr('Documentazione Tkinter'),lambda:webbrowser.open('https://docs.python.org/3/library/tkinter.html')),(tr('Informazioni'),lambda:messagebox.showinfo('VisualTk Studio',tr('VisualTk Studio 1.25\nDesigner visuale Python / Tkinter')))]),
        ]
        for title,items in definitions:
            menu=tk.Menu(bar,tearoff=False);bar.add_cascade(label=title,menu=menu)
            for label,command in items:menu.add_command(label=label,command=command)
            button=ttk.Menubutton(self.menu_bar,text=title+' ▾',menu=menu);button.pack(side='left',padx=1);self.menu_buttons.append(button)
