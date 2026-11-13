import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import Mock
from debug_view import DebugOutput
from debug_ui import DebugViewMixin

class DebugViewTests(unittest.TestCase):
    def test_fragmented_prompt_and_other_files(self):
        parser=DebugOutput('/tmp/application (demo).py')
        self.assertEqual(parser.feed('> /tmp/application (demo).py(42)event_Button1_Click()\n-> pass\n(Pd'),[])
        self.assertEqual(parser.feed('b) '),[(42,'event_Button1_Click()')])
        self.assertEqual(parser.feed("{'x': 1}\n(Pdb) "),[(42,'event_Button1_Click()')])
        self.assertEqual(parser.feed('> /tmp/external.py(5)helper()\n(Pdb) '),[None])
    def test_bounded_buffer_and_multiple_stops(self):
        parser=DebugOutput('/tmp/app.py');parser.feed('x'*100000);self.assertLessEqual(len(parser.buffer),65536)
        result=parser.feed('\n> /tmp/app.py(1)<module>()\n(Pdb) > /tmp/app.py(2)<module>()\n(Pdb) ')
        self.assertEqual([p[0] for p in result],[1,2])
    def test_real_pdb_subprocess_without_gui(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'application.py';path.write_text('value = 1\nvalue += 1\n')
            result=subprocess.run([sys.executable,'-u','-m','pdb',str(path)],input='next\nquit\n',text=True,capture_output=True,timeout=10)
            parser=DebugOutput(path);positions=[]
            for i in range(0,len(result.stdout),7):positions.extend(parser.feed(result.stdout[i:i+7]))
            self.assertEqual(result.returncode,0);self.assertEqual([p[0] for p in positions if p],[1,2])
    def test_observer_ignores_old_process_and_clears_finished_session(self):
        process=object();ui=types.SimpleNamespace(debug_process=process,debug_output=DebugOutput('/tmp/app.py'),debug_source='pass\n',debug_position=None,debug_location=Mock(),debug_jump=Mock(),paint_debug_position=Mock(),update_source=Mock())
        DebugViewMixin.observe_debug(ui,object(),'> /tmp/app.py(9)startup()\n(Pdb) ');self.assertIsNone(ui.debug_position)
        DebugViewMixin.observe_debug(ui,process,'> /tmp/app.py(9)startup()\n(Pdb) ');self.assertEqual(ui.debug_position,(9,'startup()'))
        DebugViewMixin.observe_debug(ui,object(),'',True);self.assertIsNotNone(ui.debug_source)
        DebugViewMixin.observe_debug(ui,process,'',True);self.assertIsNone(ui.debug_source);ui.update_source.assert_called_once()
    def test_resume_clears_marker_but_inspection_keeps_it(self):
        ui=types.SimpleNamespace(debug_position=(9,'startup()'),generated=Mock(),debug_jump=Mock(),debug_location=Mock())
        DebugViewMixin.debug_resuming(ui,'pp locals()');self.assertIsNotNone(ui.debug_position)
        DebugViewMixin.debug_resuming(ui,'next');self.assertIsNone(ui.debug_position);ui.generated.tag_remove.assert_called_once()
    def test_marker_requires_exact_session_source(self):
        ui=types.SimpleNamespace(debug_position=(3,'startup()'),debug_source='session\n',generated=Mock())
        ui.generated.get.return_value='changed\n';DebugViewMixin.paint_debug_position(ui);ui.generated.tag_add.assert_not_called()
        ui.generated.get.return_value='session\n';DebugViewMixin.paint_debug_position(ui);ui.generated.tag_add.assert_called_once_with('debug_current','3.0','3.end')
