import copy
from pathlib import Path
import tempfile
import threading
import unittest
from core import new_project
from project_search import search,digest,MAX_RESULTS

class ProjectSearchTests(unittest.TestCase):
    def test_all_project_scopes_and_unsaved_active_event(self):
        p=new_project();p['imports']='# needle';p['startup']='needle = 1';p['forms'][0]['events']={'Load':'print("needle")'}
        p['forms'][0]['widgets']=[dict(name='Button1',events={'Click':'saved'})]
        before=copy.deepcopy(p);override=(('event','Form1','Button1','Click'),'# new\nneedle = 2')
        result=search(p,'needle',override=override);self.assertEqual(len(result['rows']),4);self.assertEqual(p,before)
        row=result['rows'][-1];self.assertEqual((row['line'],row['column']),(2,0));self.assertEqual(row['key'],override[0]);self.assertIn('Button1',row['label'])
    def test_new_unsaved_event_not_yet_in_model(self):
        p=new_project();key=('event','Form1','Form1','Click');rows=search(p,'unfinished',override=(key,'unfinished('))['rows']
        self.assertEqual(len(rows),1);self.assertEqual(rows[0]['key'],key)
    def test_file_buffers_override_disk_and_removed_files(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'a.py').write_text('disk = 1');before=(root/'a.py').read_bytes()
            rows=search(new_project(),'unsaved',root,{'a.py':'unsaved = 2','removed.py':'unsaved = 3'})['rows']
            self.assertEqual([r['key'] for r in rows],[('file','a.py'),('file','removed.py')]);self.assertEqual((root/'a.py').read_bytes(),before);self.assertFalse((root/'removed.py').exists())
    def test_confinement_exclusions_and_bad_files(self):
        with tempfile.TemporaryDirectory() as d,tempfile.TemporaryDirectory() as outside:
            root=Path(d);(root/'a.py').write_text('needle');(root/'.venv').mkdir();(root/'.venv/x.py').write_text('needle');(root/'bad.py').write_bytes(b'\xff');(root/'link.py').symlink_to(Path(outside)/'x.py');(root/'text.txt').write_text('needle')
            result=search(new_project(),'needle',root,{'../escape.py':'needle'})
            self.assertEqual([r['key'] for r in result['rows']],[('file','a.py')]);self.assertTrue(result['warnings'])
    def test_literal_case_word_unicode_and_positions(self):
        p=new_project();p['imports']='caffè = "😀"\nValue value values\nx.y [a]'
        self.assertEqual(len(search(p,'value')['rows']),3)
        self.assertEqual(len(search(p,'value',whole_word=True)['rows']),2)
        self.assertEqual(len(search(p,'value',case_sensitive=True,whole_word=True)['rows']),1)
        self.assertEqual(search(p,'😀')['rows'][0]['column'],9)
        self.assertEqual(len(search(p,'[a]')['rows']),1);self.assertEqual(len(search(p,'x.y')['rows']),1)
    def test_limits_and_cancellation(self):
        p=new_project();p['imports']='needle '*1200;result=search(p,'needle');self.assertEqual(len(result['rows']),MAX_RESULTS);self.assertTrue(result['truncated'])
        stop=threading.Event();stop.set();self.assertTrue(search(p,'needle',stop=stop)['cancelled'])
        with self.assertRaises(ValueError):search(p,'')
    def test_source_identity_hash_changes_for_stale_results(self):
        p=new_project();p['imports']='needle';row=search(p,'needle')['rows'][0];self.assertEqual(row['digest'],digest('needle'));self.assertNotEqual(row['digest'],digest('# changed\nneedle'))
    def test_read_only_search_never_executes_python(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);marker=root/'executed';(root/'danger.py').write_text('raise AssertionError("needle")\nopen('+repr(str(marker))+',"w").write("bad")')
            self.assertEqual(len(search(new_project(),'needle',root)['rows']),1);self.assertFalse(marker.exists())

    def test_chunk_boundaries_do_not_drop_or_duplicate_matches(self):
        p=new_project();p['imports']='x'*4093+' needle '+'y'*4090+' needle'
        rows=search(p,'needle',whole_word=True)['rows'];self.assertEqual(len(rows),2)
        self.assertEqual(rows[0]['column'],4094)
        p['imports']='a'*10000
        self.assertEqual(len(search(p,'a'*1000)['rows']),10)

class SearchEditorIntegrationTests(unittest.TestCase):
    def test_snapshot_reads_live_buffers_without_commit_or_save(self):
        import types
        from unittest.mock import Mock
        from search_ui import GlobalSearch
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);p=new_project();obj=p['forms'][0];win=Mock();win.project_text.get.return_value='unsaved file needle'
            studio=types.SimpleNamespace(project=p,code_target=(obj,'Click',False),code=Mock(get=lambda *a:'unsaved event needle'),project_root=lambda:root,project_editors={root/'buffer.py':win},commit_code=Mock())
            project,override,folder,buffers=GlobalSearch.snapshot(types.SimpleNamespace(studio=studio))
            result=search(project,'needle',folder,buffers,override)
            self.assertEqual(len(result['rows']),2);studio.commit_code.assert_not_called();self.assertNotIn('Click',p['forms'][0]['events'])
    def test_navigation_opens_live_file_buffer_and_selects_match(self):
        import types
        from unittest.mock import Mock
        from search_ui import GlobalSearch
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);p=new_project();text='first\nneedle = 1';row=search(p,'needle',root,{'a.py':text})['rows'][0]
            editor=Mock(get=lambda *a:text);editor.tk.call.side_effect=lambda *a:len(a[-1]);studio=types.SimpleNamespace(project=p,project_root=lambda:root,open_project_file=Mock(return_value=editor))
            fake=types.SimpleNamespace(tree=Mock(selection=lambda:('0',)),owner=p,root_path=root,rows=[row],studio=studio,snapshot=lambda:(p,None,root,{'a.py':text}),status=Mock())
            GlobalSearch.navigate(fake);studio.open_project_file.assert_called_once_with(relative='a.py');editor.mark_set.assert_called_once_with('insert','2.0');editor.tag_add.assert_called_once_with('sel','2.0','2.6')
    def test_navigation_rejects_changed_source_or_different_project(self):
        import types
        from unittest.mock import Mock
        from search_ui import GlobalSearch
        p=new_project();p['imports']='needle';row=search(p,'needle')['rows'][0];changed=copy.deepcopy(p);changed['imports']='# changed\nneedle'
        studio=types.SimpleNamespace(project=p,project_root=lambda:None,global_code=Mock())
        fake=types.SimpleNamespace(tree=Mock(selection=lambda:('0',)),owner=p,root_path=None,rows=[row],studio=studio,snapshot=lambda:(changed,None,None,{}),status=Mock(),run=Mock())
        GlobalSearch.navigate(fake);studio.global_code.assert_not_called();fake.status.set.assert_called_once()
        studio.project=new_project();GlobalSearch.navigate(fake);fake.run.assert_called_once()
    def test_navigation_rechecks_actual_opened_editor(self):
        import types
        from unittest.mock import Mock
        from search_ui import GlobalSearch
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);p=new_project();row=search(p,'needle',root,{'a.py':'needle'})['rows'][0]
            editor=Mock(get=lambda *a:'changed after read');studio=types.SimpleNamespace(project=p,project_root=lambda:root,open_project_file=Mock(return_value=editor))
            fake=types.SimpleNamespace(tree=Mock(selection=lambda:('0',)),owner=p,root_path=root,rows=[row],studio=studio,snapshot=lambda:(p,None,root,{'a.py':'needle'}),status=Mock())
            GlobalSearch.navigate(fake);editor.mark_set.assert_not_called();fake.status.set.assert_called_once()

    def test_text_indices_follow_tcl_character_units(self):
        import tkinter,types
        from search_ui import source_index
        text='😀 needle'
        native=types.SimpleNamespace(tk=tkinter.Tcl())
        self.assertEqual(source_index(native,text,1,2),'1.'+str(native.tk.call('string','length','😀 ')))
        legacy=types.SimpleNamespace(tk=types.SimpleNamespace(call=lambda *args:len(args[-1].encode('utf-16-le'))//2))
        self.assertEqual(source_index(legacy,text,1,2),'1.3')
