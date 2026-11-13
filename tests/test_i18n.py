import ast
import copy
import json
import os
from pathlib import Path
import runpy
import string
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import i18n
from core import new_project, generate

ROOT=Path(__file__).resolve().parents[1]
class TranslationTests(unittest.TestCase):
    def setUp(self):self.previous_language=i18n.get_language()
    def tearDown(self):i18n.set_language(self.previous_language)
    def test_catalog_covers_calls(self):
        for file in ROOT.glob('*.py'):
            for node in ast.walk(ast.parse(file.read_text())):
                if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='tr' and node.args and isinstance(node.args[0],ast.Constant):
                    self.assertIn(node.args[0].value,i18n.EN_MESSAGES,str(file)+':'+str(node.lineno))
    def test_configuration_and_about_are_localized(self):
        self.assertEqual(i18n.tr('Configurazione…',language='en'),'Configuration…')
        self.assertIn('Visual Python',i18n.tr('VisualTk Studio 1.16\nDesigner visuale Python / Tkinter',language='en'))
    def test_format_fields_preserved(self):
        def fields(s):return {f for _,f,_,_ in string.Formatter().parse(s) if f is not None}
        for source,target in i18n.EN_MESSAGES.items():self.assertEqual(fields(source),fields(target),source)
    def test_translation_and_cancel(self):
        self.assertEqual(i18n.tr('Annulla',language='en'),'Undo')
        self.assertEqual(i18n.tr('Annulla',language='en',context='cancel'),'Cancel')
        self.assertEqual(i18n.tr('Connetti',language='it'),'Connetti')
    def test_settings_and_override(self):
        with tempfile.TemporaryDirectory() as d,patch.dict(os.environ,{},clear=True):
            path=Path(d)/'settings.json'
            self.assertEqual(i18n.configured_language(path),'it')
            path.write_text('{"language":"en"}');self.assertEqual(i18n.configured_language(path),'en')
            path.write_text('{"language":"xx"}');self.assertEqual(i18n.configured_language(path),'it')
            path.write_text('[]');self.assertEqual(i18n.configured_language(path),'it')
            os.environ['VTS_LANGUAGE']='en';self.assertEqual(i18n.configured_language(path),'en')
    def test_english_startup(self):
        code="import i18n,studio,workspace_ui; assert i18n.get_language()=='en'; assert 'Light' in workspace_ui.PRESETS; assert i18n.tr('Progetto')=='Project'"
        subprocess.run([sys.executable,'-c',code],cwd=ROOT,env={**os.environ,'VTS_LANGUAGE':'en'},check=True)
    def test_export_standalone_and_preserves_data(self):
        project=new_project('en');project['forms'][0]['title']='Titolo personale'
        project['forms'][0]['widgets']=[dict(name='Database1',kind='DatabaseView',x=0,y=0,width=500,height=250,props={},events={})]
        original=copy.deepcopy(project);source=generate(project);self.assertEqual(project,original)
        self.assertNotIn('from i18n import',source)
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'export.py';path.write_text(source)
            scope=runpy.run_path(str(path),run_name='export_test')
        self.assertEqual(scope['get_language'](),'en');self.assertEqual(scope['tr']('Connetti…'),'Connect…')
        del project['language'];self.assertIn("set_language('it')",generate(project))
