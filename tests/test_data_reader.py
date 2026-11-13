import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from data_reader import preview,difference,table_result,MAX_ROWS

class DataReaderTests(unittest.TestCase):
    def setUp(self):self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def file(self,name,text):
        p=self.root/name;p.write_text(text,encoding='utf-8');return p
    def test_sqlite_read_only_refresh_and_wal(self):
        p=self.root/'test.db';con=sqlite3.connect(p);con.execute('PRAGMA journal_mode=WAL');con.execute('CREATE TABLE "strange""name" (id INTEGER, value TEXT)');con.execute('INSERT INTO "strange""name" VALUES (1,?)',('before',));con.commit()
        first=preview(p);self.assertEqual(first['rows'],[['1','before']])
        con.execute('UPDATE "strange""name" SET value=?',('after',));con.commit();second=preview(p)
        self.assertEqual(difference(first,second),{'added':1,'removed':1,'columns_changed':False});self.assertEqual(con.execute('SELECT value FROM "strange""name"').fetchone()[0],'after');con.close()
    def test_missing_database_is_not_created(self):
        p=self.root/'missing.db'
        with self.assertRaises(FileNotFoundError):preview(p)
        self.assertFalse(p.exists())
    def test_sql_script_is_never_executed(self):
        p=self.file('danger.sql','DROP TABLE users;\nINSERT INTO users VALUES (1);')
        before=p.read_bytes();data=preview(p);self.assertEqual(data['rows'][0],['1','DROP TABLE users;\n']);self.assertEqual(p.read_bytes(),before)
    def test_csv_bom_semicolon_and_multiline(self):
        p=self.file('data.csv','\ufeffid;descrizione\n1;"caffè\nlungo"\n2;"test"\n');data=preview(p)
        self.assertEqual(data['columns'],['id','descrizione']);self.assertEqual(data['rows'][0],['1','caffè\nlungo'])
    def test_json_multiple_datasets_and_union(self):
        p=self.file('data.json',json.dumps({'users':[{'id':1,'x':{'a':2}},{'name':'Ada'}],'items':[3,4]}));data=preview(p)
        self.assertEqual(data['columns'],['id','x','name']);self.assertIn('"a": 2',data['rows'][0][1]);self.assertEqual(preview(p,'items')['rows'],[['3'],['4']])
    def test_ndjson_and_row_bounds(self):
        p=self.file('rows.ndjson','\n'.join(json.dumps({'i':i}) for i in range(MAX_ROWS+10)))
        data=preview(p);self.assertEqual(len(data['rows']),MAX_ROWS);self.assertTrue(data['limited'])
    def test_dbx_is_explicit_and_sqlite_header_wins(self):
        p=self.file('mail.dbx','not sqlite')
        with self.assertRaisesRegex(ValueError,'DBX is ambiguous'):preview(p)
        p.unlink();con=sqlite3.connect(p);con.execute('create table data (x)');con.close();self.assertEqual(preview(p)['datasets'],['data'])
    def test_excel_formulas_and_no_write(self):
        try:from openpyxl import Workbook
        except ImportError:self.skipTest('openpyxl unavailable')
        p=self.root/'book.xlsx';book=Workbook();book.active.append(['Name','Value']);book.active.append(['Ada','=1+2']);book.create_sheet('Second');book.save(p);book.close()
        before=hashlib.sha256(p.read_bytes()).hexdigest();data=preview(p)
        self.assertEqual(data['rows'][1],['Ada','=1+2']);self.assertEqual(data['columns'],['C1','C2']);self.assertEqual(preview(p,'Second')['selected'],'Second');self.assertEqual(before,hashlib.sha256(p.read_bytes()).hexdigest())
    def test_duplicate_row_differences_and_context(self):
        a={'path':'a','selected':'data','columns':['x'],'rows':[['1'],['1']]};b={**a,'rows':[['1']]}
        self.assertEqual(difference(a,b)['removed'],1);self.assertIsNone(difference(a,{**b,'path':'b'}));self.assertIsNone(difference(a,{**b,'selected':'other'}))
    def test_cell_and_output_bounds(self):
        data=table_result(['data'],'data',['x'],[['x'*2000],[None],[b'123']]);self.assertEqual(len(data['rows'][0][0]),512);self.assertEqual(data['rows'][1][0],'NULL');self.assertIn('binary',data['rows'][2][0])
    def test_worker_protocol_runs_in_selected_python(self):
        p=self.file('data.json','[{"ok": true}]');worker=Path(__file__).resolve().parents[1]/'data_reader.py'
        run=subprocess.run([sys.executable,str(worker)],input=json.dumps({'path':str(p)}),capture_output=True,text=True,timeout=10);self.assertEqual(run.returncode,0);self.assertTrue(json.loads(run.stdout)['ok'])
    def test_access_requires_driver_and_readonly_connection(self):
        import types
        p=self.file('data.accdb','placeholder');calls=[]
        class Cursor:
            description=[('id',)]
            def tables(self,**kw):return [types.SimpleNamespace(table_name='Data]1')]
            def execute(self,sql):calls.append(sql);return self
            def __iter__(self):return iter([(1,)])
        class Connection:
            def cursor(self):return Cursor()
            def close(self):calls.append('closed')
        def connect(text,**kwargs):
            self.assertTrue(kwargs['readonly']);self.assertIn('DBQ={',text);return Connection()
        module=types.SimpleNamespace(drivers=lambda:['Microsoft Access Driver (*.mdb, *.accdb)'],connect=connect)
        with patch.dict(sys.modules,pyodbc=module):self.assertEqual(preview(p)['rows'],[['1']])
        self.assertIn('[Data]]1]',calls[0]);self.assertEqual(calls[-1],'closed')
        module.drivers=lambda:[]
        with patch.dict(sys.modules,pyodbc=module):
            with self.assertRaisesRegex(ValueError,'PIP alone'):preview(p)
