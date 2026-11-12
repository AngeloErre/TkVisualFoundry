import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from database_runtime import DatabaseSession,parse_database_value
from core import new_project,generate,validate
from components import BUILTINS,requirements
from code_assist import examples,completions

class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.db=DatabaseSession();self.db.connect(database=':memory:');self.db.create_demo();self.db.use_table('contatti')
    def tearDown(self):self.db.disconnect()
    def test_full_crud_and_parameter_binding(self):
        value="O'Reilly'); DROP TABLE contatti; --"
        key=self.db.insert({'nome':value,'email':None})
        row=self.db.fetch()[0];self.assertEqual(row['nome'],value);self.assertIsNone(row['email'])
        self.db.update({'id':key},{'nome':'Nuovo','email':''});self.assertEqual(self.db.fetch()[0]['email'],'')
        self.db.delete({'id':key});self.assertEqual(self.db.fetch(),[]);self.assertIn('contatti',self.db.tables())
    def test_errors_roll_back_and_keep_original(self):
        key=self.db.insert({'nome':'Mario'})
        with self.assertRaises(Exception):self.db.update({'id':key},{'nome':None})
        self.assertEqual(self.db.fetch()[0]['nome'],'Mario')
        for operation in (lambda:self.db.update({}, {'nome':'x'}),lambda:self.db.delete({'id':None}),lambda:self.db.update({'id':key},{'id':2}),lambda:self.db.delete({'id':999})):
            with self.assertRaises(ValueError):operation()
        self.assertEqual(len(self.db.fetch()),1)
    def test_unknown_identifiers_and_unkeyed_table(self):
        with self.assertRaises(ValueError):self.db.use_table('contatti; DROP TABLE contatti')
        with self.assertRaises(ValueError):self.db.insert({'not_a_column':'x'})
        self.db.connection.execute('CREATE TABLE no_key (value TEXT)');self.db.use_table('no_key');self.db.insert({'value':'x'})
        self.assertEqual(len(self.db.fetch()),1)
        with self.assertRaises(ValueError):self.db.delete({})
    def test_composite_key_and_quoted_identifiers(self):
        self.db.connection.execute('CREATE TABLE "odd table" (a INTEGER, b INTEGER, "odd column" TEXT, PRIMARY KEY(a,b))')
        self.db.use_table('odd table');self.db.insert({'a':1,'b':2,'odd column':'original'})
        with self.assertRaises(ValueError):self.db.update({'a':1},{'odd column':'bad'})
        self.db.update({'a':1,'b':2},{'odd column':'ok'});self.assertEqual(self.db.fetch()[0]['odd column'],'ok')
    def test_file_reconnect_and_limits(self):
        with tempfile.TemporaryDirectory() as folder:
            path=str(Path(folder)/'demo.sqlite');self.db.connect(database=path);self.db.create_demo();self.db.use_table('contatti')
            for n in range(3):self.db.insert({'nome':str(n)})
            self.assertEqual(len(self.db.fetch(limit=2)),2);self.db.disconnect();self.db.connect(database=path);self.assertEqual(len(self.db.fetch('contatti')),3)
    def test_demo_does_not_overwrite_data(self):
        self.db.insert({'nome':'Conservato'});self.db.create_demo();self.assertEqual(self.db.fetch()[0]['nome'],'Conservato')
    def test_types_and_null_distinction(self):
        self.assertEqual(parse_database_value('42','INTEGER'),42)
        self.assertEqual(parse_database_value('false','BOOLEAN'),False)
        self.assertEqual(parse_database_value('','TEXT'),'')
        self.assertEqual(str(parse_database_value('2026-11-12','DATE')),'2026-11-12')
        with self.assertRaises(ValueError):parse_database_value('x','INTEGER')
    def test_standalone_generation_and_driver_requirements(self):
        p=new_project();d=BUILTINS['DatabaseView'];w={'name':'Database1','kind':'DatabaseView','x':0,'y':0,'width':650,'height':400,'props':copy.deepcopy(d['defaults']),'events':{'DataLoaded':'records = self.Database1.rows'}};p['forms'][0]['widgets']=[w]
        self.assertEqual(requirements(p),[]);source=generate(p);compile(source,'database_app.py','exec')
        self.assertIn('class DatabaseSession:',source);self.assertNotIn('from database_runtime import',source)
        self.assertIn("bind('<<DataLoaded>>'",source)
        w['props']['backend']='postgresql';self.assertIn('psycopg[binary]>=3',requirements(p));self.assertIn('SQLAlchemy>=2.0',requirements(p))
        w['props']['backend']='mysql';self.assertIn('PyMySQL>=1.1',requirements(p));self.assertNotIn('psycopg[binary]>=3',requirements(p))
        for label,snippet,doc in examples(w,p):compile(snippet,'example','exec')
        self.assertNotIn('self.Database1.configure(backend=',str(examples(w,p)))
        self.assertIn('self.Database1.selected_record',[v[0] for v in completions('self.Database1.sel',p)[1]])

class RemoteConnectionTests(unittest.TestCase):
    def test_remote_url_fields_and_failed_connection_cleanup(self):
        import types
        engine=types.SimpleNamespace(connect=lambda:(_ for _ in ()).throw(OSError('failure')),dispose=lambda:None)
        from unittest.mock import Mock
        create=Mock(return_value=engine);dispose=Mock();engine.dispose=dispose;url=Mock(return_value='opaque_url')
        fake=types.ModuleType('sqlalchemy');fake.create_engine=create;sub=types.ModuleType('sqlalchemy.engine');sub.URL=types.SimpleNamespace(create=url)
        with patch.dict(sys.modules,{'sqlalchemy':fake,'sqlalchemy.engine':sub}):
            db=DatabaseSession()
            with self.assertRaisesRegex(RuntimeError,'Connessione remota non riuscita'):
                db.connect(backend='postgresql',database='example',username='test',password='secret@:/',host='localhost',port=5432)
        self.assertEqual(url.call_args.kwargs['password'],'secret@:/');self.assertEqual(url.call_args.args[0],'postgresql+psycopg')
        self.assertTrue(create.call_args.kwargs['hide_parameters']);dispose.assert_called_once()

class DatabaseUITests(unittest.TestCase):
    def test_async_connect_refresh_and_selection(self):
        from test_studio import GUI
        if not GUI:self.skipTest('Sessione grafica macOS non disponibile')
        import tkinter as tk,time
        from database_runtime import DatabaseView
        root=tk.Tk();root.withdraw();widget=DatabaseView(root,database=':memory:');widget.pack()
        def wait():
            deadline=time.monotonic()+5
            while widget.busy and time.monotonic()<deadline:root.update();time.sleep(.01)
            self.assertFalse(widget.busy,widget.state.get())
        try:
            widget.connect();wait();self.assertTrue(widget.connected);widget.create_demo();wait();widget.insert_record({'nome':'Mario'});wait()
            self.assertEqual(widget.rows[0]['nome'],'Mario');widget.gridview.selection_set('0');root.update();widget.select_record();self.assertEqual(widget.selected_record['nome'],'Mario')
        finally:widget.destroy();root.destroy()
