import ast
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from core import new_project,validate,generate,load
from event_breakpoints import remap_lines,resolve_breakpoints
from rename_refactor import rename_project

class EventBreakpointTests(unittest.TestCase):
    def project(self):
        p=new_project();p['forms'][0]['widgets']=[dict(name='Button1',kind='Button',x=10,y=10,width=100,height=30,props={},events={'Click':'# comment\nprevious = 1\nprevious += 2'},breakpoints={'Click':[2]})];return p
    def test_exact_event_mapping_with_embedded_runtime(self):
        p=self.project();p['forms'][0]['widgets'].append(dict(name='Frame1',kind='Frame',x=0,y=50,width=200,height=100,props={},events={},layout={'anchors':['left','right']}))
        source=generate(p);lines,unresolved=resolve_breakpoints(p,source);self.assertEqual(unresolved,[]);self.assertEqual(len(lines),1);self.assertEqual(source.splitlines()[next(iter(lines))-1].strip(),'previous = 1')
    def test_source_remap_insert_replace_delete(self):
        old='a=1\nb=2\nc=3';self.assertEqual(remap_lines(old,'# intro\n'+old,[2]),[3]);self.assertEqual(remap_lines(old,'a=1\nb=20\nc=3',[2]),[2]);self.assertEqual(remap_lines(old,'a=1\nc=3',[2]),[])
    def test_invalid_shape_and_unresolved_comment_or_missing_event(self):
        p=self.project();obj=p['forms'][0]['widgets'][0];obj['breakpoints']={'Click':[True]}
        with self.assertRaises(ValueError):validate(p)
        obj['breakpoints']={'Click':[1,99],'Load':[1]};source=generate(p);lines,unresolved=resolve_breakpoints(p,source);self.assertEqual(lines,set());self.assertEqual(len(unresolved),3)
    def test_project_sources_and_rename_round_trip(self):
        p=self.project();p['imports']='class Application:\n    pass\nuser_global = 3';p['startup']='self.Form1.deiconify()';p['code_breakpoints']={'imports':[3],'startup':[1]}
        renamed=rename_project(p,'Button1','GoButton')['project'];self.assertEqual(renamed['forms'][0]['widgets'][0]['breakpoints'],{'Click':[2]})
        source=generate(renamed);lines,unresolved=resolve_breakpoints(renamed,source);self.assertEqual(unresolved,[]);self.assertEqual(len(lines),3)
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'project.vtk.json';path.write_text(json.dumps(renamed));self.assertEqual(load(path),renamed)
    def test_real_pdb_stops_at_resolved_event_line_without_tk(self):
        p=self.project();source=generate(p);lines,_=resolve_breakpoints(p,source);line=next(iter(lines))
        # Execute the real generated method on an uninitialized object: it needs no Tk root.
        source='\n'.join(source.splitlines()[:ast.parse(source).body[-1].lineno-1])+"\napp = Application.__new__(Application)\napp.event_Button1_Click()\n"
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'app.py';path.write_text(source)
            result=subprocess.run([sys.executable,'-m','pdb','-c',f'break {line}','-c','continue',str(path)],input='p previous\nnext\np previous\nquit\n',text=True,capture_output=True,timeout=8)
            self.assertEqual(result.returncode,0,result.stderr);self.assertIn('previous = 1',result.stdout);self.assertIn('previous += 2',result.stdout);self.assertIn('\n1\n',result.stdout.replace('(Pdb) ',''))
