"""Static, project-aware Tkinter assistance; never imports user components."""
from i18n import tr
import re
from components import registry

METHODS = {
    'configure': ('**opzioni', tr('Modifica le proprietà del componente.')),
    'cget': ('"text"', tr('Legge una proprietà.')),
    'focus_set': ('', tr('Sposta il focus sul componente.')),
    'place_info': ('', tr('Legge posizione e dimensioni.')),
    'winfo_width': ('', tr('Legge la larghezza effettiva in pixel.')),
    'winfo_height': ('', tr('Legge l’altezza effettiva in pixel.')),
}
SPECIFIC = {
    'DatabaseView': {
        'connect': ('',tr('Apre la connessione in background; attendi DatabaseConnected.')),
        'refresh': ('',tr('Rilegge e visualizza i dati; attendi DataLoaded.')),
        'create_demo': ('',tr('Crea la tabella contatti su SQLite dopo la connessione.')),
        'insert_record': ('{"nome": "Mario", "email": "mario@example.com"}',tr('Aggiunge un record alla tabella selezionata (esempio contatti).')),
        'update_record': ('{"id": 1}, {"nome": "Nuovo nome"}',tr('Modifica un record tramite chiave primaria (esempio contatti).')),
        'delete_record': ('{"id": 1}',tr('Elimina un record tramite chiave primaria; chiedi conferma all’utente prima di chiamarlo.')),
    },
    'Button': {'invoke': ('', tr('Esegue il comando associato a command, se presente; non genera il Click del designer.'))},
    'Entry': {'get': ('', tr('Legge il testo.')), 'insert': ('0, "testo"', tr('Inserisce testo.')), 'delete': ('0, "end"', tr('Cancella il testo.'))},
    'Text': {'get': ('"1.0", "end-1c"', tr('Legge il contenuto.')), 'insert': ('"end", "testo"', tr('Aggiunge testo.')), 'delete': ('"1.0", "end"', tr('Cancella il contenuto.'))},
    'Combobox': {'get': ('', tr('Legge la selezione.')), 'set': ('"valore"', tr('Imposta il valore.')), 'current': ('0', tr('Seleziona per indice.'))},
    'Listbox': {'insert': ('"end", "elemento"', tr('Aggiunge un elemento.')), 'curselection': ('', tr('Legge gli indici selezionati.')), 'delete': ('0, "end"', tr('Cancella gli elementi.'))},
    'Scale': {'get': ('', tr('Legge il valore.')), 'set': ('50', tr('Imposta il valore.'))},
    'Progressbar': {'start': ('10', tr('Avvia l’animazione.')), 'stop': ('', tr('Ferma l’animazione.')), 'step': ('10', tr('Incrementa il valore.'))},
    'Treeview': {'insert': ('"", "end", text="Elemento"', tr('Aggiunge un nodo.')), 'selection': ('', tr('Legge i nodi selezionati.'))},
    'Canvas': {'create_text': ('30, 30, text="Ciao"', tr('Disegna testo.')), 'create_rectangle': ('10, 10, 100, 60', tr('Disegna un rettangolo.'))},
}


def objects(project):
    return {obj['name']:obj for form in project['forms'] for obj in [form]+form['widgets']}


def properties(obj, project):
    if 'kind' not in obj:return {'bg':obj.get('bg','white')}
    if obj.get('kind')=='DatabaseView':return {}
    props=dict(registry(project).get(obj['kind'],{}).get('defaults',{}));props.update(obj.get('props',{}))
    kind=obj['kind']
    if kind in ('Button','Label','Checkbutton','Radiobutton'):props.setdefault('text',obj['name'])
    if kind in ('Button','Label','Entry','Text','Checkbutton','Radiobutton','Listbox','Scale','Spinbox','Frame','Canvas'):
        props.setdefault('bg','#ffffff');props.setdefault('fg','#182230') if kind not in ('Frame','Canvas') else None
    if kind in ('Button','Entry','Text','Checkbutton','Radiobutton','Listbox','Combobox','Spinbox'):props.setdefault('state','normal')
    return props


def methods(obj):
    if 'kind' not in obj:
        return {'title': ('"Titolo"',tr('Cambia il titolo.')),'geometry': ('"640x440"',tr('Cambia dimensioni.')),'deiconify': ('',tr('Mostra la finestra.')),'withdraw': ('',tr('Nasconde la finestra.')),'configure': ('**opzioni',tr('Modifica proprietà della finestra.'))}
    if obj['kind']=='DatabaseView':return SPECIFIC['DatabaseView']
    return {**METHODS,**SPECIFIC.get(obj['kind'],{})}


def examples(obj, project):
    ref='self.'+obj['name'];result=[]
    props=properties(obj,project)
    for key,value in props.items():
        if not key.isidentifier():continue
        sample=tr('Nuovo testo') if key=='text' else ('disabled' if key=='state' else value)
        result.append((tr('Modifica {v0}', v0=f'{key}'),f'{ref}.configure({key}={sample!r})',tr('Imposta {v0}. Valore nel designer: {v1}.', v0=f'{key}', v1=f'{value!r}')))
    for method,(args,help_) in methods(obj).items():
        if method=='configure':continue
        if method=='cget' and 'text' not in props:args=repr(next(iter(props),'bg'))
        snippet=ref+'.'+method+'('+args+')'
        if obj.get('kind')=='DatabaseView' and method=='delete_record':snippet='if messagebox.askyesno("Elimina", "Eliminare il record?"):\n    '+snippet
        result.append((method+'('+args+')',snippet,help_))
    if obj.get('kind')=='DatabaseView':
        result.append((tr('Leggi riga selezionata'),f'record = {ref}.selected_record', tr('Dizionario della riga selezionata o None.')))
        result.append((tr('Leggi dati caricati'),f'records = {ref}.rows', tr('Usa nell’evento DataLoaded: lista di dizionari.')))
    for form in project['forms']:
        result.append((tr('Mostra ')+form['name'],f'self.show({form["name"]!r})',tr('Apre una finestra del progetto.')))
    result.append((tr('Messaggio informativo'),'messagebox.showinfo("Informazione", "Operazione completata")',tr('Mostra un messaggio.')))
    return result


def completions(before, project):
    objs=objects(project)
    # Named options inside configure/config, including after a comma.
    match=re.search(r'self\.(\w+)\.(?:configure|config)\([^()\n]*?(?:^|[,\s])([A-Za-z_]\w*)?$',before)
    if not match:match=re.search(r'self\.(\w+)\.(?:configure|config)\(([A-Za-z_]\w*)?$',before)
    if match and match.group(1) in objs:
        prefix=match.group(2) or '';obj=objs[match.group(1)]
        return prefix,[(k+'=',f'{k}: {v!r} — valore iniziale') for k,v in properties(obj,project).items() if k.startswith(prefix)]
    match=re.search(r'(self\.(\w+)\.)(\w*)$',before)
    if match and match.group(2) in objs:
        base,name,prefix=match.groups();obj=objs[name]
        items=[(base+k,help_+tr(' Firma: ')+k+'('+args+')') for k,(args,help_) in methods(obj).items() if k.startswith(prefix)]
        if obj.get('kind')=='DatabaseView':items += [(base+k,doc) for k,doc in [('rows',tr('Lista dei record caricati')),('selected_record',tr('Dizionario selezionato o None')),('last_error',tr('Ultimo errore database'))] if k.startswith(prefix)]
        return base+prefix,items
    match=re.search(r'self\.(\w*)$',before)
    if match:
        prefix='self.'+match.group(1)
        return prefix,[( 'self.'+name,tr('Componente del progetto')) for name in objs if ('self.'+name).startswith(prefix)]+[( 'self.'+name,doc) for name,doc in [('show','show("Form2"): mostra un form'),('hide','hide("Form2"): nasconde un form'),('root',tr('Finestra radice Tk'))] if ('self.'+name).startswith(prefix)]
    return '',[]


def signature(before, project):
    match=re.search(r'self\.(\w+)\.(\w+)\([^()]*$',before)
    if not match:return ''
    name,method=match.groups();obj=objects(project).get(name)
    if not obj:return ''
    info=methods(obj).get(method)
    if method in ('configure','config'):
        return f'{name}.{method}(opzione=valore) • '+', '.join(properties(obj,project))
    return (f'{name}.{method}({info[0]}) — {info[1]}' if info else '')
