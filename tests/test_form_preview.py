import copy
import unittest
from core import new_project
from form_preview import preview_source
class PreviewTests(unittest.TestCase):
    def test_code_is_removed_and_original_preserved(self):
        p=new_project();p['imports']='raise RuntimeError("IMPORT_MARKER")';p['startup']='if INVALID_STARTUP'
        p['forms'][0]['events']={'Load':'raise RuntimeError("EVENT_MARKER")'}
        p['forms'][0]['widgets']=[dict(name='Button1',kind='Button',x=10,y=10,width=100,height=30,props={'text':'Hello','command':'exec SECRET_COMMAND','takefocus':'exec SECRET_FOCUS'},events={'Click':'INVALID_EVENT'})]
        original=copy.deepcopy(p);source,snapshot,placeholders=preview_source(p,0)
        self.assertEqual(p,original);self.assertEqual(placeholders,[])
        for marker in ('IMPORT_MARKER','INVALID_STARTUP','EVENT_MARKER','SECRET_COMMAND','SECRET_FOCUS','INVALID_EVENT'):self.assertNotIn(marker,source)
        compile(source,'preview','exec');self.assertIn("self.show('Form1')",source)
    def test_services_and_external_classes_are_placeholders(self):
        p=new_project();p['components']={'External':{'module':'never_import_this','class':'Widget'}}
        for i,kind in enumerate(('WebcamView','CloudStorage','LLMClient','MapView','External')):
            p['forms'][0]['widgets'].append(dict(name='Control'+str(i),kind=kind,x=0,y=i*30,width=100,height=30,props={},events={}))
        source,snapshot,placeholders=preview_source(p,0)
        self.assertEqual(len(placeholders),5);self.assertTrue(all(w['kind']=='Label' for w in snapshot['forms'][0]['widgets']))
        self.assertNotIn('never_import_this',source);self.assertNotIn('service_backends',source)
    def test_selected_form_only_and_tab_page(self):
        p=new_project();p['forms'].append(dict(name='Form2',title='Second',width=400,height=300,bg='white',events={},widgets=[dict(name='Tabs',kind='Notebook',x=0,y=0,width=300,height=200,props={'pages':['A','B']},events={})]))
        source,snapshot,_=preview_source(p,1,{'Tabs':'B'})
        self.assertEqual(len(snapshot['forms']),1);self.assertNotIn('self.Form1 =',source);self.assertIn("self.Tabs.pages['B']",source)
    def test_unrelated_project_dependencies_are_not_installed_for_preview(self):
        p=new_project();p['requirements']=['nonexistent-extra-library'];_,snapshot,_=preview_source(p,0)
        self.assertEqual(snapshot['requirements'],[])

class PreviewLifecycleTests(unittest.TestCase):
    def test_stop_owns_spawned_process_even_before_ui_poll(self):
        import threading
        import types
        from unittest.mock import Mock
        from preview_ui import PreviewMixin
        preview=Mock();preview.poll.return_value=None
        running_app=object()
        fake=types.SimpleNamespace(preview_serial=2,preview_cancel=threading.Event(),preview_starting=True,preview_lock=threading.Lock(),preview_spawned=preview,preview_process=None,proc=running_app)
        PreviewMixin.stop_preview(fake)
        self.assertTrue(fake.preview_cancel.is_set());self.assertFalse(fake.preview_starting)
        self.assertIsNone(fake.preview_spawned);self.assertEqual(fake.preview_serial,3)
        preview.terminate.assert_called_once();self.assertIs(fake.proc,running_app)
