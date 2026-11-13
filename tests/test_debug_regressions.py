import copy
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import Mock,patch
from settings_store import normalized_settings,load_settings
from core import new_project

class SettingsRecoveryTests(unittest.TestCase):
    def setUp(self):self.defaults={'grid':10,'font_size':13,'python':'/python','language':'it'}
    def test_malformed_shapes_and_limits(self):
        for bad in (None,42,[],{'grid':'bad','font_size':999,'appearance':[]},{'grid':True,'font_size':False,'python':[]}):
            result=normalized_settings(bad,self.defaults)
            self.assertEqual(result['grid'],10);self.assertEqual(result['font_size'],13);self.assertEqual(result['python'],'/python')
    def test_invalid_colors_are_discarded_without_losing_valid_preferences(self):
        def valid(color):
            if color=='not-a-color':raise ValueError('bad')
        result=normalized_settings({'grid':'20','appearance':{'background':'#123456','accent':'not-a-color','surface':[]},'startup_checks':'false'},self.defaults,valid)
        self.assertEqual(result['grid'],20);self.assertEqual(result['appearance'],{'background':'#123456'});self.assertTrue(result['startup_checks'])
    def test_unreadable_or_invalid_json_recovers(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'settings.json'
            for contents in (b'{bad',b'42',b'\xff\xfe'):
                p.write_bytes(contents);self.assertEqual(load_settings(p,self.defaults)['font_size'],13)

class EditorContextTests(unittest.TestCase):
    def test_context_switch_resets_native_undo(self):
        from studio import Studio
        obj={'name':'Button1','events':{'Click':'print(1)'}}
        fake=types.SimpleNamespace(commit_code=Mock(),selected=obj,form={},evvar=Mock(get=lambda:'Click'),code=Mock(),code_object_var=Mock(),code_label=Mock(),tabs=Mock(),highlight=Mock(),update_assistant=Mock())
        Studio.edit_event(fake)
        fake.code.edit_reset.assert_called_once();self.assertEqual(fake.code_target,(obj,'Click',False))
    def test_worker_exit_race_does_not_break_editor_shutdown(self):
        from analysis_client import AnalysisClient
        import threading
        process=Mock();process.poll.return_value=None;process.terminate.side_effect=ProcessLookupError('already exited')
        fake=types.SimpleNamespace(process=process,process_lock=threading.Lock())
        AnalysisClient.stop_process(fake);self.assertIsNone(fake.process)

    def test_history_restore_clears_buffer_target(self):
        from assist_ui import AssistMixin
        fake=types.SimpleNamespace(code_target=({},'Click',False),dismiss_completion=Mock(),code=Mock(),code_label=Mock(),code_object_var=Mock(),update_assistant=Mock())
        AssistMixin.reset_code_context(fake)
        self.assertIsNone(fake.code_target);fake.code.delete.assert_called_once_with('1.0','end');fake.code.edit_reset.assert_called_once()
        self.assertEqual(fake.code.configure.call_args.kwargs,{'state':'disabled'})

class BackgroundCheckTests(unittest.TestCase):
    def test_cancelled_audit_does_not_start_processes_or_network(self):
        from startup_checks import audit
        import threading
        stop=threading.Event();stop.set()
        with patch('startup_checks.installed') as probe:
            self.assertTrue(audit('/python',[],[],stop)['cancelled']);probe.assert_not_called()
    def test_cancellation_skips_queued_checks_and_pip(self):
        from startup_checks import audit
        import threading
        stop=threading.Event()
        def first(*args):stop.set();return {}
        inventory={'python':'3.15.2','packages':{'package'+str(i):'1.0' for i in range(40)}}
        with patch('startup_checks.installed',return_value=inventory),patch('startup_checks.package_check',side_effect=first) as packages,patch('startup_checks.check_link') as links,patch('startup_checks.subprocess.run') as processes:
            self.assertTrue(audit('/python',[],['https://example.org'],stop)['cancelled'])
            self.assertLessEqual(packages.call_count,6);links.assert_not_called();processes.assert_not_called()

    def test_code_edits_do_not_invalidate_dependency_report(self):
        from intelligence_ui import IntelligenceMixin
        fake=types.SimpleNamespace(config_data={'python':'/python'},project=new_project())
        before=IntelligenceMixin.health_signature(fake);fake.project['startup']='print("changed")'
        self.assertEqual(before,IntelligenceMixin.health_signature(fake))
        fake.project['requirements']=['numpy']
        self.assertNotEqual(before,IntelligenceMixin.health_signature(fake))

class ProjectRecoveryTests(unittest.TestCase):
    def test_invalid_geometry_rejected_before_rendering(self):
        from core import validate
        for value in ('640',False,2.5):
            p=new_project();p['forms'][0]['width']=value
            with self.assertRaises(ValueError):validate(p,code=False)
        p=new_project();p['forms'][0]['widgets']=[dict(name='Label1',kind='Label',x='10',y=0,width=80,height=25,props={},events={})]
        with self.assertRaises(ValueError):validate(p,code=False)

    def test_failed_atomic_save_preserves_original(self):
        from project_files import atomic_write_text
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'project.json';path.write_text('original')
            with patch('os.replace',side_effect=OSError('disk error')):
                with self.assertRaises(OSError):atomic_write_text(path,'new')
            self.assertEqual(path.read_text(),'original');self.assertEqual(list(Path(d).iterdir()),[path])
            atomic_write_text(path,'updated');self.assertEqual(path.read_text(),'updated')
    def test_named_editor_color_uses_tk_rgb(self):
        from ux_theme import editor_palette
        self.assertEqual(editor_palette('white',(65535,65535,65535)),editor_palette('#ffffff'))
