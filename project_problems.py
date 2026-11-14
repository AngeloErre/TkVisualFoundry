"""Non-executing project diagnostics with event-local source locations."""
import ast
import json
import subprocess
from i18n import tr
from core import executable_body

def sources(project):
    yield '$project','imports',project.get('imports',''),False
    yield '$project','startup',project.get('startup',''),True
    for form in project['forms']:
        for obj in [form]+form['widgets']:
            for event,body in obj.get('events',{}).items():yield obj['name'],event,body,True

def module_inventory(python,root):
    script='import sys,json,importlib.metadata as m; print(json.dumps(sorted(set(sys.stdlib_module_names)|set(m.packages_distributions()))))'
    result=subprocess.run([python,'-c',script],capture_output=True,text=True,timeout=15)
    if result.returncode:raise RuntimeError(result.stderr[-1000:])
    modules=set(json.loads(result.stdout))
    if root:
        for path in root.iterdir():
            if path.is_file() and path.suffix=='.py' and path.stem.isidentifier():modules.add(path.stem)
            elif path.is_dir() and path.name.isidentifier():modules.add(path.name)
    return modules

def project_problems(project,available_modules=None):
    known={'root','show','hide','startup','_error','_theme_style','_app_icon'}|{o['name'] for f in project['forms'] for o in [f]+f['widgets']}
    trees=[];issues=[]
    for obj,event,body,wrapped in sources(project):
        text='def handler(self, event=None):\n'+''.join('    '+line+'\n' for line in executable_body(body).splitlines()) if wrapped else body
        try:tree=ast.parse(text);trees.append((obj,event,tree,wrapped))
        except SyntaxError as exc:issues.append({'severity':'error','object':obj,'event':event,'line':max(1,(exc.lineno or 1)-(1 if wrapped else 0)),'column':max(0,(exc.offset or 1)-1-(4 if wrapped else 0)),'message':exc.msg})
    for _,_,tree,_ in trees:
        for node in ast.walk(tree):
            if isinstance(node,ast.Attribute) and isinstance(node.value,ast.Name) and node.value.id=='self' and isinstance(node.ctx,ast.Store):known.add(node.attr)
    for obj,event,tree,wrapped in trees:
        for node in ast.walk(tree):
            message=None
            if isinstance(node,ast.Attribute) and isinstance(node.value,ast.Name) and node.value.id=='self' and isinstance(node.ctx,ast.Load) and node.attr not in known:message=tr('Riferimento self non riconosciuto: ')+node.attr
            elif available_modules is not None and isinstance(node,(ast.Import,ast.ImportFrom)):
                names=[a.name.split('.')[0] for a in node.names] if isinstance(node,ast.Import) else ([node.module.split('.')[0]] if node.module and not node.level else [])
                missing=[name for name in names if name not in available_modules]
                if missing:message=tr('Modulo non rilevato nell’ambiente: ')+', '.join(missing)
            if message:issues.append({'severity':'warning','object':obj,'event':event,'line':max(1,node.lineno-(1 if wrapped else 0)),'column':max(0,node.col_offset-(4 if wrapped else 0)),'message':message})
    return sorted(issues,key=lambda row:(row['severity']!='error',row['object'],row['event'],row['line']))
