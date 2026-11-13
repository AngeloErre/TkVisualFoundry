"""Offline component reference and optional official/installed documentation."""
from components import registry
from code_assist import properties, methods, examples
from i18n import tr
from urllib.parse import urlparse

URLS={
 'tkinter':'https://docs.python.org/3/library/tkinter.html',
 'tkinter.ttk':'https://docs.python.org/3/library/tkinter.ttk.html',
 'tkinter.scrolledtext':'https://docs.python.org/3/library/tkinter.scrolledtext.html',
 'customtkinter':'https://customtkinter.tomschimansky.com/documentation/',
 'tkcalendar':'https://tkcalendar.readthedocs.io/en/stable/',
 'tksheet':'https://ragardner.github.io/tksheet/DOCUMENTATION.html',
 'tkintermapview':'https://github.com/TomSchimansky/TkinterMapView',
 'tkinterweb':'https://tkinterweb.readthedocs.io/en/latest/',
 'Pmw':'https://pmw.sourceforge.net/',
 'visualtk_runtime':'https://github.com/AngeloErre/VisualTkStudio',
 'integration_runtime':'https://github.com/AngeloErre/VisualTkStudio',
 'database_runtime':'https://docs.python.org/3/library/sqlite3.html',
 'productivity_runtime':'https://github.com/AngeloErre/VisualTkStudio',
}

KIND_URLS={
 'Sheet':'https://ragardner.github.io/tksheet/DOCUMENTATION.html',
 'MapView':'https://github.com/TomSchimansky/TkinterMapView',
 'CTkTabview':URLS['customtkinter'], 'Notebook':URLS['tkinter.ttk'],
 'ImageGallery':'https://pillow.readthedocs.io/en/stable/',
 'AudioPlayer':'https://pyga.me/docs/', 'WebcamView':'https://docs.opencv.org/4.x/',
 'USBExplorer':'https://github.com/pyusb/pyusb', 'SerialMonitor':'https://pyserial.readthedocs.io/en/latest/',
 'MIDIPlayer':'https://mido.readthedocs.io/en/stable/',
 'ExcelWorkbook':'https://openpyxl.readthedocs.io/en/stable/',
 'PDFDocument':'https://pypdf.readthedocs.io/en/stable/',
 'WebView':URLS['tkinterweb'],
}
PROVIDER_URLS={'openai':'https://platform.openai.com/docs/overview','anthropic':'https://docs.anthropic.com/en/docs/overview',
 'gemini':'https://ai.google.dev/gemini-api/docs','drive':'https://developers.google.com/drive/api/guides/about-sdk',
 's3':'https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html',
 'webdav':'https://www.rfc-editor.org/rfc/rfc4918'}

def valid_url(url):
    parsed=urlparse(url)
    return parsed.scheme=='https' and bool(parsed.hostname) and not parsed.username and not parsed.password

def reference(obj,project):
    kind=obj.get('kind','Tk');spec=registry(project).get(kind,{})
    module=spec.get('module','tkinter.ttk' if kind in ('Combobox','Progressbar') else 'tkinter')
    cls=spec.get('class',kind)
    url=spec.get('documentation') or KIND_URLS.get(kind) or URLS.get(module,URLS.get(module.split('.')[0],''))
    if kind in ('CloudStorage','LLMClient'):url=PROVIDER_URLS.get(obj.get('props',{}).get('provider','drive' if kind=='CloudStorage' else 'openai'),'')
    if not valid_url(url):url=''
    parts=[obj['name']+' • '+kind, module+'.'+cls, spec.get('description',''),
           tr('Proprietà modificabili da codice')]
    parts += [f'{key}: {type(value).__name__} = {value!r}' for key,value in properties(obj,project).items()]
    parts += ['',tr('Metodi ed esempi')]
    parts += [f'{name}({args})\n{doc}' for name,(args,doc) in methods(obj).items()]
    parts += ['']+[snippet for _,snippet,_ in examples(obj,project)[:8]]
    if spec.get('defaults'):parts += ['',tr('Configurazione nel designer'),repr(spec['defaults'])]
    from dependency_manager import component_requirements
    parts += ['',tr('Pacchetti richiesti'),', '.join(component_requirements(project,kind,obj.get('props',{}))) or tr('Libreria standard')]
    return {'text':'\n\n'.join(parts),'url':url,'module':module,'class':cls}

def documentation_urls(project):
    return sorted(set(URLS.values()) | set(KIND_URLS.values()) | set(PROVIDER_URLS.values()) | {s['documentation'] for s in registry(project).values() if valid_url(s.get('documentation',''))})
