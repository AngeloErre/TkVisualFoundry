import json
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock,patch
from project_environment import environment_python,create_environment
from environment_ui import EnvironmentMixin
class EnvironmentTests(unittest.TestCase):
    def test_real_creation_and_reuse_without_network(self):
        with tempfile.TemporaryDirectory() as folder:
            python=create_environment(sys.executable,folder)
            self.assertEqual(create_environment('/not-used',folder),python)
            code='import sys,tkinter,json; print(json.dumps([sys.prefix,sys.base_prefix]))'
            result=subprocess.run([python,'-c',code],capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,0,result.stderr);prefix,base=json.loads(result.stdout);self.assertNotEqual(prefix,base)
    def test_existing_non_environment_and_symlink_are_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'.venv').mkdir();(root/'.venv/keep.txt').write_text('keep')
            with self.assertRaises(ValueError):create_environment(sys.executable,root)
            self.assertEqual((root/'.venv/keep.txt').read_text(),'keep')
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'.venv').symlink_to(root/'elsewhere')
            with self.assertRaises(ValueError):environment_python(root)
    def test_failed_creation_cleans_only_new_directory(self):
        with tempfile.TemporaryDirectory() as folder,patch('project_environment.validate_interpreter'),patch('project_environment.subprocess.run',return_value=types.SimpleNamespace(returncode=1,stderr='failed',stdout='')):
            with self.assertRaises(RuntimeError):create_environment('/python',folder)
            self.assertFalse((Path(folder)/'.venv').exists())
    def test_switch_and_missing_env_never_falls_back_silently(self):
        with tempfile.TemporaryDirectory() as folder:
            fake=types.SimpleNamespace(path=Path(folder)/'project.json',project={'environment':{'managed':True}},global_python='/global',config_data={'python':'/global'},analysis_client=True,restart_intellisense=Mock())
            EnvironmentMixin.activate_project_environment(fake)
            self.assertEqual(fake.config_data['python'],str(environment_python(folder)))
            fake.project={};EnvironmentMixin.activate_project_environment(fake);self.assertEqual(fake.config_data['python'],'/global')
    def test_global_settings_do_not_persist_project_python(self):
        fake=types.SimpleNamespace(global_python='/global')
        with patch('environment_ui.atomic_write_text') as save:
            EnvironmentMixin.save_ide_settings(fake,{'python':'/project/.venv/bin/python','grid':10})
            self.assertEqual(json.loads(save.call_args.args[1])['python'],'/global')
