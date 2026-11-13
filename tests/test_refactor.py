import copy
import unittest
from core import new_project,generate
from rename_refactor import rename_project
class RenameTests(unittest.TestCase):
    def project(self):
        p=new_project();p['forms'][0]['widgets']=[dict(name='Button1',kind='Button',x=10,y=10,width=90,height=30,props={'text':'Button1'},events={'Click':'self.Button1.configure(text="Button1") # self.Button1\nself.event_Button1_Click()'})];return p
    def test_static_references_and_event_methods_preserve_strings_comments(self):
        p=self.project();original=copy.deepcopy(p);plan=rename_project(p,'Button1','SaveButton');self.assertEqual(p,original)
        button=plan['project']['forms'][0]['widgets'][0]
        self.assertEqual(button['props']['text'],'Button1');self.assertIn('self.SaveButton.configure(text="Button1") # self.Button1',button['events']['Click']);self.assertIn('self.event_SaveButton_Click()',button['events']['Click'])
        compile(generate(plan['project']),'renamed','exec')
    def test_form_name_and_parent_and_literal_show_calls(self):
        p=self.project();p['forms'][0]['widgets'][0]['parent']='Form1';p['startup']='self.show("Form1")\nself.hide("Form1")\nself.show(name="Form1")'
        plan=rename_project(p,'Form1','MainForm')['project'];self.assertEqual(plan['forms'][0]['name'],'MainForm');self.assertEqual(plan['forms'][0]['widgets'][0]['parent'],'MainForm');self.assertIn("self.show('MainForm')",plan['startup']);self.assertIn("name='MainForm'",plan['startup'])
    def test_unicode_locations_and_reflective_literal(self):
        p=self.project();p['startup']='text = "città"; self.Button1.configure(text=text)\ngetattr(self, "Button1").invoke()'
        code=rename_project(p,'Button1','Pulsante')['project']['startup'];self.assertIn('"città"; self.Pulsante',code);self.assertIn("getattr(self, 'Pulsante')",code)
    def test_class_and_shadowed_self_are_not_renamed(self):
        p=self.project();p['imports']='class Other:\n    def method(self):\n        return self.Button1'
        plan=rename_project(p,'Button1','SaveButton');self.assertEqual(plan['project']['imports'],p['imports']);self.assertTrue(plan['warnings'])
    def test_collision_and_syntax_errors_leave_original_unchanged(self):
        p=self.project();original=copy.deepcopy(p)
        for name in ('Form1','root','not valid'):
            with self.assertRaises(ValueError):rename_project(p,'Button1',name)
        self.assertEqual(p,original);p['startup']='if ('
        with self.assertRaises(ValueError):rename_project(p,'Button1','SaveButton')
    def test_reassigned_self_is_left_for_manual_review(self):
        p=self.project();p['startup']='self = other\nprint(self.Button1)'
        plan=rename_project(p,'Button1','SaveButton')
        self.assertEqual(plan['project']['startup'],p['startup']);self.assertTrue(plan['warnings'])
