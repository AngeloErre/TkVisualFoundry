"""Integration catalog and theme settings, distinct from installation or GUI validation."""
from pathlib import PurePosixPath
from i18n import tr

LIBRARIES=[
 ('tkinter','standard',[],'tkinter','native',tr('Controlli Tk standard')),
 ('tkinter.ttk','widgets',[],'tkinter.ttk','native',tr('Controlli standard con temi ttk')),
 ('CustomTkinter','widgets',['customtkinter>=5.2,<7'],'customtkinter','adapter',tr('Controlli moderni e contenitori annidati')),
 ('ttkbootstrap','theme',['ttkbootstrap>=1.10,<2'],'ttkbootstrap','adapter',tr('Temi della serie 1.x; versione vincolata per compatibilità')),
 ('ttkthemes','theme',['ttkthemes>=3.2,<4'],'ttkthemes','adapter',tr('Raccolta di temi ttk; controlla le licenze prima della distribuzione')),
 ('sv-ttk','theme',['sv-ttk>=2,<3'],'sv_ttk','adapter',tr('Tema ttk Sun Valley chiaro/scuro')),
 ('Azure','theme',[],'','assets',tr('Importa la cartella contenente azure.tcl e le sue risorse')),
 ('Forest','theme',[],'','assets',tr('Importa la cartella con forest-light.tcl e forest-dark.tcl')),
 ('Tix','legacy',[],'','unsupported',tr('tkinter.tix è stato rimosso da Python 3.13; non disponibile in questo ambiente')),
 ('Pmw','widgets',['Pmw>=2.1,<3'],'Pmw','adapter',tr('Megawidget selezionati con inizializzazione in esecuzione')),
 ('tkcalendar','widgets',['tkcalendar>=1.6'],'tkcalendar','adapter',tr('Calendario e campo data')),
 ('tksheet','widgets',['tksheet>=7,<8'],'tksheet','adapter',tr('Tabella modificabile con eventi per celle e selezioni')),
 ('tkinterweb','widgets',['tkinterweb>=4'],'tkinterweb','adapter',tr('Adattatore HTML/web')),
 ('tkintermapview','widgets',['tkintermapview>=1.29,<2'],'tkintermapview','adapter',tr('Mappe, coordinate e marcatori; possono servire servizi cartografici online')),
 ('tkVideoPlayer','widgets',['tkVideoPlayer>=2.8'],'tkVideoPlayer','experimental',tr('Video opzionale; verifica la compatibilità di PyAV')),
 ('TkinterDnD2','widgets',['tkinterdnd2>=0.4'],'tkinterdnd2','adapter',tr('Drag and drop nativo; binari Tcl/Tk specifici per piattaforma')),
 ('PySimpleGUI','framework',[],'','separate',tr('Motore di layout/eventi separato; non disponibile come widget nella palette')),
 ('FreeSimpleGUI','framework',[],'','separate',tr('Motore di layout/eventi separato; non disponibile come widget nella palette')),
 ('guizero','framework',[],'','separate',tr('Modello App/contenitori separato; non disponibile come widget nella palette')),
]
LIBRARIES.extend([
 ('MIDI','widgets',['mido>=1.3,<2','python-rtmidi>=1.5,<2'],'mido','adapter','MIDIPlayer: requires a synthesizer output; no audio engine included'),
 ('Excel','widgets',['openpyxl>=3.1,<4'],'openpyxl','adapter','ExcelWorkbook: XLSX/XLSM cells and sheets, no formula calculation'),
 ('PDF','widgets',['pypdf[crypto]>=6,<8'],'pypdf','adapter','PDFDocument: text, merge and page extraction; no OCR'),
 ('Stampa','widgets',[],'productivity_runtime','adapter','PrintDocument: associated application and operating-system print queue'),
 ('Google Drive','widgets',['google-api-python-client>=2,<3','google-auth-oauthlib>=1,<2','google-auth-httplib2>=0.2,<1'],'googleapiclient.discovery','adapter','CloudStorage: Desktop OAuth or ADC, external tokens'),
 ('S3 / MinIO','widgets',['boto3>=1.35,<2'],'boto3','adapter','CloudStorage: bucket and account credentials required'),
 ('WebDAV','widgets',['requests>=2.32,<3'],'requests','adapter','CloudStorage: Nextcloud/ownCloud and compatible HTTPS servers'),
 ('OpenAI','widgets',['openai>=2,<4'],'openai','adapter','LLMClient: official Responses API; key and model required'),
 ('Claude','widgets',['anthropic>=0.70,<2'],'anthropic','adapter','LLMClient: official Messages API; key and model required'),
 ('Gemini','widgets',['google-genai>=1,<3'],'google.genai','adapter','LLMClient: official Google Gen AI SDK; key and model required'),
])

THEME_REQUIREMENTS={row[0]:row[2] for row in LIBRARIES if row[1]=='theme'}

def theme_config(project):
    config=project.get('theme_config')
    if config is None:return {'provider':'ttkbootstrap','name':project['theme']} if project.get('theme') else {'provider':'none'}
    if not isinstance(config,dict):raise ValueError('Invalid theme settings')
    provider=config.get('provider','none')
    if provider not in ('none','ttkbootstrap','ttkthemes','sv-ttk','azure','forest'):raise ValueError('Unsupported theme provider')
    if config.get('mode','light') not in ('light','dark'):raise ValueError('Theme mode must be light or dark')
    if provider in ('azure','forest'):
        raw=config.get('file','');path=PurePosixPath(raw)
        if not raw or path.is_absolute() or any(part in ('.','..') or part.startswith('.') or ':' in part or '\\' in part for part in path.parts) or path.suffix.lower()!='.tcl':raise ValueError('Theme must be a project-relative Tcl file')
    if not isinstance(config.get('name',''),str):raise ValueError('Theme name must be text')
    return {'provider':provider,**config}

def theme_requirements(project):
    config=theme_config(project);provider=config['provider']
    return THEME_REQUIREMENTS.get(provider,[])

def packaging_flags(project):
    from components import requirements
    from re import split
    names={split(r'[<>=!~\[]',value,maxsplit=1)[0].lower() for value in requirements(project)}
    modules={'customtkinter':'customtkinter','ttkbootstrap':'ttkbootstrap','ttkthemes':'ttkthemes','sv-ttk':'sv_ttk','pmw':'Pmw','tkcalendar':'tkcalendar','tksheet':'tksheet','tkinterweb':'tkinterweb','tkintermapview':'tkintermapview','tkinterdnd2':'tkinterdnd2','tkvideoplayer':'tkVideoPlayer'}
    flags=[]
    for name,module in {'mido':'mido','python-rtmidi':'rtmidi','openpyxl':'openpyxl','pypdf':'pypdf','openai':'openai','anthropic':'anthropic','google-genai':'google.genai','google-api-python-client':'googleapiclient','google-auth-oauthlib':'google_auth_oauthlib','google-auth-httplib2':'google_auth_httplib2','boto3':'boto3','requests':'requests'}.items():
        if name in names:flags+=['--collect-all='+module]
    if 'boto3' in names:flags+=['--collect-all=botocore']
    if names & {'openai','anthropic','google-genai','google-api-python-client','requests','boto3'}:flags+=['--collect-data=certifi']
    for name,module in modules.items():
        if name in names:flags+=['--collect-all='+module]
    if 'customtkinter' in names:flags+=['--hidden-import=PIL._tkinter_finder']
    return flags

def component_family(kind,project,reg=None):
    from components import registry
    data=(registry(project) if reg is None else reg).get(kind)
    if not data:return 'tkinter.ttk' if kind in ('Combobox','Progressbar') else 'tkinter'
    if data.get('family'):return data['family']
    if kind in ('Calendar','DateEntry'):return 'tkcalendar'
    if kind=='FileDropZone':return 'TkinterDnD2'
    if kind=='WebView':return 'tkinterweb'
    if kind=='LegacyVideoPlayer':return 'tkVideoPlayer'
    if kind in ('Notebook','Treeview'):return 'tkinter.ttk'
    return 'VisualTk' if data['module'] in ('visualtk_runtime','database_runtime') else data['module']
