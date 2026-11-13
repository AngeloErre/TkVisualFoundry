"""Persistent watch paths resolved only against already serialized inspector nodes."""
import ast
from i18n import tr


def parse_watch(expression):
    if not isinstance(expression,str) or not expression.strip() or len(expression)>256:raise ValueError(tr('Usa un percorso di variabile con al massimo 256 caratteri.'))
    try:node=ast.parse(expression.strip(),mode='eval').body
    except (SyntaxError,ValueError) as exc:raise ValueError(tr('Percorso Watch non valido.')) from exc
    steps=[]
    while not isinstance(node,ast.Name):
        if isinstance(node,ast.Attribute):steps.append(('attribute',node.attr));node=node.value
        elif isinstance(node,ast.Subscript) and isinstance(node.slice,ast.Constant) and type(node.slice.value) in (str,int) and (not isinstance(node.slice.value,int) or node.slice.value>=0):steps.append(('index',node.slice.value));node=node.value
        else:raise ValueError(tr('Le Watch accettano nomi, attributi, indici interi non negativi e chiavi stringa; chiamate e calcoli non sono supportati.'))
        if len(steps)>16:raise ValueError(tr('Percorso Watch troppo profondo.'))
    return node.id,list(reversed(steps))


def validate_watches(project):
    paths=project.get('watches',[])
    if not isinstance(paths,list) or len(paths)>100 or len(set(p for p in paths if isinstance(p,str)))!=len(paths):raise ValueError(tr('Usa al massimo 100 percorsi Watch distinti.'))
    for path in paths:parse_watch(path)


def resolve_watch(expression,snapshot):
    root,steps=parse_watch(expression)
    if not snapshot:return None,''
    groups=snapshot.get('groups',[]);scope={'self':'self','globals':'globals','locals':'locals','last':'last locals'}.get(root)
    if scope:
        if not steps or steps[0][0]!='attribute':return None,''
        name=steps[0][1];steps=steps[1:];candidates=[g for g in groups if g.get('scope')==scope]
    else:
        name=root;candidates=[g for s in ('locals','globals','last locals') for g in groups if g.get('scope')==s]
    for group in candidates:
        node=next((v for v in group.get('values',[]) if v.get('name')==name),None)
        if node is None:continue
        origin=group.get('scope','')+' · '+group.get('name','')
        if group.get('file'):origin+=' · '+group['file']
        for kind,key in steps:
            found=None
            for child in node.get('children',[]):
                if kind=='attribute' and child.get('name')==key:found=child;break
                if kind=='index':
                    try:actual=ast.literal_eval(child.get('name',''))
                    except (ValueError,SyntaxError):continue
                    if type(actual) in (str,int,bool) and actual==key:found=child;break
            node=found
            if node is None:return None,origin
        return node,origin
    return None,''


def rename_watch(expression,mapping):
    parse_watch(expression);tree=ast.parse(expression.strip(),mode='eval');changed=False
    for node in ast.walk(tree):
        if isinstance(node,ast.Attribute) and isinstance(node.value,ast.Name) and node.value.id=='self' and node.attr in mapping:
            node.attr=mapping[node.attr];changed=True
    return ast.unparse(tree) if changed else expression
