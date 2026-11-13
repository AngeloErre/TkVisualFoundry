import json
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock
from tests.test_inspector import wait_snapshot
from watch_values import resolve_watch
from inspector_ui import InspectorMixin
ROOT=Path(__file__).resolve().parents[1]
class StackSelectionTests(unittest.TestCase):
    def test_real_frame_switch_updates_locals_watches_and_rejects_stale_token(self):
        with tempfile.TemporaryDirectory() as folder:
            d=Path(folder);p=d/'app.py';p.write_text("import helper\nglobal_marker='app'\ndef inner():\n    value=20\n    print(value)\nhelper.outer(inner)\n");(d/'helper.py').write_text("global_marker='helper'\ndef outer(callback):\n    value=10\n    callback()\n");out=d/'snapshot.json';config=d/'config.json';config.write_text(json.dumps({'output':str(out)}))
            proc=subprocess.Popen([sys.executable,'-u',str(ROOT/'inspector_runner.py'),'--config',str(config),'--debug',str(p)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            try:
                wait_snapshot(out,lambda x:x['state']=='paused');proc.stdin.write('break 5\ncontinue\n');proc.stdin.flush()
                data=wait_snapshot(out,lambda x:x['state']=='paused' and resolve_watch('locals.value',x)[0] and resolve_watch('locals.value',x)[0]['value']=='20')
                self.assertEqual(resolve_watch('globals.global_marker',data)[0]['value'],"'app'")
                outer=next(f for f in data['stack'] if f['function']=='outer');inner=next(f for f in data['stack'] if f['function']=='inner');token=data['pause_id']
                proc.stdin.write(f"vtsframe {token} {outer['index']}\n");proc.stdin.flush()
                selected=wait_snapshot(out,lambda x:x['selected_index']==outer['index'] and resolve_watch('locals.value',x)[0] and resolve_watch('locals.value',x)[0]['value']=='10')
                self.assertTrue(next(f for f in selected['stack'] if f['function']=='outer')['selected']);self.assertEqual(resolve_watch('globals.global_marker',selected)[0]['value'],"'helper'")
                proc.stdin.write(f"vtsframe {'0'*32} {inner['index']}\n");proc.stdin.flush()
                stale=wait_snapshot(out,lambda x:x['sequence']>selected['sequence']);self.assertEqual(stale['selected_index'],outer['index'])
                stdout,stderr=proc.communicate('quit\n',timeout=5);self.assertEqual(proc.returncode,0,stderr);self.assertIn('Stale or invalid frame request',stdout)
            finally:
                if proc.poll() is None:proc.kill();proc.communicate()
    def test_ui_rejects_running_and_wrong_project_context(self):
        process=Mock();process.poll.return_value=None
        ui=types.SimpleNamespace(inspector_tree=Mock(),inspector_data={'state':'paused','pause_id':'a'*32},inspector_stack_rows={'frame:0':{'index':3}},debug_paused=True,watch_session='old',history_session='new',debug_process=process,inspector_process=process,proc=process,inspector_status=Mock(),debug_cmd=Mock())
        ui.inspector_tree.selection.return_value=['frame:0'];InspectorMixin.select_inspector_frame(ui);ui.debug_cmd.assert_not_called()
        ui.watch_session='new';InspectorMixin.select_inspector_frame(ui);ui.debug_cmd.assert_called_once_with('vtsframe '+'a'*32+' 3')
