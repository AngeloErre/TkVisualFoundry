import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from watch_values import parse_watch,resolve_watch,rename_watch
from inspector_runtime import variable_nodes
from core import new_project,validate,generate,load
from rename_refactor import rename_project
from tests.test_inspector import wait_snapshot

ROOT=Path(__file__).resolve().parents[1]
class WatchTests(unittest.TestCase):
    def snapshot(self):
        return {'state':'running','groups':[{'scope':'locals','name':'callback','values':variable_nodes({'count':2,'config':{'port':8000}})},{'scope':'globals','name':'app.py','values':variable_nodes({'count':1})},{'scope':'self','name':'Application','values':variable_nodes({'counter':3,'samples':[10,20]})}]}
    def test_paths_resolve_containers_and_explicit_scopes(self):
        snapshot=self.snapshot()
        for path,value in [('self.counter','3'),('self.samples[1]','20'),("config['port']",'8000'),('count','2'),('globals.count','1')]:
            node,origin=resolve_watch(path,snapshot);self.assertEqual(node['value'],value);self.assertTrue(origin)
        snapshot['groups'].append({'scope':'last locals','name':'old','values':variable_nodes({'old_value':42})})
        self.assertEqual(resolve_watch('last.old_value',snapshot)[0]['value'],'42')
    def test_unsafe_or_unsupported_expressions_are_rejected(self):
        for path in ['self.method()','__import__("os").system("bad")','count + 1','[x for x in data]','data[-1]','data[1:3]','data[True]','x'*257]:
            with self.subTest(path=path),self.assertRaises(ValueError):parse_watch(path)
    def test_missing_or_truncated_values_do_not_fabricate_results(self):
        data=self.snapshot();data['groups'][2]['values']=variable_nodes({'samples':list(range(100))})
        self.assertIsNone(resolve_watch('self.samples[99]',data)[0]);self.assertIsNone(resolve_watch('unknown',data)[0]);self.assertIsNone(resolve_watch('count',None)[0])
    def test_project_validation_rename_and_round_trip(self):
        p=new_project();p['watches']=['self.Form1',"config['Form1']"]
        renamed=rename_project(p,'Form1','MainForm')['project'];self.assertEqual(renamed['watches'],['self.MainForm',"config['Form1']"])
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'demo.vtk.json';path.write_text(json.dumps(renamed));self.assertEqual(load(path)['watches'],renamed['watches'])
        self.assertNotIn('resolve_watch',generate(p))
        for bad in [None,{},['count','count'],['f()'],['x'+str(i) for i in range(101)]]:
            p['watches']=bad
            with self.assertRaises(ValueError):validate(p)
    def test_rename_only_changes_self_component_references(self):
        self.assertEqual(rename_watch("self.Button1['key']",{'Button1':'Go'}),"self.Go['key']")
        self.assertEqual(rename_watch("config['Button1']",{'Button1':'Go'}),"config['Button1']")
        self.assertEqual(rename_watch('Button1',{'Button1':'Go'}),'Button1')
    def test_live_sampled_watch_changes_with_real_runner(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d);target=folder/'app.py';target.write_text('import time\nuser_counter=3\ntime.sleep(0.8)\nuser_counter=4\ntime.sleep(0.9)\n');output=folder/'snapshot.json';config=folder/'config.json';config.write_text(json.dumps({'output':str(output)}))
            proc=subprocess.Popen([sys.executable,'-u',str(ROOT/'inspector_runner.py'),'--config',str(config),str(target)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            try:
                def has_value(data,value):
                    node,_=resolve_watch('globals.user_counter',data);return node and node['value']==value
                first=wait_snapshot(output,lambda data:has_value(data,'3'));second=wait_snapshot(output,lambda data:has_value(data,'4'))
                self.assertGreater(second['sequence'],first['sequence']);_,stderr=proc.communicate(timeout=5);self.assertEqual(proc.returncode,0,stderr)
            finally:
                if proc.poll() is None:proc.kill();proc.communicate()

    def test_opening_another_project_resets_snapshot_ownership(self):
        import types
        from unittest.mock import Mock,patch
        from studio import Studio
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'other.vtk.json';path.write_text(json.dumps(new_project()))
            ui=types.SimpleNamespace(dirty_guard=lambda:True,history_session='previous-session',history_last_queued='old-snapshot',code=Mock(),refresh=Mock())
            with patch('studio.filedialog.askopenfilename',return_value=str(path)):Studio.open_project(ui)
            self.assertNotEqual(ui.history_session,'previous-session');self.assertIsNone(ui.history_last_queued);ui.refresh.assert_called_once()
