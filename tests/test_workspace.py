import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core import new_project,generate,validate
from i18n import tr
from workspace_ui import duplicate_form,PRESETS

class WorkspaceTests(unittest.TestCase):
    def test_duplicate_form_is_independent_and_generates(self):
        p=new_project();original=p['forms'][0]
        original['widgets']=[{'name':'Button1','kind':'Button','x':10,'y':10,'width':90,'height':30,'props':{'text':'Apri'},'events':{'Click':'self.show("Form2")'}}]
        duplicate=duplicate_form(p,0);p['forms'].append(duplicate)
        self.assertEqual(duplicate['name'],'Form2')
        self.assertEqual(duplicate['widgets'][0]['name'],'Button1_copy1')
        self.assertEqual(duplicate['widgets'][0]['events'],original['widgets'][0]['events'])
        duplicate['widgets'][0]['props']['text']='Altro'
        self.assertEqual(original['widgets'][0]['props']['text'],'Apri')
        validate(p);compile(generate(p),'generated','exec')
        again=duplicate_form(p,0)
        self.assertEqual(again['name'],'Form3');self.assertEqual(again['widgets'][0]['name'],'Button1_copy2')

    def test_presets_have_complete_hex_colors(self):
        keys=set(PRESETS[tr('Chiaro')])
        for preset in PRESETS.values():
            self.assertEqual(set(preset),keys)
            for value in preset.values():
                self.assertRegex(value,r'^#[0-9a-fA-F]{6}$')
