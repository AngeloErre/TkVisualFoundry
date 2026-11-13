import unittest
from core import new_project
from project_problems import project_problems
class ProblemsTests(unittest.TestCase):
    def test_syntax_is_event_local(self):
        p=new_project();p['forms'][0]['events']={'Load':'x = 1\nif ('}
        rows=project_problems(p);self.assertEqual(rows[0]['line'],2);self.assertEqual(rows[0]['event'],'Load');self.assertEqual(rows[0]['severity'],'error')
    def test_static_references_and_assigned_attributes(self):
        p=new_project();p['startup']='self.custom = 1\nprint(self.custom)\nprint(self.MissingButton)'
        rows=project_problems(p);self.assertEqual(len(rows),1);self.assertEqual(rows[0]['line'],3)
    def test_import_diagnostics_do_not_execute_code(self):
        p=new_project();p['imports']='import missing_module\nraise RuntimeError("must not execute")'
        rows=project_problems(p,{'tkinter'});self.assertEqual(len(rows),1);self.assertEqual(rows[0]['object'],'$project')
    def test_strings_and_comments_are_not_references(self):
        p=new_project();p['startup']='# self.Unknown\nprint("self.Other")'
        self.assertEqual(project_problems(p),[])
