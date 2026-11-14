import copy
from decimal import Decimal
import hashlib
import io
import json
from pathlib import Path
import sqlite3
import struct
import tempfile
import types
import unittest
from unittest.mock import Mock,patch
from project_templates import instantiate

class StarterBatchFiveTests(unittest.TestCase):
    def fixture(self,key):
        p=instantiate(key);ns={'messagebox':Mock(),'filedialog':Mock()};exec(p['imports'],ns)
        app=types.SimpleNamespace(Form1=Mock(),root=Mock(),archive_records=[],archive_selected=None,archive_visible=[],FilterEntry=Mock(),RecordList=Mock(),StatusLabel=Mock(),SummaryLabel=Mock(),PhotoPreview=Mock(),contact_photo=None)
        app.FilterEntry.get.return_value='';app.RecordList.curselection.return_value=(0,)
        for i,field in enumerate(ns['ARCHIVE_FIELDS']):setattr(app,'Field'+str(i),Mock())
        prefix=p['startup'].split('self.archive_selected')[0];exec(prefix,ns,{'self':app});return ns,app
    def test_expenses_decimal_totals_and_separate_currencies(self):
        ns,app=self.fixture('expenses');sample=app.archive_records[0]
        records=ns['archive_validate_records']([dict(sample,id='a',amount='0,10'),dict(sample,id='b',amount='0.20'),dict(sample,id='c',amount='1',direction='Income'),dict(sample,id='d',amount='2',currency='USD')])
        self.assertEqual(records[0]['amount'],'0.10');totals=ns['expense_totals'](records);self.assertEqual(totals,{'EUR':Decimal('0.70'),'USD':Decimal('-2.00'),'GBP':Decimal('0.00')})
    def test_expenses_reject_invalid_amount_dates_and_currency(self):
        ns,app=self.fixture('expenses');sample=app.archive_records[0]
        for record in [dict(sample,amount=x) for x in ('0','-1','NaN','1.234','1e9')]+[dict(sample,date='2026-02-30'),dict(sample,currency='ZZZ')]:
            with self.assertRaises(ValueError):ns['archive_validate_records']([record])
    def test_inventory_summary_and_threshold_boundary(self):
        ns,app=self.fixture('inventory');self.assertEqual(ns['inventory_summary'](app.archive_records),(5,Decimal('12.50'),0));record=dict(app.archive_records[0],quantity='2');self.assertIn('[LOW]',ns['archive_row_label'](record));self.assertEqual(ns['inventory_summary']([record])[2],1)
    def test_inventory_adjustment_and_negative_stock_preservation(self):
        ns,app=self.fixture('inventory');app.archive_selected=app.archive_records[0]['id'];ns['inventory_adjust'](app,1);self.assertEqual(app.archive_records[0]['quantity'],'6');ns['inventory_adjust'](app,-1);self.assertEqual(app.archive_records[0]['quantity'],'5')
        app.archive_records[0]['quantity']='0';before=copy.deepcopy(app.archive_records);ns['inventory_adjust'](app,-1);self.assertEqual(app.archive_records,before);ns['messagebox'].showerror.assert_called_once()
    def test_inventory_unique_codes_and_numeric_limits(self):
        ns,app=self.fixture('inventory');sample=app.archive_records[0]
        with self.assertRaises(ValueError):ns['archive_validate_records']([sample,dict(sample,id='second',sku=sample['sku'].lower())])
        for record in (dict(sample,quantity='1.5'),dict(sample,quantity='1000001'),dict(sample,cost='-2'),dict(sample,threshold='-1')):
            with self.assertRaises(ValueError):ns['archive_validate_records']([record])
    def test_media_year_and_borrower_validation(self):
        ns,app=self.fixture('media');sample=app.archive_records[0]
        for record in (dict(sample,year='20'),dict(sample,year='0000'),dict(sample,status='Loaned',borrower='')):
            with self.assertRaises(ValueError):ns['archive_validate_records']([record])
        self.assertEqual(ns['archive_validate_records']([dict(sample,status='Loaned',borrower='Ada')])[0]['borrower'],'Ada')
    def test_json_archives_roundtrip_and_failed_write(self):
        for key in ('expenses','inventory','media'):
            ns,app=self.fixture(key)
            with tempfile.TemporaryDirectory() as d:
                path=Path(d)/'data.json';path.write_text('original');ns['filedialog'].asksaveasfilename.return_value=str(path)
                with patch.object(ns['os'],'replace',side_effect=OSError('disk error')):ns['archive_save'](app)
                self.assertEqual(path.read_text(),'original');self.assertEqual(list(Path(d).iterdir()),[path]);ns['archive_save'](app)
                before=copy.deepcopy(app.archive_records);app.archive_records=[];ns['filedialog'].askopenfilename.return_value=str(path);ns['messagebox'].askyesno.return_value=True;ns['archive_open'](app);self.assertEqual(app.archive_records,before)
    def test_contact_database_roundtrip_and_parameterized_values(self):
        ns,app=self.fixture('contacts');app.archive_records[0].update(name="O'Connor caffè",notes='quotes "; DROP TABLE contacts; --')
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'contacts.sqlite';ns['filedialog'].asksaveasfilename.return_value=str(path);ns['archive_save'](app)
            con=sqlite3.connect(path);self.assertEqual(con.execute('SELECT name FROM contacts').fetchone()[0],"O'Connor caffè");con.close()
            before=copy.deepcopy(app.archive_records);app.archive_records=[];ns['filedialog'].askopenfilename.return_value=str(path);ns['messagebox'].askyesno.return_value=True;ns['archive_open'](app);self.assertEqual(app.archive_records,before)
            app.archive_records[0]['phone']='123';ns['archive_save'](app);con=sqlite3.connect(path);self.assertEqual(con.execute('SELECT phone FROM contacts').fetchone()[0],'123');con.close()
    def test_contact_save_rejects_unrelated_database(self):
        ns,app=self.fixture('contacts')
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'foreign.sqlite';con=sqlite3.connect(path);con.execute('CREATE TABLE important(value)');con.execute('INSERT INTO important VALUES(42)');con.commit();con.close();before=path.read_bytes();ns['filedialog'].asksaveasfilename.return_value=str(path);ns['archive_save'](app);self.assertEqual(path.read_bytes(),before)
            con=sqlite3.connect(path);self.assertEqual(con.execute('SELECT * FROM important').fetchall(),[(42,)]);con.close();ns['messagebox'].showerror.assert_called_once()
    def test_contact_schema_failure_does_not_replace_collection(self):
        ns,app=self.fixture('contacts')
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'wrong.sqlite';con=sqlite3.connect(path);con.execute('CREATE TABLE contacts(id)');con.close();ns['filedialog'].askopenfilename.return_value=str(path);before=app.archive_records;ns['archive_open'](app);self.assertIs(app.archive_records,before)
    def test_contact_transaction_failure_preserves_saved_data(self):
        ns,app=self.fixture('contacts')
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'contacts.sqlite';ns['filedialog'].asksaveasfilename.return_value=str(path);ns['archive_save'](app)
            con=sqlite3.connect(path);con.execute('CREATE TRIGGER blocked BEFORE DELETE ON contacts BEGIN SELECT RAISE(ABORT,"blocked"); END');con.commit();con.close()
            app.archive_records=[];ns['archive_save'](app);con=sqlite3.connect(path);self.assertEqual(con.execute('SELECT COUNT(*) FROM contacts').fetchone()[0],1);con.close();ns['messagebox'].showerror.assert_called_once()
            # A later insert failure must also roll back the preceding DELETE.
            con=sqlite3.connect(path);con.execute('DROP TRIGGER blocked');con.execute('ALTER TABLE contacts RENAME TO old_contacts');con.execute("CREATE TABLE contacts(id TEXT PRIMARY KEY, name TEXT NOT NULL, phone TEXT, email TEXT, photo TEXT, notes TEXT CHECK(notes != 'blocked'))");con.execute('INSERT INTO contacts SELECT * FROM old_contacts');con.execute('DROP TABLE old_contacts');con.commit();con.close()
            app.archive_records=[dict(id='replacement',name='Replacement',phone='',email='',photo='',notes='blocked')];ns['archive_save'](app)
            con=sqlite3.connect(path);self.assertEqual(con.execute('SELECT name FROM contacts').fetchall(),[('Example Contact',)]);con.close()
    def test_contact_email_validation_and_save_open_cancel(self):
        ns,app=self.fixture('contacts');sample=app.archive_records[0]
        with self.assertRaises(ValueError):ns['archive_validate_records']([dict(sample,email='invalid')])
        ns['filedialog'].asksaveasfilename.return_value='';ns['archive_save'](app);ns['filedialog'].askopenfilename.return_value='';before=app.archive_records;ns['archive_open'](app);self.assertIs(app.archive_records,before)
    def test_photo_png_header_bounds_and_reference_lifetime(self):
        ns,app=self.fixture('contacts')
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'photo.png';path.write_bytes(b'\x89PNG\r\n\x1a\n'+b'\0'*8+struct.pack('>II',320,240));app.Field3.get.return_value=str(path)
            photo=Mock();thumb=Mock();photo.subsample.return_value=thumb
            with patch.object(ns['tk'],'PhotoImage',return_value=photo):ns['contacts_preview'](app)
            photo.subsample.assert_called_once_with(2);self.assertIs(app.contact_photo,thumb);app.PhotoPreview.configure.assert_called_with(image=thumb,text='')
            path.write_bytes(b'\x89PNG\r\n\x1a\n'+b'\0'*8+struct.pack('>II',100000,100000))
            with patch.object(ns['tk'],'PhotoImage') as loader:ns['contacts_preview'](app);loader.assert_not_called()
            self.assertIsNone(app.contact_photo)
    def test_new_contact_clears_previous_photo(self):
        ns,app=self.fixture('contacts');app.contact_photo=object();ns['archive_clear'](app);self.assertIsNone(app.contact_photo);app.PhotoPreview.configure.assert_called_with(image='',text='No photo')
