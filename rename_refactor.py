"""Reviewed, source-preserving object rename. Never executes submitted project code."""
from watch_values import rename_watch
from event_breakpoints import remap_lines
import ast
import copy
import unicodedata
from core import identifier,validate
from i18n import tr

def rewrite_source(body,mapping,form_rename=False,wrapped=True):
    lines=body.splitlines(keepends=True)
    text='def __vts_handler(self, event=None):\n'+''.join('    '+line for line in lines) if wrapped else body
    if wrapped and not body.strip():text+='    pass\n'
    try:tree=ast.parse(text)
    except SyntaxError as exc:raise ValueError(tr('Correggi gli errori di sintassi prima della rinomina.')) from exc
    offsets=[];position=0
    for line in lines:offsets.append(position);position+=len(line)
    edits=[];warnings=[]
    old=next(iter(mapping));new=mapping[old]
    def offset(row,column):
        row-=1 if wrapped else 0
        if not 1<=row<=len(lines):raise ValueError('Invalid source location')
        column-=4 if wrapped else 0
        return offsets[row-1]+len(lines[row-1].encode('utf-8')[:max(0,column)].decode('utf-8','ignore'))
    def replace(node,value,attribute=False):
        end=offset(node.end_lineno,node.end_col_offset)
        if attribute:
            start=end
            while start>0 and (('_'+body[start-1]).isidentifier()):start-=1
        else:start=offset(node.lineno,node.col_offset)
        edits.append((start,end,value,max(1,node.lineno-(1 if wrapped else 0))))
    class Visitor(ast.NodeVisitor):
        blocked=0
        def visit_ClassDef(self,node):
            self.blocked+=1;self.generic_visit(node);self.blocked-=1
        def visit_FunctionDef(self,node):
            shadow=node.name!='__vts_handler' and any(arg.arg=='self' for arg in node.args.posonlyargs+node.args.args+node.args.kwonlyargs)
            self.blocked+=int(shadow);self.generic_visit(node);self.blocked-=int(shadow)
        visit_AsyncFunctionDef=visit_FunctionDef
        def visit_Lambda(self,node):
            shadow=any(arg.arg=='self' for arg in node.args.posonlyargs+node.args.args+node.args.kwonlyargs)
            self.blocked+=int(shadow);self.generic_visit(node);self.blocked-=int(shadow)
        def visit_Attribute(self,node):
            if node.attr in mapping:
                if not self.blocked and isinstance(node.value,ast.Name) and node.value.id=='self':replace(node,mapping[node.attr],True)
                else:warnings.append((max(1,node.lineno-(1 if wrapped else 0)),tr('Riferimento ambiguo da controllare: ')+node.attr))
            self.generic_visit(node)
        def visit_Call(self,node):
            if not self.blocked:
                if form_rename and isinstance(node.func,ast.Attribute) and isinstance(node.func.value,ast.Name) and node.func.value.id=='self' and node.func.attr in ('show','hide'):
                    arg=node.args[0] if node.args else next((key.value for key in node.keywords if key.arg=='name'),None)
                    if isinstance(arg,ast.Constant) and arg.value==old:replace(arg,repr(new))
                    elif arg is not None and not isinstance(arg,ast.Constant):warnings.append((max(1,node.lineno-(1 if wrapped else 0)),tr('Accesso dinamico da controllare manualmente.')))
                if isinstance(node.func,ast.Name) and node.func.id in ('getattr','hasattr','setattr','delattr') and len(node.args)>=2 and isinstance(node.args[0],ast.Name) and node.args[0].id=='self':
                    arg=node.args[1]
                    if isinstance(arg,ast.Constant) and isinstance(arg.value,str) and arg.value in mapping:replace(arg,repr(mapping[arg.value]))
                    elif not isinstance(arg,ast.Constant):warnings.append((max(1,node.lineno-(1 if wrapped else 0)),tr('Accesso dinamico da controllare manualmente.')))
            self.generic_visit(node)
    visitor=Visitor()
    if wrapped and any(isinstance(node,ast.Name) and node.id=='self' and isinstance(node.ctx,ast.Store) for node in ast.walk(tree)):visitor.blocked=1
    visitor.visit(tree)
    # Apply from the end: every other byte/character, including comments and strings, is preserved.
    unique=sorted(set(edits),reverse=True);rewritten=body
    for start,end,value,_ in unique:rewritten=rewritten[:start]+value+rewritten[end:]
    return rewritten,[{'line':row,'before':body[start:end],'after':value} for start,end,value,row in sorted(unique)],warnings

def rename_project(project,old,new):
    validate(project,code=False)
    if not identifier(new) or unicodedata.normalize('NFKC',new)!=new:raise ValueError(tr('Nome Python non valido o riservato.'))
    objs={obj['name']:obj for form in project['forms'] for obj in [form]+form['widgets']}
    if unicodedata.normalize('NFKC',old)!=old:raise ValueError(tr('Nome non normalizzato: verifica i riferimenti manualmente.'))
    if old not in objs:raise ValueError(tr('Oggetto non trovato.'))
    if new in objs and new!=old:raise ValueError(tr('Nome già usato nel progetto.'))
    if old==new:return {'project':copy.deepcopy(project),'changes':[],'warnings':[]}
    snapshot=copy.deepcopy(project);mapping={old:new}
    for event in objs[old].get('events',{}):mapping['event_'+old+'_'+event]='event_'+new+'_'+event
    form_rename=any(form['name']==old for form in project['forms']);changes=[];warnings=[]
    def rewrite(obj,key,scope,wrapped):
        rewritten,edits,notes=rewrite_source(obj.get(key,''),mapping,form_rename,wrapped)
        obj[key]=rewritten
        changes.extend({**edit,'scope':scope} for edit in edits)
        warnings.extend({'scope':scope,'line':line,'message':message} for line,message in notes)
    rewrite(snapshot,'imports','$project/imports',False);rewrite(snapshot,'startup','$project/startup',True)
    for form in snapshot['forms']:
        for obj in [form]+form['widgets']:
            original_name=obj['name']
            for event in obj.get('events',{}):rewrite(obj['events'],event,original_name+'/'+event,True)
            if original_name==old:obj['name']=new;changes.append({'scope':original_name,'line':0,'before':old,'after':new})
            if obj.get('parent')==old:obj['parent']=new;changes.append({'scope':original_name+'/parent','line':0,'before':old,'after':new})
    for key,lines in list(snapshot.get('code_breakpoints',{}).items()):
        snapshot['code_breakpoints'][key]=remap_lines(project.get(key,''),snapshot.get(key,''),lines)
    for old_form,new_form in zip(project['forms'],snapshot['forms']):
        for old_obj,new_obj in zip([old_form]+old_form['widgets'],[new_form]+new_form['widgets']):
            for event,lines in list(new_obj.get('breakpoints',{}).items()):
                new_obj['breakpoints'][event]=remap_lines(old_obj.get('events',{}).get(event,''),new_obj.get('events',{}).get(event,''),lines)
    if 'watches' in snapshot:snapshot['watches']=list(dict.fromkeys(rename_watch(path,mapping) for path in snapshot['watches']))
    validate(snapshot)
    return {'project':snapshot,'changes':changes,'warnings':warnings}
