"""Declarative component registry. Importing descriptors never executes plugin code."""
import copy
import json
import keyword
import re
from pathlib import Path

BUILTINS = {
 'ImageGallery': {'module':'visualtk_runtime','class':'ImageGallery','defaults':{'directory':'','thumbnail_size':110,'columns':3,'bg':'#ffffff'},'requirements':['Pillow>=10'], 'description':'Galleria miniature con selezione e apertura cartella.'},
 'AudioPlayer': {'module':'visualtk_runtime','class':'AudioPlayer','defaults':{'source':'','volume':0.7,'bg':'#e4e8ee'},'requirements':['pygame-ce>=2.5.8'], 'description':'Player MP3: apri, riproduci, pausa, riprendi e stop.'},
 'WebcamView': {'module':'visualtk_runtime','class':'WebcamView','defaults':{'camera_index':0,'fps':20,'bg':'#182230'},'requirements':['opencv-python>=4.10','Pillow>=10'], 'description':'Webcam live, avvio esplicito e snapshot.'},
 'USBExplorer': {'module':'visualtk_runtime','class':'USBExplorer','defaults':{'bg':'#e4e8ee'},'requirements':['pyusb>=1.2'], 'description':'Elenco USB, VID/PID e selezione dispositivo. Richiede libusb.'},
 'SerialMonitor': {'module':'visualtk_runtime','class':'SerialMonitor','defaults':{'port':'','baudrate':9600,'bg':'#e4e8ee'},'requirements':['pyserial>=3.5'], 'description':'Monitor seriale USB: connessione, lettura e invio testo.'}
}
BUILTINS.update({
 'Treeview': {'module':'tkinter.ttk','class':'Treeview','defaults':{'columns':['nome','valore'],'show':'tree headings','selectmode':'browse'},'requirements':[],'description':'Albero/tabella ttk; heading, insert e column nel codice Load.'},
 'Notebook': {'module':'visualtk_runtime','class':'NotebookView','defaults':{'pages':['Pagina 1','Pagina 2']},'requirements':[],'description':'Schede ttk. add_page(titolo) restituisce un Frame per i widget creati da codice.'},
 'ScrolledText': {'module':'tkinter.scrolledtext','class':'ScrolledText','defaults':{'font':'Helvetica 12','wrap':'word','bg':'#ffffff','fg':'#182230'},'requirements':[],'description':'Testo multiriga con scrollbar integrata.'},
 'FileDropZone': {'module':'visualtk_runtime','class':'FileDropZone','defaults':{'text':'Trascina qui file dal Finder','bg':'#eaf2ff'},'requirements':['tkinterdnd2>=0.4'],'description':'Drag & drop nativo di file. Evento FilesDropped; proprietà paths.'},
 'FileBrowserButton': {'module':'visualtk_runtime','class':'FileBrowserButton','defaults':{'text':'Sfoglia…','mode':'open','advanced':False},'requirements':[],'description':'Dialoghi standard: open, multiple, directory, save. advanced=true richiede tkfilebrowser.'},
 'AdvancedFileBrowser': {'module':'visualtk_runtime','class':'FileBrowserButton','defaults':{'text':'File browser avanzato','mode':'multiple','advanced':True},'requirements':['tkfilebrowser>=2.3'],'description':'Dialoghi tkfilebrowser, con selezione multipla.'},
 'MessageButton': {'module':'visualtk_runtime','class':'MessageButton','defaults':{'text':'Mostra messaggio','title':'Informazione','message':'Ciao!','mode':'info'},'requirements':[],'description':'Dialoghi info, warning, error, confirm, text, integer, float, color.'},
 'HtmlView': {'module':'visualtk_runtime','class':'HtmlView','defaults':{'html':'<h2>VisualTk Studio</h2><p>HTML semplice</p>'},'requirements':['tkhtmlview>=0.3'],'description':'Rendering HTML leggero con tkhtmlview.'},
 'WebView': {'module':'visualtk_runtime','class':'WebView','defaults':{'url':'https://www.python.org'},'requirements':['tkinterweb>=4'],'description':'HTML/CSS e pagine web/locali con TkinterWeb. Premi Apri per caricare.'},
 'NativeWebButton': {'module':'visualtk_runtime','class':'NativeWebButton','defaults':{'url':'https://www.python.org','text':'Apri web nativo','title':'Browser'},'requirements':['pywebview>=5'],'description':'Finestra web nativa in processo separato, compatibile con il mainloop Tk.'},
 'VideoPlayer': {'module':'visualtk_runtime','class':'VideoPlayer','defaults':{'source':'','volume':70},'requirements':['python-vlc>=3'],'description':'Riproduzione locale/streaming tramite VLC. Su Mac finestra video separata; richiede VLC/libVLC.'},
 'LegacyVideoPlayer': {'module':'visualtk_runtime','class':'LegacyVideoPlayer','defaults':{'source':''},'requirements':['tkVideoPlayer>=2.8'],'description':'Adapter tkVideoPlayer opzionale/legacy. Dipendenze PyAV da verificare con Python 3.13.'},
 'YouTubePlayer': {'module':'visualtk_runtime','class':'YouTubePlayer','defaults':{'url':'','backend':'yt-dlp'},'requirements':['yt-dlp','python-vlc>=3'],'description':'Risoluzione stream YouTube e riproduzione VLC. Backend alternativi pytubefix/pytube.'},
 'Calendar': {'module':'tkcalendar','class':'Calendar','defaults':{'selectmode':'day'},'requirements':['tkcalendar>=1.6'],'description':'Calendario con selezione data.'},
 'DateEntry': {'module':'tkcalendar','class':'DateEntry','defaults':{'date_pattern':'dd/mm/yyyy'},'requirements':['tkcalendar>=1.6'],'description':'Campo data con calendario a comparsa.'},
 'CTkButton': {'module':'customtkinter','class':'CTkButton','defaults':{'text':'Pulsante moderno','fg_color':'#1f6aa5','corner_radius':8},'requirements':['customtkinter>=5.2'],'description':'Pulsante moderno CustomTkinter.'},
 'CTkEntry': {'module':'customtkinter','class':'CTkEntry','defaults':{'placeholder_text':'Scrivi qui…','corner_radius':8},'requirements':['customtkinter>=5.2'],'description':'Campo testo CustomTkinter.'},
 'CTkSwitch': {'module':'customtkinter','class':'CTkSwitch','defaults':{'text':'Attiva opzione'},'requirements':['customtkinter>=5.2'],'description':'Interruttore CustomTkinter.'}
})

CATALOG = [
 ('Pillow','Immagini / gallerie'),('pygame-ce','Audio MP3 — Python 3.15'),('opencv-python','Webcam / computer vision'),('pyusb','USB generico'),('pyserial','Seriale / Arduino'),
 ('customtkinter','Widget moderni'),('ttkbootstrap','Temi e componenti ttk'),('tkcalendar','Calendario'),('tksheet','Tabelle'),('matplotlib','Grafici'),('numpy','Calcolo numerico'),('tkinterdnd2','Drag & drop Finder'),('tkfilebrowser','Dialoghi file avanzati'),('tkinterweb','HTML/CSS web'),('tkhtmlview','HTML leggero'),('pywebview','Web nativo'),('python-vlc','Video / streaming'),('yt-dlp','YouTube'),('pytubefix','YouTube alternativo'),('pytube','YouTube legacy'),('tkVideoPlayer','Video legacy / verificare Python'),('cefpython3','Chromium legacy — non supportato su Python 3.13')]

def descriptor(data):
    for field in ('module','class'):
        value=data.get(field,'')
        if not isinstance(value,str) or not all(p.isidentifier() and not keyword.iskeyword(p) for p in value.split('.')):raise ValueError('Modulo/classe Python non validi')
    if '.' in data['class']:raise ValueError('class deve essere un singolo identificatore')
    if not isinstance(data.get('defaults',{}),dict):raise ValueError('defaults deve essere un oggetto JSON')
    req=data.get('requirements',[])
    if not isinstance(req,list) or any(not isinstance(r,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.\-\[\],<>=!~ ]*',r) for r in req):raise ValueError('requirements ammette solo nomi/versioni PyPI, senza URL o opzioni')
    json.dumps(data); return copy.deepcopy(data)

def registry(project):
    result=copy.deepcopy(BUILTINS)
    for name,data in project.get('components',{}).items():
        if not name.isidentifier() or name in BUILTINS:raise ValueError('Nome componente riservato o non valido')
        result[name]=descriptor(data)
    return result

def requirements(project):
    reg=registry(project); result=set(project.get('requirements',[]))
    for f in project['forms']:
        for w in f['widgets']:
            if w['kind'] in reg:result.update(reg[w['kind']].get('requirements',[]))
    if project.get('theme'):result.add('ttkbootstrap>=1.10')
    for f in project['forms']:
        for w in f['widgets']:
            if w['kind']=='YouTubePlayer' and w.get('props',{}).get('backend') in ('pytubefix','pytube'):result.add(w['props']['backend'])
            if w['kind']=='FileBrowserButton' and w.get('props',{}).get('advanced'):result.add('tkfilebrowser>=2.3')
    # Validate also user-added packages before invoking pip.
    descriptor({'module':'placeholder','class':'Placeholder','requirements':list(result)})
    return sorted(result)

def install_args(python, specs):
    descriptor({'module':'placeholder','class':'Placeholder','requirements':list(specs)})
    if not specs:raise ValueError('Nessuna dipendenza da installare')
    return [python,'-m','pip','install','--index-url','https://pypi.org/simple',*specs]
