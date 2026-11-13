"""Persisted source-local breakpoints and non-executing generated-line mapping."""
import ast
import difflib
import types


def validate_breakpoints(obj,project=False):
    field='code_breakpoints' if project else 'breakpoints';data=obj.get(field,{})
    if not isinstance(data,dict):raise ValueError('Invalid breakpoint settings.')
    for key,lines in data.items():
        if not isinstance(key,str) or project and key not in ('startup','imports'):raise ValueError('Invalid breakpoint scope.')
        if not isinstance(lines,list) or any(type(line) is not int or not 1<=line<=100000 for line in lines) or len(lines)!=len(set(lines)):raise ValueError('Breakpoints require unique positive line numbers.')


def remap_lines(old,new,lines):
    if not lines:return []
    if old==new:return sorted(set(lines))
    mapped=[];opcodes=difflib.SequenceMatcher(None,old.splitlines(),new.splitlines(),autojunk=True).get_opcodes()
    for line in lines:
        for tag,a,b,c,d in opcodes:
            if a<=line-1<b:
                offset=line-1-a
                if tag=='equal' or tag=='replace' and offset<d-c:mapped.append(c+offset+1)
                break
    return sorted(set(mapped))


def source_points(project):
    for key,lines in project.get('code_breakpoints',{}).items():
        for line in lines:yield '$project',key,line
    for form in project['forms']:
        for obj in [form]+form['widgets']:
            for event,lines in obj.get('breakpoints',{}).items():
                for line in lines:yield obj['name'],event,line


def resolve_breakpoints(project,source):
    """Return exact executable source lines and unresolved source-local locations."""
    points=list(source_points(project))
    if not points:return set(),[]
    tree=ast.parse(source);application=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Application'][-1]
    methods={n.name:n for n in application.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
    executable=set()
    def collect(code):
        executable.update(line for _,_,line in code.co_lines() if line)
        for value in code.co_consts:
            if isinstance(value,types.CodeType):collect(value)
    collect(compile(source,'application.py','exec'))
    resolved=set();unresolved=[]
    for obj,event,line in points:
        method=methods.get('startup' if obj=='$project' and event=='startup' else 'event_'+obj+'_'+event)
        if obj=='$project' and event=='imports':
            body=project.get('imports','');start=source.splitlines().index('import traceback')+1;target=start+line
        else:
            body=project.get('startup','') if obj=='$project' else next((o.get('events',{}).get(event,'') for f in project['forms'] for o in [f]+f['widgets'] if o['name']==obj),'')
            target=method.lineno+line if method else None
        rows=body.splitlines()
        if target and 0<line<=len(rows) and rows[line-1].strip() and not rows[line-1].lstrip().startswith('#') and target in executable:resolved.add(target)
        else:unresolved.append((obj,event,line))
    return resolved,unresolved
