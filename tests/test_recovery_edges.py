import json
from pathlib import Path
import tempfile
import unittest
from core import new_project,generate,load,executable_body
from hierarchy import ordered_widgets
from project_problems import project_problems
from event_breakpoints import resolve_breakpoints

class RecoveryEdgeTests(unittest.TestCase):
    def test_blank_and_comment_only_bodies_compile_without_changing_project(self):
        for body in ('','   ','# TODO','# first\n\n    # second\n'):
            p=new_project();p['startup']=body;p['forms'][0]['events']={'Click':body};before=json.dumps(p)
            source=generate(p);compile(source,'comment-only','exec');self.assertEqual(json.dumps(p),before)
            self.assertFalse([i for i in project_problems(p) if i['severity']=='error'])
            self.assertTrue(executable_body(body).endswith('pass'))
    def test_real_syntax_errors_remain_visible(self):
        p=new_project();p['forms'][0]['events']={'Click':'if True:\n# missing body'}
        with self.assertRaises(SyntaxError):generate(p)
        self.assertTrue(any(i['severity']=='error' for i in project_problems(p)))
    def test_user_line_offsets_are_preserved(self):
        body='# comment\nvalue = 3\nprint(value)';self.assertEqual(executable_body(body),body)
        p=new_project();p['startup']=body;p['code_breakpoints']={'startup':[2]}
        source=generate(p);lines,unresolved=resolve_breakpoints(p,source)
        self.assertFalse(unresolved);self.assertTrue(any(source.splitlines()[line-1].strip()=='value = 3' for line in lines))
    def test_utf8_bom_project_opens_without_rewriting_file(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'project.vtk.json';p=new_project();path.write_bytes(b'\xef\xbb\xbf'+json.dumps(p,ensure_ascii=False).encode());before=path.read_bytes()
            self.assertEqual(load(path),p);self.assertEqual(path.read_bytes(),before)
    def test_deep_hierarchy_orders_parents_without_recursion(self):
        p=new_project();p['forms'][0]['widgets']=[dict(name='Frame'+str(i),kind='Frame',parent='Frame'+str(i+1) if i<1499 else 'Form1',x=0,y=0,width=100,height=100,props={},events={}) for i in range(1500)]
        ordered=ordered_widgets(p['forms'][0]);self.assertEqual(ordered[0]['name'],'Frame1499');self.assertEqual(ordered[-1]['name'],'Frame0')
        compile(generate(p),'deep','exec')
    def test_deep_cycle_and_stable_sibling_order(self):
        form={'name':'Form1','widgets':[dict(name='Frame'+str(i),kind='Frame',parent='Frame'+str((i+1)%1500),props={}) for i in range(1500)]}
        with self.assertRaisesRegex(ValueError,'Container cycle'):ordered_widgets(form)
        form['widgets']=[dict(name='Child',kind='Button',parent='Outer'),dict(name='Sibling',kind='Button'),dict(name='Outer',kind='Frame')]
        self.assertEqual([w['name'] for w in ordered_widgets(form)],['Outer','Child','Sibling'])
