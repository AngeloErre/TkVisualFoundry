import io
import json
from pathlib import Path
import queue
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
import zipfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from component_palette import icon_pixels,KINDS,LayoutMixin
from dependency_manager import install_dependencies,preparation_action,PACKAGE_MODULES,probe_interpreter

class LayoutAndPreparationTests(unittest.TestCase):
    def test_icons_for_components_without_font_or_pillow(self):
        for kind in list(KINDS)+['ExternalControl']:
            pixels=icon_pixels(kind);self.assertEqual(len(pixels),20);self.assertTrue(all(len(row)==20 for row in pixels))
            self.assertTrue(any(color=='#ffffff' for row in pixels for color in row))
        self.assertNotEqual(icon_pixels('WebcamView'),icon_pixels('DatabaseView'))
    def test_auto_preparation_proceeds_and_never_retries_forever(self):
        missing=[{'state':'missing'}];ready=[{'state':'ready'}]
        self.assertEqual(preparation_action(missing,True,False,True),'install')
        self.assertEqual(preparation_action(ready,True,True,True),'continue')
        self.assertEqual(preparation_action(missing,True,True,True),'wait')
        self.assertEqual(preparation_action(ready,False,False,False),'ready')
    def test_log_cannot_cover_component_actions(self):
        pane=types.SimpleNamespace(winfo_height=lambda:600,panes=lambda:('main','log'))
        position=[10];pane.sashpos=lambda index,*new:position.__setitem__(0,new[0]) if new else position[0]
        LayoutMixin.clamp_log(types.SimpleNamespace(vertical=pane,log_visible=True))
        self.assertGreaterEqual(position[0],390)
    def test_native_import_failure_is_reported_per_package(self):
        metadata='VISUALTK_DEPENDENCIES='+json.dumps([{'package':'numpy','spec':'numpy','version':'2','state':'ready','detail':''}])
        with patch('dependency_manager.subprocess.run',side_effect=[types.SimpleNamespace(returncode=0,stdout=metadata,stderr=''),types.SimpleNamespace(returncode=-6,stdout='',stderr='native module failed')]):
            result=probe_interpreter('/python',['numpy'])
        self.assertEqual(result[0]['state'],'broken');self.assertIn('native module',result[0]['detail'])
    def test_automatic_result_schedules_continuation(self):
        from dependency_ui import DependencyWizard
        events=queue.Queue();events.put(('result',[{'spec':'numpy','state':'ready','version':'2','detail':'OK'}]));scheduled=[]
        controls=types.SimpleNamespace(get=lambda:True)
        fake=types.SimpleNamespace(closed=False,events=events,busy=True,results=[],automatic=controls,install_attempted=False,on_ready=lambda:None,table=types.SimpleNamespace(item=lambda *a,**k:None),controls=lambda:None,status=types.SimpleNamespace(set=lambda value:None),pages=types.SimpleNamespace(select=lambda value:None),finish=lambda:None)
        fake.after=lambda delay,callback:scheduled.append(callback) or 'id';fake.poll=lambda:None
        DependencyWizard.poll(fake)
        self.assertTrue(fake.ready);self.assertIn(fake.finish,scheduled)

class PipConflictTests(unittest.TestCase):
    def run_conflict(self,current):
        proc=lambda code:types.SimpleNamespace(stdout=io.StringIO('dependency conflict\n'),wait=lambda:code,kill=lambda:None,terminate=lambda:None)
        checks=[types.SimpleNamespace(returncode=0,stdout=''),types.SimpleNamespace(returncode=1,stdout='old conflict\n'),types.SimpleNamespace(returncode=1,stdout=current)]
        with patch('dependency_manager.subprocess.run',side_effect=checks),patch('dependency_manager.subprocess.Popen',side_effect=[proc(0),proc(1)]),patch('dependency_manager.probe_interpreter',return_value=[{'state':'ready'}]):
            return install_dependencies('/python',['example'])
    def test_preexisting_conflict_is_not_blame_for_new_install(self):
        self.assertEqual(self.run_conflict('old conflict\n'),[{'state':'ready'}])
    def test_new_conflicts_block_success(self):
        with self.assertRaisesRegex(RuntimeError,'Conflitti'):self.run_conflict('new conflict\n')

class RealPipOfflineTests(unittest.TestCase):
    def test_real_install_in_isolated_environment_without_network(self):
        with tempfile.TemporaryDirectory(prefix='visualtk-pip-test-') as directory:
            root=Path(directory);venv=root/'venv'
            result=subprocess.run([sys.executable,'-m','venv',str(venv)],capture_output=True,text=True,timeout=45)
            self.assertEqual(result.returncode,0,result.stderr)
            python=str(venv/('Scripts/python.exe' if sys.platform=='win32' else 'bin/python'))
            wheel=root/'visualtk_pip_smoke-1.0-py3-none-any.whl';dist='visualtk_pip_smoke-1.0.dist-info'
            files={'visualtk_pip_smoke/__init__.py':'VALUE = 42\n',dist+'/METADATA':'Metadata-Version: 2.1\nName: visualtk-pip-smoke\nVersion: 1.0\n\n',dist+'/WHEEL':'Wheel-Version: 1.0\nGenerator: VisualTkTests\nRoot-Is-Purelib: true\nTag: py3-none-any\n'}
            files[dist+'/RECORD']=''.join(name+',,\n' for name in list(files)+[dist+'/RECORD'])
            with zipfile.ZipFile(wheel,'w') as archive:
                for name,content in files.items():archive.writestr(name,content)
            def offline(python,specs,binary_only):return [python,'-m','pip','install','--no-index','--find-links',str(root),*specs]
            output=[]
            with patch('dependency_manager.pip_install_command',side_effect=offline),patch.dict(PACKAGE_MODULES,{'visualtk-pip-smoke':'visualtk_pip_smoke'}):
                states=install_dependencies(python,['visualtk-pip-smoke==1.0'],on_output=output.append)
            self.assertEqual(states[0]['state'],'ready');self.assertEqual(states[0]['detail'],'Import verificato')
            actual=subprocess.run([python,'-c','import visualtk_pip_smoke; print(visualtk_pip_smoke.VALUE)'],capture_output=True,text=True,timeout=10)
            self.assertEqual(actual.stdout.strip(),'42');self.assertTrue(any('Successfully installed' in line for line in output))

class CompactLayoutUITests(unittest.TestCase):
    def test_buttons_remain_visible_with_log_at_minimum_size(self):
        from test_studio import GUI
        if not GUI:self.skipTest('Sessione grafica macOS non disponibile')
        from studio import Studio
        app=Studio();app.geometry('1050x650');app.update()
        try:
            app.show_log(True);app.update();app.vertical.sashpos(0,5);app.clamp_log();app.update()
            for button in (app.insert_button,app.apply_button):
                self.assertTrue(button.winfo_viewable());self.assertGreater(button.winfo_height(),10)
                self.assertLess(button.winfo_rooty()+button.winfo_height(),app.vertical.winfo_rooty()+app.vertical.sashpos(0))
            self.assertGreaterEqual(len(app.menu_buttons),7)
            app.palette.selection_set(0);app.palette_query.set('Button');app.update();self.assertIn('Button',app.palette.names)
        finally:app.temp.cleanup();app.destroy()
    def test_pip_actions_visible_even_on_small_window(self):
        from test_studio import GUI
        if not GUI:self.skipTest('Sessione grafica macOS non disponibile')
        from studio import Studio
        from dependency_ui import DependencyWizard
        app=Studio();app.update();wizard=DependencyWizard(app);wizard.geometry('640x420');app.update()
        try:
            for control in (wizard.install_button,wizard.verify_button,wizard.cancel_button):
                self.assertTrue(control.winfo_viewable());self.assertLessEqual(control.winfo_rooty()+control.winfo_height(),wizard.winfo_rooty()+wizard.winfo_height())
        finally:wizard.dispose();app.temp.cleanup();app.destroy()
