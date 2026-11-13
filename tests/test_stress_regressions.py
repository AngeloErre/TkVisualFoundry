import copy
import json
from pathlib import Path
import tempfile
import unittest
from core import new_project,validate,identifier,generate
from data_reader import preview,difference

class StressRegressionTests(unittest.TestCase):
    def test_python_normalized_identifiers_cannot_shadow_root(self):
        for name in ('𝚛𝚘𝚘𝚝','K','ｅｖｅｎｔ_Button_Click','e\u0301'):
            self.assertFalse(identifier(name),name)
        for name in ('Bottone','caffè','Δεδομένα'):self.assertTrue(identifier(name))
        p=new_project();p['forms'][0]['widgets']=[dict(name='𝚛𝚘𝚘𝚝',kind='Button',x=0,y=0,width=80,height=25,props={},events={})]
        with self.assertRaises(ValueError):generate(p)
    def test_malformed_code_rejected_before_loading_into_editor(self):
        for bad in (None,1,False,[],{'text':'pass'}):
            for key in ('startup','imports'):
                p=new_project();p[key]=bad
                with self.subTest(key=key,bad=bad),self.assertRaises(ValueError):validate(p,code=False)
            p=new_project();p['forms'][0]['events']={'Click':bad}
            with self.subTest(event=bad),self.assertRaises(ValueError):validate(p,code=False)
    def test_invalid_shapes_fail_without_replacing_project(self):
        for malformed in (None,[],{'version':1,'forms':'bad'}):
            with self.assertRaises(ValueError):validate(malformed,code=False)
        for field,bad in [('widgets',{}),('events',[]),('title',None),('bg',3),('props',[])]:
            p=new_project();p['forms'][0][field]=bad
            with self.subTest(field=field),self.assertRaises(ValueError):validate(p,code=False)
    def test_data_comparison_preserves_type_information(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'data.json'
            for left,right in [(None,'NULL'),(1,'1'),(True,'True'),(1,1.0)]:
                p.write_text(json.dumps([{'x':left}]));before=preview(p)
                p.write_text(json.dumps([{'x':right}]));after=preview(p)
                delta=difference(before,after);self.assertEqual((delta['added'],delta['removed']),(1,1),(left,right))
                self.assertEqual(difference(after,preview(p))['added'],0)
    def test_preview_keys_stay_bounded_and_count_duplicates(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'data.json';p.write_text(json.dumps([{'x':1}]*600));before=preview(p)
            self.assertEqual(len(before['row_keys']),500);self.assertTrue(all(len(k)==64 for k in before['row_keys']))
            p.write_text(json.dumps([{'x':1}]*499));delta=difference(before,preview(p));self.assertEqual(delta['removed'],1)

class ReaderLifecycleTests(unittest.TestCase):
    def test_exit_race_is_harmless(self):
        from unittest.mock import Mock
        from data_viewer_ui import stop_reader
        process=Mock();process.poll.return_value=None;process.kill.side_effect=ProcessLookupError('already gone')
        stop_reader(process);process.kill.assert_called_once();stop_reader(None)
    def test_close_reaps_real_worker_and_is_idempotent(self):
        import subprocess,sys,threading,types
        from unittest.mock import Mock
        from data_viewer_ui import DataViewer
        process=subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)'])
        fake=types.SimpleNamespace(process=process,process_lock=threading.Lock(),closed=False,sequence=1,after_id='poll',auto_id='auto',after_cancel=Mock(),destroy=Mock())
        try:
            DataViewer.close(fake);process.wait(timeout=3);DataViewer.close(fake)
            self.assertIsNone(fake.process);self.assertTrue(fake.closed);fake.destroy.assert_called_once();self.assertEqual(fake.after_cancel.call_count,2)
        finally:
            if process.poll() is None:process.kill()
            process.wait(timeout=3)
    def test_close_during_worker_creation_does_not_orphan_child(self):
        import subprocess,sys,threading,types,queue
        from unittest.mock import Mock,patch
        from data_viewer_ui import DataViewer
        entered=threading.Event();release=threading.Event();children=[];original=subprocess.Popen
        def delayed(*args,**kwargs):
            entered.set()
            if not release.wait(3):raise RuntimeError('test synchronization timed out')
            process=original(*args,**kwargs);children.append(process);return process
        fake=types.SimpleNamespace(closed=False,busy=False,path='/unused',sequence=0,process=None,process_lock=threading.Lock(),selector=Mock(),status=Mock(),dataset=Mock(get=lambda:''),studio=types.SimpleNamespace(config_data={'python':sys.executable}),events=queue.Queue(),after_id=None,auto_id=None,after_cancel=Mock(),destroy=Mock())
        with patch('data_viewer_ui.subprocess.Popen',side_effect=delayed):
            DataViewer.refresh(fake)
            try:
                self.assertTrue(entered.wait(3));DataViewer.close(fake);release.set();fake.events.get(timeout=5)
                self.assertEqual(len(children),1);self.assertIsNotNone(children[0].poll());self.assertIsNone(fake.process)
            finally:
                release.set()
                for process in children:
                    if process.poll() is None:process.kill()
                    process.wait(timeout=3)

class BinaryComparisonTests(unittest.TestCase):
    def test_changed_blob_with_same_length_is_detected(self):
        import sqlite3
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'data.sqlite';con=sqlite3.connect(p);con.execute('CREATE TABLE data(value BLOB)');con.execute('INSERT INTO data VALUES (?)',(b'abc',));con.commit();before=preview(p)
            con.execute('UPDATE data SET value=?',(b'xyz',));con.commit();after=preview(p);con.close()
            self.assertEqual(before['rows'],after['rows'])
            self.assertEqual(difference(before,after)['added'],1);self.assertEqual(difference(before,after)['removed'],1)
