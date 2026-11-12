"""Static, project-aware Tkinter assistance; never imports user components."""
import re
from components import registry

METHODS = {
    'configure': ('**opzioni', 'Modifica le proprietà del componente.'),
    'cget': ('"text"', 'Legge una proprietà.'),
    'focus_set': ('', 'Sposta il focus sul componente.'),
    'place_info': ('', 'Legge posizione e dimensioni.'),
    'winfo_width': ('', 'Legge la larghezza effettiva in pixel.'),
    'winfo_height': ('', 'Legge l’altezza effettiva in pixel.'),
}
SPECIFIC = {
    'Button': {'invoke': ('', 'Esegue il comando associato a command, se presente; non genera il Click del designer.')},
    'Entry': {'get': ('', 'Legge il testo.'), 'insert': ('0, "testo"', 'Inserisce testo.'), 'delete': ('0, "end"', 'Cancella il testo.')},
    'Text': {'get': ('"1.0", "end-1c"', 'Legge il contenuto.'), 'insert': ('"end", "testo"', 'Aggiunge testo.'), 'delete': ('"1.0", "end"', 'Cancella il contenuto.')},
    'Combobox': {'get': ('', 'Legge la selezione.'), 'set': ('"valore"', 'Imposta il valore.'), 'current': ('0', 'Seleziona per indice.')},
    'Listbox': {'insert': ('"end", "elemento"', 'Aggiunge un elemento.'), 'curselection': ('', 'Legge gli indici selezionati.'), 'delete': ('0, "end"', 'Cancella gli elementi.')},
    'Scale': {'get': ('', 'Legge il valore.'), 'set': ('50', 'Imposta il valore.')},
    'Progressbar': {'start': ('10', 'Avvia l’animazione.'), 'stop': ('', 'Ferma l’animazione.'), 'step': ('10', 'Incrementa il valore.')},
    'Treeview': {'insert': ('"", "end", text="Elemento"', 'Aggiunge un nodo.'), 'selection': ('', 'Legge i nodi selezionati.')},
    'Canvas': {'create_text': ('30, 30, text="Ciao"', 'Disegna testo.'), 'create_rectangle': ('10, 10, 100, 60', 'Disegna un rettangolo.')},
}


def objects(project):
    return {obj['name']:obj for form in project['forms'] for obj in [form]+form['widgets']}


def properties(obj, project):
    if 'kind' not in obj:return {'bg':obj.get('bg','white')}
    props=dict(registry(project).get(obj['kind'],{}).get('defaults',{}));props.update(obj.get('props',{}))
    kind=obj['kind']
    if kind in ('Button','Label','Checkbutton','Radiobutton'):props.setdefault('text',obj['name'])
    if kind in ('Button','Label','Entry','Text','Checkbutton','Radiobutton','Listbox','Scale','Spinbox','Frame','Canvas'):
        props.setdefault('bg','#ffffff');props.setdefault('fg','#182230') if kind not in ('Frame','Canvas') else None
    if kind in ('Button','Entry','Text','Checkbutton','Radiobutton','Listbox','Combobox','Spinbox'):props.setdefault('state','normal')
    return props


def methods(obj):
    if 'kind' not in obj:
        return {'title': ('"Titolo"','Cambia il titolo.'),'geometry': ('"640x440"','Cambia dimensioni.'),'deiconify': ('','Mostra la finestra.'),'withdraw': ('','Nasconde la finestra.'),'configure': ('**opzioni','Modifica proprietà della finestra.')}
    return {**METHODS,**SPECIFIC.get(obj['kind'],{})}


def examples(obj, project):
    ref='self.'+obj['name'];result=[]
    props=properties(obj,project)
    for key,value in props.items():
        if not key.isidentifier():continue
        sample='Nuovo testo' if key=='text' else ('disabled' if key=='state' else value)
        result.append((f'Modifica {key}',f'{ref}.configure({key}={sample!r})',f'Imposta {key}. Valore nel designer: {value!r}.'))
    for method,(args,help_) in methods(obj).items():
        if method=='configure':continue
        if method=='cget' and 'text' not in props:args=repr(next(iter(props),'bg'))
        result.append((method+'('+args+')',ref+'.'+method+'('+args+')',help_))
    for form in project['forms']:
        result.append(('Mostra '+form['name'],f'self.show({form["name"]!r})','Apre una finestra del progetto.'))
    result.append(('Messaggio informativo','messagebox.showinfo("Informazione", "Operazione completata")','Mostra un messaggio.'))
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
        return base+prefix,[(base+k,help_+' Firma: '+k+'('+args+')') for k,(args,help_) in methods(obj).items() if k.startswith(prefix)]
    match=re.search(r'self\.(\w*)$',before)
    if match:
        prefix='self.'+match.group(1)
        return prefix,[( 'self.'+name,'Componente del progetto') for name in objs if ('self.'+name).startswith(prefix)]+[( 'self.'+name,doc) for name,doc in [('show','show("Form2"): mostra un form'),('hide','hide("Form2"): nasconde un form'),('root','Finestra radice Tk')] if ('self.'+name).startswith(prefix)]
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
