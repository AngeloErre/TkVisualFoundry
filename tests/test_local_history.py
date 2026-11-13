import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from core import new_project
from local_history import HistoryStore,captured_project,recovered_path,compare_projects
class HistoryTests(unittest.TestCase):
    def test_pending_editor_text_is_copied_without_mutating_project(self):
        p=new_project();p['forms'][0]['events']={'Load':'pass'};original=copy.deepcopy(p)
        result=captured_project(p,('Form1','Load',False),'if INCOMPLETE:')
        self.assertEqual(p,original);self.assertEqual(result['forms'][0]['events']['Load'],'if INCOMPLETE:')
        result=captured_project(p,('Application','imports',True),'import pending')
        self.assertEqual(result['imports'],'import pending')
    def test_dedup_retention_and_recoverable_invalid_syntax(self):
        with tempfile.TemporaryDirectory() as folder:
            store=HistoryStore(folder,keep=2);p=new_project();p['startup']='if ('
            first=store.save(p,None,'session');self.assertEqual(first,store.save(p,None,'session'))
            p['name']='Second';store.save(p,None,'session');p['name']='Third';last=store.save(p,None,'session')
            self.assertEqual(len(store.index()),2);self.assertEqual(store.read(last)['project']['startup'],'if (')
    def test_recovery_path_never_overwrites_original_or_existing_copy(self):
        with tempfile.TemporaryDirectory() as folder:
            original=Path(folder)/'Demo.vtk.json';original.write_text('original')
            target=recovered_path(original);self.assertNotEqual(target,original);target.write_text('existing')
            self.assertNotEqual(recovered_path(original),target);self.assertEqual(original.read_text(),'original')
    def test_failed_write_preserves_old_snapshot(self):
        with tempfile.TemporaryDirectory() as folder:
            store=HistoryStore(folder);p=new_project();first=store.save(p,None,'session');p['name']='Changed'
            with patch('local_history.atomic_write_text',side_effect=OSError('disk failure')):
                with self.assertRaises(OSError):store.save(p,None,'session')
            self.assertEqual(len(store.index()),1);self.assertTrue(first.exists())
    def test_corrupt_records_are_skipped_and_external_reads_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            store=HistoryStore(folder);first=store.save(new_project(),None,'session')
            first.write_text('[]');self.assertEqual(store.index(),[])
            with self.assertRaises(ValueError):store.read(Path(folder).parent/'outside.json')
    def test_comparison_is_bounded_and_does_not_change_snapshots(self):
        current=new_project();previous=copy.deepcopy(current);previous['startup']='print("previous")'
        text,truncated=compare_projects(current,previous);self.assertIn('previous',text);self.assertFalse(truncated)
        self.assertTrue(compare_projects(current,previous,limit=5)[1])
    def test_restore_rechecks_target_after_saving_current_work(self):
        import types
        from unittest.mock import Mock
        from history_ui import HistoryMixin
        with tempfile.TemporaryDirectory() as folder:
            original=Path(folder)/'Demo.vtk.json';original.write_text('{}');candidate=recovered_path(original)
            def guard():candidate.write_text('saved current work');return True
            fake=types.SimpleNamespace(dirty_guard=guard,refresh=Mock(),history_window=Mock())
            HistoryMixin.restore_local_snapshot(fake,{'project_path':str(original),'project':new_project()})
            self.assertNotEqual(fake.path,candidate);self.assertEqual(candidate.read_text(),'saved current work');self.assertTrue(fake.recovery_unsaved)
