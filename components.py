"""Declarative component registry. Importing descriptors never executes plugin code."""
from i18n import tr
import copy
import json
import keyword
import re
from pathlib import Path

BUILTINS = {
 'ImageGallery': {'module':'visualtk_runtime','class':'ImageGallery','defaults':{'directory':'','thumbnail_size':110,'columns':3,'bg':'#ffffff'},'requirements':['Pillow>=10'], 'description':tr('Galleria miniature con selezione e apertura cartella.')},
 'AudioPlayer': {'module':'visualtk_runtime','class':'AudioPlayer','defaults':{'source':'','volume':0.7,'bg':'#e4e8ee'},'requirements':['pygame-ce>=2.5.8'], 'description':tr('Player MP3: apri, riproduci, pausa, riprendi e stop.')},
 'WebcamView': {'module':'visualtk_runtime','class':'WebcamView','defaults':{'camera_index':0,'fps':20,'bg':'#182230'},'requirements':['opencv-python>=4.10','Pillow>=10'], 'description':tr('Webcam live, avvio esplicito e snapshot.')},
 'USBExplorer': {'module':'visualtk_runtime','class':'USBExplorer','defaults':{'bg':'#e4e8ee'},'requirements':['pyusb>=1.2'], 'description':tr('Elenco USB, VID/PID e selezione dispositivo. Richiede libusb.')},
 'SerialMonitor': {'module':'visualtk_runtime','class':'SerialMonitor','defaults':{'port':'','baudrate':9600,'bg':'#e4e8ee'},'requirements':['pyserial>=3.5'], 'description':tr('Monitor seriale USB: connessione, lettura e invio testo.')}
}
BUILTINS.update({
 'Treeview': {'module':'tkinter.ttk','class':'Treeview','defaults':{'columns':['nome','valore'],'show':'tree headings','selectmode':'browse'},'requirements':[],'description':tr('Albero/tabella ttk; heading, insert e column nel codice Load.')},
 'Notebook': {'module':'visualtk_runtime','class':'NotebookView','defaults':{'pages':[tr('Pagina 1'),tr('Pagina 2')]},'requirements':[],'description':tr('Schede ttk. add_page(titolo) restituisce un Frame per i widget creati da codice.')},
 'ScrolledText': {'module':'tkinter.scrolledtext','class':'ScrolledText','defaults':{'font':'Helvetica 12','wrap':'word','bg':'#ffffff','fg':'#182230'},'requirements':[],'description':tr('Testo multiriga con scrollbar integrata.')},
 'FileDropZone': {'module':'visualtk_runtime','class':'FileDropZone','defaults':{'text':tr('Trascina qui file dal Finder'),'bg':'#eaf2ff'},'requirements':['tkinterdnd2>=0.4'],'description':tr('Drag & drop nativo di file. Evento FilesDropped; proprietà paths.')},
 'FileBrowserButton': {'module':'visualtk_runtime','class':'FileBrowserButton','defaults':{'text':tr('Sfoglia…'),'mode':'open','advanced':False},'requirements':[],'description':tr('Dialoghi standard: open, multiple, directory, save. advanced=true richiede tkfilebrowser.')},
 'AdvancedFileBrowser': {'module':'visualtk_runtime','class':'FileBrowserButton','defaults':{'text':tr('File browser avanzato'),'mode':'multiple','advanced':True},'requirements':['tkfilebrowser>=2.3'],'description':tr('Dialoghi tkfilebrowser, con selezione multipla.')},
 'MessageButton': {'module':'visualtk_runtime','class':'MessageButton','defaults':{'text':tr('Mostra messaggio'),'title':tr('Informazione'),'message':tr('Ciao!'),'mode':'info'},'requirements':[],'description':tr('Dialoghi info, warning, error, confirm, text, integer, float, color.')},
 'HtmlView': {'module':'visualtk_runtime','class':'HtmlView','defaults':{'html':'<h2>VisualTk Studio</h2><p>HTML semplice</p>'},'requirements':['tkhtmlview>=0.3'],'description':tr('Rendering HTML leggero con tkhtmlview.')},
 'WebView': {'module':'visualtk_runtime','class':'WebView','defaults':{'url':'https://www.python.org'},'requirements':['tkinterweb>=4'],'description':tr('HTML/CSS e pagine web/locali con TkinterWeb. Premi Apri per caricare.')},
 'NativeWebButton': {'module':'visualtk_runtime','class':'NativeWebButton','defaults':{'url':'https://www.python.org','text':tr('Apri web nativo'),'title':'Browser'},'requirements':['pywebview>=5'],'description':tr('Finestra web nativa in processo separato, compatibile con il mainloop Tk.')},
 'VideoPlayer': {'module':'visualtk_runtime','class':'VideoPlayer','defaults':{'source':'','volume':70},'requirements':['python-vlc>=3'],'description':tr('Riproduzione locale/streaming tramite VLC. Su Mac finestra video separata; richiede VLC/libVLC.')},
 'LegacyVideoPlayer': {'module':'visualtk_runtime','class':'LegacyVideoPlayer','defaults':{'source':''},'requirements':['tkVideoPlayer>=2.8'],'description':'Adapter tkVideoPlayer opzionale/legacy. Dipendenze PyAV da verificare con Python 3.13.'},
 'YouTubePlayer': {'module':'visualtk_runtime','class':'YouTubePlayer','defaults':{'url':'','backend':'yt-dlp'},'requirements':['yt-dlp','python-vlc>=3'],'description':tr('Risoluzione stream YouTube e riproduzione VLC. Backend alternativi pytubefix/pytube.')},
 'Calendar': {'module':'tkcalendar','class':'Calendar','defaults':{'selectmode':'day'},'requirements':['tkcalendar>=1.6'],'description':tr('Calendario con selezione data.')},
 'DateEntry': {'module':'tkcalendar','class':'DateEntry','defaults':{'date_pattern':'dd/mm/yyyy'},'requirements':['tkcalendar>=1.6'],'description':tr('Campo data con calendario a comparsa.')},
 'CTkButton': {'module':'customtkinter','class':'CTkButton','defaults':{'text':tr('Pulsante moderno'),'fg_color':'#1f6aa5','corner_radius':8},'requirements':['customtkinter>=5.2'],'description':tr('Pulsante moderno CustomTkinter.')},
 'CTkEntry': {'module':'customtkinter','class':'CTkEntry','defaults':{'placeholder_text':tr('Scrivi qui…'),'corner_radius':8},'requirements':['customtkinter>=5.2'],'description':tr('Campo testo CustomTkinter.')},
 'CTkSwitch': {'module':'customtkinter','class':'CTkSwitch','defaults':{'text':tr('Attiva opzione')},'requirements':['customtkinter>=5.2'],'description':tr('Interruttore CustomTkinter.')}
})

BUILTINS['DatabaseView']={'module':'database_runtime','class':'DatabaseView','defaults':{'backend':'sqlite','database':'visualtk.sqlite','host':'localhost','port':0,'username':'','password_env':'VISUALTK_DB_PASSWORD','table':'','limit':200},'requirements':[],'description':tr('Database SQLite/PostgreSQL/MySQL con tabella dati e comandi CRUD. SQLite non richiede PIP.')}
BUILTINS['WebcamView']['requirements']=['opencv-python>=4.10','numpy','Pillow>=10']

# Typed integration metadata also drives palette families and the library manager.
for suffix in ('Button','Label','Entry','Checkbutton','Radiobutton','Scale','Spinbox','Frame','Labelframe','Separator','Scrollbar','Menubutton','Sizegrip','Panedwindow'):
    BUILTINS['T'+suffix]={'module':'tkinter.ttk','class':suffix,'family':'tkinter.ttk','container':suffix in ('Frame','Labelframe'),'defaults':({'text':suffix} if suffix in ('Button','Label','Checkbutton','Radiobutton','Labelframe','Menubutton') else {}),'requirements':[],'description':'ttk '+suffix}
for suffix,defaults in {
    'Label':{'text':'Label'},'CheckBox':{'text':'Check'},'RadioButton':{'text':'Option'},'Slider':{'from_':0,'to':100},'ProgressBar':{},'OptionMenu':{'values':['First','Second']},'ComboBox':{'values':['First','Second']},'SegmentedButton':{'values':['First','Second']},'Textbox':{},'Frame':{'corner_radius':8},'ScrollableFrame':{'label_text':'Panel'}
}.items():
    BUILTINS['CTk'+suffix]={'module':'customtkinter','class':'CTk'+suffix,'family':'CustomTkinter','defaults':defaults,'requirements':['customtkinter>=5.2,<7'],'description':'CustomTkinter '+suffix}
for name in ('CTkButton','CTkEntry','CTkSwitch'):BUILTINS[name].update(family='CustomTkinter',requirements=['customtkinter>=5.2,<7'])
BUILTINS['CTkTabview']={'module':'integration_runtime','class':'ModernTabs','family':'CustomTkinter','defaults':{'pages':['Page 1','Page 2']},'requirements':['customtkinter>=5.2,<7'],'description':'CustomTkinter tab container'}
BUILTINS['LabelFrame']={'module':'tkinter','class':'LabelFrame','family':'tkinter','defaults':{'text':'Group'},'requirements':[],'description':'Tkinter labelled container'}
BUILTINS['Sheet']={'module':'integration_runtime','class':'SheetView','family':'tksheet','defaults':{'data':[['A',1],['B',2]],'headers':['Name','Value'],'editable':True},'requirements':['tksheet>=7,<8'],'description':'Editable table: get_data, set_data, get_cell, set_cell'}
BUILTINS['MapView']={'module':'integration_runtime','class':'MapView','family':'tkintermapview','defaults':{'latitude':40.8518,'longitude':14.2681,'zoom':10},'requirements':['tkintermapview>=1.29,<2'],'description':'Map with coordinates, zoom and markers'}
for suffix,defaults in {'ComboBox':{'scrolledlist_items':['First','Second']},'EntryField':{'value':''},'Counter':{'entryfield_value':0},'ScrolledText':{}}.items():
    BUILTINS['Pmw'+suffix]={'module':'Pmw','class':suffix,'family':'Pmw','defaults':defaults,'requirements':['Pmw>=2.1,<3'],'description':'Pmw '+suffix}

CATALOG = [
 ('Pillow',tr('Immagini / gallerie')),('pygame-ce',tr('Audio MP3 — Python 3.15')),('opencv-python','Webcam / computer vision'),('pyusb',tr('USB generico')),('pyserial',tr('Seriale / Arduino')),
 ('customtkinter',tr('Widget moderni')),('ttkbootstrap',tr('Temi e componenti ttk')),('tkcalendar',tr('Calendario')),('SQLAlchemy',tr('Database remoti')),('psycopg','PostgreSQL'),('PyMySQL','MySQL'),('tksheet',tr('Tabelle')),('matplotlib',tr('Grafici')),('numpy',tr('Calcolo numerico')),('tkinterdnd2',tr('Drag & drop Finder')),('tkfilebrowser',tr('Dialoghi file avanzati')),('tkinterweb',tr('HTML/CSS web')),('tkhtmlview',tr('HTML leggero')),('pywebview',tr('Web nativo')),('python-vlc',tr('Video / streaming')),('yt-dlp','YouTube'),('pytubefix',tr('YouTube alternativo')),('pytube','YouTube legacy'),('tkVideoPlayer',tr('Video legacy / verificare Python')),('cefpython3',tr('Chromium legacy — non supportato su Python 3.13'))]

def descriptor(data):
    for field in ('module','class'):
        value=data.get(field,'')
        if not isinstance(value,str) or not all(p.isidentifier() and not keyword.iskeyword(p) for p in value.split('.')):raise ValueError(tr('Modulo/classe Python non validi'))
    if '.' in data['class']:raise ValueError(tr('class deve essere un singolo identificatore'))
    if not isinstance(data.get('defaults',{}),dict):raise ValueError(tr('defaults deve essere un oggetto JSON'))
    req=data.get('requirements',[])
    if not isinstance(req,list) or any(not isinstance(r,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.\-\[\],<>=!~ ]*',r) for r in req):raise ValueError(tr('requirements ammette solo nomi/versioni PyPI, senza URL o opzioni'))
    json.dumps(data); return copy.deepcopy(data)

def registry(project):
    result=copy.deepcopy(BUILTINS)
    for name,data in project.get('components',{}).items():
        if not name.isidentifier() or name in BUILTINS:raise ValueError(tr('Nome componente riservato o non valido'))
        result[name]=descriptor(data)
    return result

def requirements(project):
    reg=registry(project); result=set(project.get('requirements',[]))
    for f in project['forms']:
        for w in f['widgets']:
            if w['kind'] in reg:result.update(reg[w['kind']].get('requirements',[]))
    from library_catalog import theme_requirements
    result.update(theme_requirements(project))
    if project.get('appearance_mode'):result.add('customtkinter>=5.2,<7')
    for f in project['forms']:
        for w in f['widgets']:
            if w['kind']=='YouTubePlayer' and w.get('props',{}).get('backend') in ('pytubefix','pytube'):result.add(w['props']['backend'])
            if w['kind']=='FileBrowserButton' and w.get('props',{}).get('advanced'):result.add('tkfilebrowser>=2.3')
    for f in project['forms']:
        for w in f['widgets']:
            if w['kind']=='DatabaseView':
                backend=w.get('props',{}).get('backend','sqlite')
                if backend=='postgresql':result.update(['SQLAlchemy>=2.0','psycopg[binary]>=3'])
                elif backend=='mysql':result.update(['SQLAlchemy>=2.0','PyMySQL>=1.1'])
    # Validate also user-added packages before invoking pip.
    descriptor({'module':'placeholder','class':'Placeholder','requirements':list(result)})
    return sorted(result)

def install_args(python, specs):
    descriptor({'module':'placeholder','class':'Placeholder','requirements':list(specs)})
    if not specs:raise ValueError(tr('Nessuna dipendenza da installare'))
    return [python,'-m','pip','install','--index-url','https://pypi.org/simple',*specs]

def design_size(kind,external=False):
    if kind in ('Sheet','MapView'):return 600,380
    if kind in ('Notebook','CTkTabview'):return 500,320
    if kind in ('Frame','LabelFrame','TFrame','TLabelframe','CTkFrame','CTkScrollableFrame','TPanedwindow'):return 400,240
    if kind in ('CTkTextbox','PmwScrolledText'):return 360,220
    if kind=='TSeparator':return 240,12
    if kind=='TScrollbar':return 20,160
    if kind=='TSizegrip':return 20,20
    if kind in ('CTkSlider','TScale'):return 240,36
    if kind=='CTkProgressBar':return 240,22
    if kind.startswith(('T','CTk','Pmw')) and kind in BUILTINS and kind not in ('Treeview',):return 180,38
    return (480,280) if kind in BUILTINS or external else (140,90 if kind in ('Text','Listbox','Canvas') else 35)
