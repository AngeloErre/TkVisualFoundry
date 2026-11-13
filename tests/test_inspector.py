import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from inspector_runtime import value_node,variable_nodes,instance_attributes

ROOT=Path(__file__).resolve().parents[1]

def wait_snapshot(path,predicate,timeout=8):
    end=time.monotonic()+timeout;last=None
    while time.monotonic()<end:
        try:
            last=json.loads(path.read_text())
            if predicate(last):return last
        except (OSError,ValueError):pass
        time.sleep(.03)
    raise AssertionError('Expected inspector state not received: '+str(last))

class InspectorTests(unittest.TestCase):
    def test_safe_summary_never_calls_user_hooks(self):
        class Hostile:
            def __repr__(self):raise AssertionError('repr called')
            @property
            def value(self):raise AssertionError('property called')
        self.assertEqual(value_node('obj',Hostile())['value'],'<Hostile object>')
        class Guarded:
            @property
            def __dict__(self):raise AssertionError('dict property called')
        self.assertEqual(instance_attributes(Guarded()),{})
        class DictSubclass(dict):
            def items(self):raise AssertionError('custom items called')
        self.assertEqual(variable_nodes(DictSubclass(public=3))[0]['value'],'3')
        class Meta(type):
            @property
            def __name__(cls):raise AssertionError('metaclass property called')
        class MetaObject(metaclass=Meta):pass
        self.assertEqual(value_node('obj',MetaObject())['type'],'MetaObject')
        node=value_node('data',{'values':[1,2],'obj':Hostile()});self.assertEqual(len(node['children']),2)
    def test_cycles_large_containers_and_private_names_are_bounded(self):
        cycle=[];cycle.append(cycle);self.assertIn('cycle',value_node('cycle',cycle)['children'][0]['value'])
        node=value_node('many',list(range(100000)));self.assertEqual(len(node['children']),30)
        nodes=variable_nodes({'__builtins__':1,'public':'x'*10000});self.assertEqual(len(nodes),1);self.assertLess(len(nodes[0]['value']),500)
        self.assertEqual(variable_nodes({'_private_counter':2})[0]['name'],'_private_counter')
    def launch(self,d,source,debug=False):
        target=d/'app.py';target.write_text(source);output=d/'snapshot.json';config=d/'config.json';config.write_text(json.dumps({'output':str(output)}))
        args=[sys.executable,'-u',str(ROOT/'inspector_runner.py'),'--config',str(config)]+(['--debug'] if debug else [])+[str(target)]
        return subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True),output
    def test_live_globals_attributes_and_last_callback_locals(self):
        with tempfile.TemporaryDirectory() as folder:
            d=Path(folder);proc,out=self.launch(d,'import time\nuser_total=7\nclass Application:\n    def update(self):\n        amount=42\n        self.counter=amount\napp=Application()\napp.update()\ntime.sleep(0.8)\napp.counter=99\nuser_total=11\ntime.sleep(1.2)\n')
            try:
                data=wait_snapshot(out,lambda d:any(g['scope']=='self' for g in d['groups']))
                attrs=next(g for g in data['groups'] if g['scope']=='self');self.assertEqual(next(v['value'] for v in attrs['values'] if v['name']=='counter'),'42')
                last=next(g for g in data['groups'] if g['scope']=='last locals');self.assertEqual(next(v['value'] for v in last['values'] if v['name']=='amount'),'42')
                globals_=next(g for g in data['groups'] if g['scope']=='globals');self.assertIn('user_total',[v['name'] for v in globals_['values']]);self.assertEqual(data['state'],'running')
                updated=wait_snapshot(out,lambda d:any(g['scope']=='self' and any(v['name']=='counter' and v['value']=='99' for v in g['values']) for g in d['groups']))
                self.assertGreater(updated['sequence'],data['sequence'])
                stdout,stderr=proc.communicate(timeout=6);self.assertEqual(proc.returncode,0,stderr);self.assertEqual(json.loads(out.read_text())['state'],'finished')
                if os.name=='posix':self.assertEqual(out.stat().st_mode&0o777,0o600)
            finally:
                if proc.poll() is None:proc.kill();proc.communicate()
    def test_real_debug_pause_locals_and_stack(self):
        with tempfile.TemporaryDirectory() as folder:
            proc,out=self.launch(Path(folder),'user_value=10\nuser_value+=5\n',debug=True)
            try:
                first=wait_snapshot(out,lambda d:d['state']=='paused');self.assertTrue(first['stack'])
                proc.stdin.write('next\n');proc.stdin.flush()
                second=wait_snapshot(out,lambda d:d['state']=='paused' and d['sequence']>first['sequence'] and any(any(v['name']=='user_value' for v in g['values']) for g in d['groups']))
                self.assertTrue(second['stack']);stdout,stderr=proc.communicate('quit\n',timeout=5);self.assertEqual(proc.returncode,0,stderr)
            finally:
                if proc.poll() is None:proc.kill();proc.communicate()

    def test_breakpoint_has_function_locals(self):
        with tempfile.TemporaryDirectory() as folder:
            proc,out=self.launch(Path(folder),'def callback():\n    local_amount=21\n    local_amount+=1\ncallback()\n',debug=True)
            try:
                wait_snapshot(out,lambda d:d['state']=='paused')
                proc.stdin.write('break 3\ncontinue\n');proc.stdin.flush()
                data=wait_snapshot(out,lambda d:d['state']=='paused' and any(g['scope']=='locals' and any(v['name']=='local_amount' and v['value']=='21' for v in g['values']) for g in d['groups']))
                self.assertEqual(data['stack'][0]['function'],'callback')
                stdout,stderr=proc.communicate('quit\n',timeout=5);self.assertEqual(proc.returncode,0,stderr)
            finally:
                if proc.poll() is None:proc.kill();proc.communicate()

    def test_finished_ui_ignores_old_process(self):
        import types
        from unittest.mock import Mock
        from inspector_ui import InspectorMixin
        process=object();ui=types.SimpleNamespace(inspector_process=process,inspector_file=Path('/tmp/snapshot'),inspector_last_poll=1,poll_inspector=Mock(),inspector_data={'state':'running'},render_inspector=Mock())
        InspectorMixin.inspector_finished(ui,object());ui.poll_inspector.assert_not_called()
        InspectorMixin.inspector_finished(ui,process);self.assertEqual(ui.inspector_data['state'],'finished');self.assertIsNone(ui.inspector_file);ui.render_inspector.assert_called_once()
