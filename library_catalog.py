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
