import copy
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import Mock,patch
from project_templates import instantiate

class StarterBatchFourTests(unittest.TestCase):
    def ns(self,key):
        ns={'messagebox':Mock(),'filedialog':Mock()};exec(instantiate(key)['imports'],ns);return ns
    def samples(self,key):
        p=instantiate(key);ns=self.ns(key);app=types.SimpleNamespace(Form1=Mock(),root=Mock(),archive_records=[],archive_selected=None,archive_visible=[],FilterEntry=Mock(get=Mock(return_value='')),RecordList=Mock(),StatusLabel=Mock())
        for i,field in enumerate(ns['ARCHIVE_FIELDS']):setattr(app,'Field'+str(i),Mock())
        # The startup sample is trusted project source, not imported user data.
        prefix=p['startup'].split('self.archive_selected')[0];exec(prefix,ns,{'self':app})
        return ns,app
    def fill(self,ns,app,record):
        for i,(key,*_) in enumerate(ns['ARCHIVE_FIELDS']):getattr(app,'Field'+str(i)).get.return_value=record[key]
    def test_calculator_precedence_functions_and_radians(self):
        calculate=self.ns('calculator')['calc_expression']
        self.assertEqual(calculate('2 + 3 * 4'),14);self.assertEqual(calculate('sqrt(81) + sin(pi/2)'),10);self.assertEqual(calculate('log(8,2)'),3);self.assertEqual(calculate('factorial(5)'),120);self.assertEqual(calculate('-2**2'),-4)
    def test_calculator_rejects_code_and_unbounded_inputs(self):
        calculate=self.ns('calculator')['calc_expression']
        for expression in ('__import__("os").getcwd()','(1).__class__','[x for x in (1,2)]','True','2**1000000','factorial(500)','1e999','sin(x=2)','"hello"','a'*257):
            with self.subTest(expression=expression),self.assertRaises((ValueError,SyntaxError,TypeError,OverflowError)):calculate(expression)
        with self.assertRaises(ZeroDivisionError):calculate('1/0')
    def test_calculator_errors_do_not_grow_history(self):
        ns=self.ns('calculator');app=types.SimpleNamespace(ExpressionEntry=Mock(get=Mock(return_value='1+2')),ResultLabel=Mock(),HistoryList=Mock(),calc_history=[])
        for _ in range(105):ns['calc_calculate'](app)
        self.assertEqual(len(app.calc_history),100);self.assertEqual(app.calc_history[0],('1+2','3'));app.ExpressionEntry.get.return_value='1/0';ns['calc_calculate'](app);self.assertEqual(len(app.calc_history),100);self.assertIn('Error:',app.ResultLabel.configure.call_args.kwargs['text'])
    def test_all_archive_samples_validate_and_roundtrip_shape(self):
        for key in ('books','recipes','timetable'):
            ns,app=self.samples(key);self.assertEqual(len(app.archive_records),1);self.assertEqual(ns['archive_validate_records'](copy.deepcopy(app.archive_records)),app.archive_records)
    def test_archive_add_update_delete_and_filter_identity(self):
        ns,app=self.samples('books');record=app.archive_records[0].copy();record.update(title='New title',author='Ada');self.fill(ns,app,record);ns['archive_store'](app);self.assertEqual(len(app.archive_records),2);identity=app.archive_selected
        record['title']='Updated';self.fill(ns,app,record);ns['archive_store'](app,True);self.assertEqual(len(app.archive_records),2);self.assertEqual(next(r for r in app.archive_records if r['id']==identity)['title'],'Updated')
        app.FilterEntry.get.return_value='no matching record';ns['archive_render'](app);self.assertEqual(app.archive_visible,[]);self.assertIsNone(app.archive_selected)
        app.archive_selected=identity;ns['messagebox'].askyesno.return_value=False;ns['archive_delete'](app);self.assertEqual(len(app.archive_records),2)
        ns['messagebox'].askyesno.return_value=True;ns['archive_delete'](app);self.assertEqual(len(app.archive_records),1)
    def test_invalid_update_preserves_record_collection(self):
        ns,app=self.samples('books');app.archive_selected=app.archive_records[0]['id'];record=app.archive_records[0].copy();record['rating']='9';self.fill(ns,app,record);before=copy.deepcopy(app.archive_records);ns['archive_store'](app,True);self.assertEqual(app.archive_records,before)
    def test_duplicate_ids_and_bad_field_types_are_rejected(self):
        ns,app=self.samples('books');sample=app.archive_records[0]
        for records in ([sample,sample], [dict(sample,title=None)], [dict(sample,status='Unknown')], [dict(sample,id=[])], [dict(sample,title='')]):
            with self.assertRaises(ValueError):ns['archive_validate_records'](records)
    def test_recipes_reject_invalid_times_and_empty_ingredients(self):
        ns,app=self.samples('recipes');sample=app.archive_records[0]
        for value in ('-1','1441','2.5','bad'):
            with self.assertRaises(ValueError):ns['archive_validate_records']([dict(sample,minutes=value)])
        with self.assertRaises(ValueError):ns['archive_validate_records']([dict(sample,ingredients=' ')])
        self.assertEqual(ns['archive_validate_records']([dict(sample,minutes='1440')])[0]['minutes'],'1440')
    def test_timetable_adjacent_periods_allowed_overlaps_rejected(self):
        ns,app=self.samples('timetable');first=app.archive_records[0];second=dict(first,id='second',start='10:00',end='11:00');self.assertEqual(len(ns['archive_validate_records']([first,second])),2)
        with self.assertRaisesRegex(ValueError,'overlap'):ns['archive_validate_records']([first,dict(second,start='09:30')])
        self.assertEqual(len(ns['archive_validate_records']([first,dict(second,day='Tuesday',start='09:00')])),2)
    def test_timetable_invalid_times_and_sorting(self):
        ns,app=self.samples('timetable');sample=app.archive_records[0]
        for value in ('9:00','24:00','09:99','bad'):
            with self.assertRaises(ValueError):ns['archive_validate_records']([dict(sample,start=value)])
        with self.assertRaises(ValueError):ns['archive_validate_records']([dict(sample,end='08:00')])
        earlier=dict(sample,id='earlier',start='07:00',end='08:00');rows=ns['archive_validate_records']([sample,earlier]);self.assertEqual(rows[0]['id'],'earlier')
    def test_all_archives_atomic_save_open_and_type_guard(self):
        for key in ('books','recipes','timetable'):
            ns,app=self.samples(key)
            with tempfile.TemporaryDirectory() as d:
                path=Path(d)/'archive.json';path.write_text('original');ns['filedialog'].asksaveasfilename.return_value=str(path)
                with patch.object(ns['os'],'replace',side_effect=OSError('disk error')):ns['archive_save'](app)
                self.assertEqual(path.read_text(),'original');self.assertEqual(list(Path(d).iterdir()),[path]);ns['archive_save'](app);data=json.loads(path.read_text());self.assertEqual(data['kind'],ns['ARCHIVE_KIND'])
                ns['filedialog'].askopenfilename.return_value=str(path);ns['messagebox'].askyesno.return_value=True;app.archive_records=[];ns['archive_open'](app);self.assertEqual(len(app.archive_records),1)
                data['kind']='wrong archive';path.write_text(json.dumps(data));before=app.archive_records;ns['archive_open'](app);self.assertIs(app.archive_records,before)
    def test_recipe_save_size_limit_keeps_existing_file(self):
        ns,app=self.samples('recipes');sample=app.archive_records[0];app.archive_records=[dict(sample,id=str(i),ingredients='x'*10000,steps='y'*10000) for i in range(110)]
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'recipes.json';path.write_text('original');ns['filedialog'].asksaveasfilename.return_value=str(path);ns['archive_save'](app);self.assertEqual(path.read_text(),'original');self.assertEqual(list(Path(d).iterdir()),[path]);ns['messagebox'].showerror.assert_called_once()
    def test_archive_save_open_and_close_cancellations(self):
        ns,app=self.samples('books');ns['filedialog'].asksaveasfilename.return_value='';ns['archive_save'](app);ns['filedialog'].askopenfilename.return_value='';before=app.archive_records;ns['archive_open'](app);self.assertIs(app.archive_records,before)
        ns['messagebox'].askyesno.return_value=False;ns['archive_close'](app);app.root.destroy.assert_not_called()
