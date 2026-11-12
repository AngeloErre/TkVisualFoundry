import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core import new_project
from code_assist import completions,examples,signature

class AssistTests(unittest.TestCase):
    def setUp(self):
        self.p=new_project()
        self.button={'name':'Button1','kind':'Button','x':10,'y':20,'width':120,'height':35,'props':{'text':'Ciao'},'events':{}}
        self.entry={**self.button,'name':'Entry1','kind':'Entry','props':{}}
        self.p['forms'][0]['widgets']=[self.button,self.entry]

    def test_project_names_and_method_prefix(self):
        prefix,items=completions('self.But',self.p)
        self.assertEqual(prefix,'self.But');self.assertEqual([i[0] for i in items],['self.Button1'])
        prefix,items=completions('self.Button1.con',self.p)
        self.assertEqual(prefix,'self.Button1.con');self.assertEqual(items[0][0],'self.Button1.configure')

    def test_configure_properties(self):
        for text,prefix in [('self.Button1.configure(te','te'),('self.Button1.configure(','') ,('self.Button1.configure(bg="red", te','te')]:
            got,items=completions(text,self.p)
            self.assertEqual(got,prefix);self.assertIn('text=',[i[0] for i in items])

    def test_examples_are_valid_and_type_specific(self):
        button=examples(self.button,self.p);entry=examples(self.entry,self.p)
        self.assertIn("self.Button1.configure(text='Nuovo testo')",[x[1] for x in button])
        self.assertIn('self.Entry1.get()',[x[1] for x in entry])
        self.assertNotIn('self.Button1.get()',[x[1] for x in button])
        for obj in [self.button,self.entry,self.p['forms'][0]]:
            for label,code,doc in examples(obj,self.p):compile(code,'snippet','exec')

    def test_external_defaults_without_import(self):
        self.p['components']={'MyWidget':{'module':'not_installed_123','class':'Widget','defaults':{'custom_option':42},'requirements':[]}}
        widget={**self.button,'kind':'MyWidget','name':'MyWidget1','props':{}}
        self.p['forms'][0]['widgets'].append(widget)
        prefix,items=completions('self.MyWidget1.configure(cu',self.p)
        self.assertEqual(items[0][0],'custom_option=')
        self.assertNotIn('not_installed_123',sys.modules)

    def test_signatures_and_unknown_control(self):
        self.assertIn('text',signature('self.Button1.configure(',self.p))
        self.assertIn('Legge il testo',signature('self.Entry1.get(',self.p))
        self.assertEqual(completions('self.Unknown.',self.p),('',[]))
        self.assertEqual(completions('print(123)',self.p),('',[]))
