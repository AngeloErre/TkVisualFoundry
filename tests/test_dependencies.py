import copy
import json
import sys
from pathlib import Path
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core import new_project
from components import BUILTINS,requirements
from dependency_manager import dependency_plan,probe_interpreter,pip_install_command

class DependencyTests(unittest.TestCase):
    def test_webcam_explains_numpy_and_projects_match(self):
        p=new_project();specs=dependency_plan(p,'WebcamView');self.assertIn('numpy',specs);self.assertIn('opencv-python>=4.10',specs);self.assertIn('Pillow>=10',specs)
        p['forms'][0]['widgets']=[{'name':'Camera1','kind':'WebcamView','props':{}}]
        self.assertEqual(specs,requirements(p))
    def test_database_drivers_are_conditional(self):
        p=new_project();self.assertEqual(dependency_plan(p,'DatabaseView'),[])
        self.assertEqual(dependency_plan(p,'DatabaseView',{'backend':'mysql'}),['PyMySQL>=1.1','SQLAlchemy>=2.0'])
        self.assertIn('psycopg[binary]>=3',dependency_plan(p,'DatabaseView',{'backend':'postgresql'}))
    def test_explicit_interpreter_and_safe_arguments(self):
        cmd=pip_install_command('/path with spaces/python',['numpy','Pillow>=10'])
        self.assertEqual(cmd[0],'/path with spaces/python');self.assertIn('--prefer-binary',cmd);self.assertNotIn('--only-binary=:all:',cmd);self.assertNotIn('--user',cmd)
        with self.assertRaises(ValueError):pip_install_command('python',['numpy; rm -rf /'])
    def test_probe_real_metadata_and_missing_distribution(self):
        result=probe_interpreter(sys.executable,['pip','visualtk-nonexistent-test-package-123'])
        self.assertEqual(result[0]['state'],'ready');self.assertEqual(result[1]['state'],'missing')
    def test_incompatible_version_is_detected(self):
        result=probe_interpreter(sys.executable,['pip>=9999'])
        self.assertEqual(result[0]['state'],'incompatible')
    def test_probe_uses_target_and_propagates_failures(self):
        import subprocess
        with patch('dependency_manager.subprocess.run',side_effect=subprocess.TimeoutExpired('python',40)):
            with self.assertRaises(subprocess.TimeoutExpired):probe_interpreter('/custom/python',['numpy'])

class WizardPipelineTests(unittest.TestCase):
    def test_install_checks_pip_then_verifies_imports(self):
        import types,io
        from dependency_manager import install_dependencies
        processes=[]
        def process(args,**kwargs):
            proc=types.SimpleNamespace(stdout=io.StringIO('installation output\n'),wait=lambda:0,kill=lambda:None,terminate=lambda:None);processes.append(args);return proc
        expected=[{'state':'ready'}]
        with patch('dependency_manager.subprocess.run',return_value=types.SimpleNamespace(returncode=0,stdout='')),patch('dependency_manager.subprocess.Popen',side_effect=process),patch('dependency_manager.probe_interpreter',return_value=expected) as probe:
            self.assertEqual(install_dependencies(sys.executable,['numpy']),expected)
        self.assertEqual(len(processes),2);self.assertEqual(processes[-1][-2:],['pip','check']);probe.assert_called_once_with(sys.executable,['numpy'])
    def test_failed_install_never_reports_ready(self):
        import types,io
        from dependency_manager import install_dependencies
        proc=types.SimpleNamespace(stdout=io.StringIO('ERROR\n'),wait=lambda:1,kill=lambda:None,terminate=lambda:None)
        with patch('dependency_manager.subprocess.run',return_value=types.SimpleNamespace(returncode=0,stdout='')),patch('dependency_manager.subprocess.Popen',return_value=proc),patch('dependency_manager.probe_interpreter') as probe:
            with self.assertRaises(RuntimeError):install_dependencies(sys.executable,['numpy'])
        probe.assert_not_called()

class DependencyUITests(unittest.TestCase):
    def test_wizard_constructs_and_checks_standard_library_project(self):
        from test_studio import GUI
        if not GUI:self.skipTest('Sessione grafica macOS non disponibile')
        import tkinter as tk,time
        from studio import Studio
        from dependency_ui import DependencyWizard
        app=Studio();app.withdraw();wizard=DependencyWizard(app)
        try:
            wizard.after(0,wizard.verify)
            deadline=time.monotonic()+5
            while time.monotonic()<deadline:
                app.update()
                if str(wizard.ready_button['state'])=='normal':break
                time.sleep(.01)
            self.assertEqual(str(wizard.ready_button['state']),'normal')
        finally:wizard.dispose();app.temp.cleanup();app.destroy()
