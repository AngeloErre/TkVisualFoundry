import json
from pathlib import Path
import tempfile
import unittest
from installation import record_install,uninstall_plan,confined
class InstallationTests(unittest.TestCase):
    def setup_install(self,folder):
        source=folder/'source';root=folder/'installed';source.mkdir();root.mkdir();(source/'studio.py').write_text('original');(root/'studio.py').write_text('original');(root/'.venv').mkdir();record_install(root,source);return source,root
    def test_plan_keeps_modified_and_unknown_project_files(self):
        with tempfile.TemporaryDirectory() as d:
            source,root=self.setup_install(Path(d));(root/'personal.vtk.json').write_text('user project');plan=uninstall_plan(root,expected=root);self.assertEqual(plan['files'],[root/'studio.py']);self.assertEqual(plan['environment'],root/'.venv')
            (root/'studio.py').write_text('user modification');plan=uninstall_plan(root,expected=root);self.assertEqual(plan['files'],[]);self.assertIn(root/'studio.py',plan['preserve']);self.assertTrue((root/'personal.vtk.json').exists())
    def test_wrong_root_paths_and_symlinks_are_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            source,root=self.setup_install(Path(d))
            with self.assertRaises(ValueError):uninstall_plan(root,expected=source)
            for path in ['../outside','/etc/passwd','C:/Windows/file','dir\\file']:
                with self.assertRaises(ValueError):confined(root,path)
            (root/'studio.py').unlink();(root/'studio.py').symlink_to(source/'studio.py')
            with self.assertRaises(ValueError):uninstall_plan(root,expected=root)
    def test_environment_ownership_mismatch_is_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            source,root=self.setup_install(Path(d));(root/'.venv/.visualtk-owner').write_text('different owner');plan=uninstall_plan(root,expected=root);self.assertIsNone(plan['environment']);self.assertIn(root/'.venv',plan['preserve'])
    def test_old_unknown_installation_is_not_deleted(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            with self.assertRaises(FileNotFoundError):uninstall_plan(root,expected=root)
    def test_actual_uninstall_in_fixture_preserves_personal_data(self):
        from unittest.mock import patch
        from installation import uninstall_mac
        with tempfile.TemporaryDirectory() as d:
            home=Path(d);source=home/'download';root=home/'Applications/VisualTkStudio';source.mkdir();root.mkdir(parents=True)
            (source/'studio.py').write_text('owned');(root/'studio.py').write_text('owned');(root/'.venv').mkdir();(root/'personal.vtk.json').write_text('personal');(root/'empty-personal-folder').mkdir();(home/'settings.json').write_text('settings');record_install(root,source)
            with patch('installation.Path.home',return_value=home),patch('installation.install_root',return_value=root),patch('builtins.input',return_value='y'):uninstall_mac(root)
            self.assertTrue((root/'empty-personal-folder').is_dir());self.assertFalse((root/'studio.py').exists());self.assertFalse((root/'.venv').exists());self.assertTrue((root/'personal.vtk.json').exists());self.assertTrue((home/'settings.json').exists())
    def test_rebrand_preserves_owned_legacy_launcher_and_modified_files(self):
        from unittest.mock import patch
        from installation import APP_NAME,LEGACY_APP_NAME
        with tempfile.TemporaryDirectory() as d:
            home=Path(d);source=home/'download';root=home/'Applications/VisualTkStudio';source.mkdir();root.mkdir(parents=True);(source/'studio.py').write_text('code');(root/'studio.py').write_text('code')
            old=home/'Applications'/LEGACY_APP_NAME;new=home/'Applications'/APP_NAME
            for app in (old,new):
                (app/'Contents/MacOS').mkdir(parents=True);(app/'Contents/Info.plist').write_text('owned plist');(app/'Contents/MacOS/VisualTkStudio').write_text('owned launcher')
            record_install(root,source,old)
            # Version 1.29 had no app_name field: it must remain a recognized old launcher.
            marker=root/'.visualtk-install.json';data=json.loads(marker.read_text());data.pop('app_name');marker.write_text(json.dumps(data))
            record_install(root,source,new);data=json.loads(marker.read_text());self.assertEqual(data['app_name'],APP_NAME);self.assertTrue(data['legacy_app_files'])
            (old/'Contents/Info.plist').write_text('user change')
            with patch('installation.Path.home',return_value=home):plan=uninstall_plan(root,expected=root,app=new)
            self.assertIn(old/'Contents/Info.plist',plan['preserve']);self.assertIn(old/'Contents/MacOS/VisualTkStudio',plan['files']);self.assertIn(new/'Contents/Info.plist',plan['files'])
    def test_recording_from_installed_folder_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            with self.assertRaises(ValueError):record_install(root,root)
