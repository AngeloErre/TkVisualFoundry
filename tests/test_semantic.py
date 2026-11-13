import importlib.util
from pathlib import Path
import queue
import shutil
import subprocess
import sys
import tempfile
import time
import types
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core import new_project
from i18n import tr
from semantic_engine import SemanticEngine,local_analysis,in_literal,editor_source
from analysis_client import AnalysisClient


def request(body,project=None,**extra):
    return {'body':body,'cursor':f'{body.count(chr(10))+1}.{len(body.split(chr(10))[-1])}','project':project or new_project(),'cwd':str(Path(__file__).resolve().parents[1]),**extra}


class LocalCompletionTests(unittest.TestCase):
    def test_messagebox_public_members_are_available_without_jedi(self):
        result=local_analysis('messagebox.',new_project())
        names={item['name'] for item in result['items']}
        self.assertTrue({'showinfo','showwarning','showerror','askyesno','askokcancel','askretrycancel'}.issubset(names))
        self.assertFalse(any(name.startswith('_') for name in names))
        self.assertTrue(all(item['prefix_len']==0 for item in result['items']))
    def test_method_prefix_and_signature(self):
        result=local_analysis('messagebox.sh',new_project())
        self.assertEqual({item['name'] for item in result['items']},{'showinfo','showwarning','showerror'})
        self.assertTrue(all(item['prefix_len']==2 for item in result['items']))
        tip=local_analysis('messagebox.showinfo(',new_project())['calltip']
        self.assertIn('title',tip);self.assertIn('message',tip)
    def test_no_suggestions_inside_comments_or_unfinished_strings(self):
        for body in ['# messagebox.', 'value = "messagebox.', "x = '''messagebox."]:
            self.assertTrue(in_literal(body));self.assertEqual(local_analysis(body,new_project())['items'],[])
        self.assertFalse(in_literal('text = "done"\nmessagebox.'))
        self.assertFalse(in_literal('"hello".'))
    def test_module_aliases_and_shadowing(self):
        body='from tkinter import messagebox as mb\nmb.'
        self.assertIn('showinfo',{i['name'] for i in local_analysis('mb.',new_project(),body)['items']})
        self.assertEqual(local_analysis('messagebox.',new_project(),'messagebox = object()\nmessagebox.')['items'],[])
        self.assertIsInstance(local_analysis('sys.version.',new_project(),'import sys\nsys.version.')['items'],list)
    def test_component_replacement_keeps_receiver(self):
        p=new_project();p['forms'][0]['widgets']=[{'name':'Button1','kind':'Button','props':{}}]
        result=local_analysis('self.Button1.con',p)
        option=next(i for i in result['items'] if i['insert']=='configure')
        self.assertEqual('self.Button1.con'[:-option['prefix_len']]+option['insert'],'self.Button1.configure')
    def test_editor_source_maps_cursor_in_both_contexts(self):
        body='messagebox.'
        for mode in ('event','imports'):
            source,row,col=editor_source(request(body,mode=mode))
            self.assertEqual(source.splitlines()[row-1][:col].strip(),body)


@unittest.skipUnless(importlib.util.find_spec('jedi'),'Jedi non installato nel runtime dei test')
class SemanticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.cache=tempfile.TemporaryDirectory();cls.engine=SemanticEngine(cls.cache.name)
    @classmethod
    def tearDownClass(cls):cls.cache.cleanup()
    def names(self,body,**extra):return {i['name'] for i in self.engine.analyze(request(body,**extra))['items']}
    def test_messagebox_and_active_argument(self):
        self.assertIn('showinfo',self.names('messagebox.'))
        self.assertIn('title=',self.names('messagebox.showinfo(ti'))
        result=self.engine.analyze(request('messagebox.showinfo("Title", ',action='signature'))
        self.assertIn('showinfo',result['calltip']);self.assertIn(tr('   • argomento: ')+'message',result['calltip'])
        partial=self.engine.analyze(request('messagebox.showinfo("Title", "Operazione',action='signature'))
        self.assertIn('showinfo',partial['calltip'])
    def test_python_variables_and_chained_calls(self):
        self.assertIn('upper',self.names('value = "hello"\nvalue.'))
        self.assertIn('read_text',self.names('from pathlib import Path\nPath(".").'))
        self.assertIn('append',self.names('values = []\nvalues.'))
    def test_project_imports_aliases_and_module_editor(self):
        p=new_project();p['imports']='import pathlib as paths'
        self.assertIn('Path',self.names('paths.',project=p))
        self.assertIn('sqrt',self.names('import math as m\nm.',mode='imports'))
    def test_all_inherited_widget_methods(self):
        p=new_project();p['forms'][0]['widgets']=[{'name':'Button1','kind':'Button','props':{}}]
        names=self.names('self.Button1.',project=p)
        self.assertTrue({'configure','cget','bind','after','invoke','pack','winfo_width'}.issubset(names))
    def test_selected_method_has_real_documentation(self):
        data=self.engine.analyze(request('messagebox.',action='detail',detail_name='showinfo'))['detail']
        self.assertIn('showinfo',data['signature']);self.assertTrue(data['doc'])
    def test_external_module_and_component_are_analyzed_without_execution(self):
        with tempfile.TemporaryDirectory() as folder:
            directory=Path(folder);marker=directory/'EXECUTED'
            (directory/'widget_fixture.py').write_text(f'from pathlib import Path\nPath({str(marker)!r}).write_text("bad")\nclass Fancy:\n    def __init__(self, master=None):\n        self.caption = "Hello"\n    def activate(self, enabled: bool = True):\n        """Enable the widget."""\n        return enabled\n')
            p=new_project();p['components']={'FancyControl':{'module':'widget_fixture','class':'Fancy','defaults':{},'requirements':[]}}
            p['forms'][0]['widgets']=[{'name':'Fancy1','kind':'FancyControl','props':{}}]
            data=self.engine.analyze(request('self.Fancy1.',p,cwd=folder))
            self.assertTrue({'activate','caption'}.issubset({i['name'] for i in data['items']}));self.assertFalse(marker.exists())
    @unittest.skipUnless(importlib.util.find_spec('numpy'),'NumPy non installato')
    def test_installed_numpy(self):
        names=self.names('import numpy as np\nnp.')
        self.assertTrue({'array','asarray','linspace','mean','zeros'}.issubset(names))


class AnalysisTransportTests(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec('jedi'),'Jedi not installed')
    def test_persistent_worker_and_clean_shutdown(self):
        client=AnalysisClient(timeout=25)
        try:
            identifier=client.submit(sys.executable,request('messagebox.'))
            result=client.results.get(timeout=30);self.assertEqual(result['id'],identifier);self.assertNotIn('error',result)
            self.assertIn('showinfo',{i['name'] for i in result['items']})
            pid=client.process.pid
            client.submit(sys.executable,request('messagebox.sh'))
            result=client.results.get(timeout=30);self.assertEqual(client.process.pid,pid);self.assertIn('showinfo',{i['name'] for i in result['items']})
        finally:client.close();client.thread.join(timeout=3)
        self.assertFalse(client.thread.is_alive())
    def test_timeout_does_not_block_ui_thread(self):
        with tempfile.TemporaryDirectory() as folder:
            worker=Path(folder)/'slow.py';worker.write_text('import time\ntime.sleep(60)\n')
            client=AnalysisClient(worker=worker,timeout=.2)
            try:
                start=time.monotonic();client.submit(sys.executable,request('x.'));self.assertLess(time.monotonic()-start,.1)
                self.assertIn('error',client.results.get(timeout=4))
            finally:client.close();client.thread.join(timeout=2)
    def test_missing_jedi_is_actionable(self):
        with tempfile.TemporaryDirectory() as folder:
            # -S removes installed packages without modifying the user's interpreter.
            wrapper=Path(folder)/'worker.py';real=Path(__file__).resolve().parents[1]/'intellisense_worker.py'
            wrapper.write_text('import os,sys\nos.execv(sys.executable,[sys.executable,"-S",'+repr(str(real))+'])\n')
            client=AnalysisClient(worker=wrapper)
            try:
                client.submit(sys.executable,request('messagebox.'));result=client.results.get(timeout=8);self.assertTrue(result.get('missing_jedi'))
            finally:client.close();client.thread.join(timeout=2)
    def test_replacement_inserts_only_member_name(self):
        from assist_ui import AssistMixin
        class Text:
            def __init__(self):self.value='messagebox.sh'
            def edit_separator(self):pass
            def delete(self,start,end):self.value=self.value[:-int(start.split('-')[1][:-1])]
            def insert(self,index,text):self.value+=text
            def focus_set(self):pass
        code=Text();fake=types.SimpleNamespace(assist_popup=True,completion_box=types.SimpleNamespace(curselection=lambda:(0,)),completion_items=[{'insert':'showinfo','prefix_len':2}],code=code,dismiss_completion=lambda:None,highlight=lambda:None,after=lambda *a:'timer')
        AssistMixin.accept_completion(fake);self.assertEqual(code.value,'messagebox.showinfo')

class TargetEnvironmentTests(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec('jedi'),'Jedi not installed')
    def test_library_in_selected_environment_is_visible(self):
        with tempfile.TemporaryDirectory() as directory:
            env=Path(directory)/'environment'
            result=subprocess.run([sys.executable,'-m','venv','--system-site-packages',str(env)],capture_output=True,text=True,timeout=40)
            self.assertEqual(result.returncode,0,result.stderr)
            python=str(env/'bin/python')
            target=subprocess.check_output([python,'-c','import site,sys; from pathlib import Path; print(next(p for p in site.getsitepackages() if Path(p).is_relative_to(sys.prefix)))'],text=True).strip();self.assertTrue(Path(target).resolve().is_relative_to(env.resolve()))
            # A nested venv inherits the base interpreter, not its parent venv's packages.
            for dependency in ('jedi','parso'):
                spec=importlib.util.find_spec(dependency)
                shutil.copytree(Path(spec.origin).parent,Path(target)/dependency,dirs_exist_ok=True)
            package=Path(target)/'vts_selected_only';package.mkdir();(package/'__init__.py').write_text('def unique_operation(value: str = "hello") -> str:\n    """Only installed in selected environment."""\n    return value\n')
            self.assertIsNone(importlib.util.find_spec('vts_selected_only'))
            client=AnalysisClient(timeout=20)
            try:
                client.submit(python,request('import vts_selected_only as lib\nlib.'))
                result=client.results.get(timeout=25);self.assertNotIn('error',result);self.assertIn('unique_operation',{i['name'] for i in result['items']})
            finally:client.close();client.thread.join(timeout=3)
    def test_old_response_does_not_reopen_dismissed_popup(self):
        from assist_ui import AssistMixin
        from unittest.mock import Mock
        results=queue.Queue();results.put({'id':1,'items':[{'name':'stale'}]});show=Mock()
        fake=types.SimpleNamespace(analysis_client=types.SimpleNamespace(results=results),analysis_requests={1:(('old',),True,None)},assist_snapshot=lambda:('new',),show_completions=show,after=lambda *a:'timer',poll_analysis=lambda:None)
        AssistMixin.poll_analysis(fake);show.assert_not_called()

class CompletionFocusTests(unittest.TestCase):
    def test_suggestions_use_an_in_window_panel_without_focus_calls(self):
        from assist_ui import AssistMixin
        from unittest.mock import Mock
        code=Mock();code.bbox.return_value=(10,15,0,20);code.winfo_rootx.return_value=120;code.winfo_rooty.return_value=140
        fake=types.SimpleNamespace(assist_popup=None,code=code,config_data={},winfo_width=lambda:800,winfo_height=lambda:600,winfo_rootx=lambda:100,winfo_rooty=lambda:100,completion_describe=Mock(),accept_completion=Mock())
        panel=Mock();box=Mock()
        with patch('assist_ui.tk.Frame',return_value=panel) as frame,patch('assist_ui.tk.Toplevel') as native,patch('assist_ui.tk.Listbox',return_value=box),patch('assist_ui.ttk.Scrollbar'):
            AssistMixin.show_completions(fake,[{'name':'showinfo','insert':'showinfo','prefix_len':0}])
        native.assert_not_called();frame.assert_called_once_with(fake,takefocus=False,borderwidth=1,relief='solid')
        panel.place.assert_called_once_with(x=30,y=75,width=540,height=240)
        code.focus_set.assert_not_called();box.focus_set.assert_not_called();panel.focus_set.assert_not_called()

class IntellisenseUITests(unittest.TestCase):
    def test_dot_popup_and_acceptance(self):
        from test_studio import GUI
        if not GUI:self.skipTest('Sessione grafica non disponibile')
        from studio import Studio
        with patch('studio.ensure_current'):app=Studio()
        app.update()
        try:
            app.tabs.select(1);app.code.delete('1.0','end');app.code.insert('1.0','messagebox.');app.code.mark_set('insert','end-1c');app.complete()
            app.update()
            self.assertIsNotNone(app.assist_popup)
            self.assertIs(app.assist_popup.winfo_toplevel(),app)
            self.assertIs(app.focus_get(),app.code)
            app.code.event_generate('<KeyPress>',keysym='s');app.update()
            self.assertEqual(app.code.get('1.0','end-1c'),'messagebox.s')
            app.code.delete('insert-1c','insert')
            index=next(i for i,item in enumerate(app.completion_items) if item['name']=='showinfo')
            app.completion_box.selection_clear(0,'end');app.completion_box.selection_set(index);app.accept_completion()
            self.assertEqual(app.code.get('1.0','end-1c'),'messagebox.showinfo')
        finally:app.temp.cleanup();app.destroy()
