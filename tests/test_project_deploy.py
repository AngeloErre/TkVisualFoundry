import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import plistlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core import new_project
from project_files import project_file,list_files,included_files,rename_file,trash_file
from deployment import export_deployment
import deploy_build

class ProjectFilesTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.project=new_project()
    def tearDown(self):self.temp.cleanup()
    def test_confines_paths_and_symlinks(self):
        for name in ['../outside','/tmp/test','C:/windows','folder/../../bad','.git/config','folder\\bad']:
            with self.assertRaises(ValueError):project_file(self.root,name)
        outside=self.root.parent/'outside';(self.root/'link').symlink_to(outside)
        with self.assertRaises(ValueError):project_file(self.root,'link/secret')
    def test_inclusion_rename_and_recoverable_trash(self):
        (self.root/'assets').mkdir();(self.root/'assets/a.txt').write_text('hello');self.project['files']=['assets','assets/a.txt']
        self.assertEqual(set(included_files(self.project,self.root)),{'assets/a.txt'})
        rename_file(self.project,self.root,'assets','resources');self.assertEqual(self.project['files'],['resources','resources/a.txt'])
        target=trash_file(self.project,self.root,'resources');self.assertEqual((target/'a.txt').read_text(),'hello');self.assertEqual(self.project['files'],[])
        self.assertEqual(list_files(self.root),[])
    def test_skips_venv_hidden_and_links(self):
        for name in ['.git','.venv','dist','build','assets']:(self.root/name).mkdir()
        (self.root/'assets/a.txt').write_text('x');(self.root/'assets/.secret').write_text('private')
        self.assertEqual(list_files(self.root),[('assets',True),('assets/a.txt',False)])
    def test_no_overwrite(self):
        for name in ['a.txt','b.txt']:(self.root/name).write_text(name)
        with self.assertRaises(FileExistsError):rename_file(self.project,self.root,'a.txt','b.txt')
        self.assertEqual((self.root/'b.txt').read_text(),'b.txt')

class DeploymentTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.project=new_project('en');self.path=self.root/'demo.vtk.json';self.path.write_text('{}');self.dest=self.root/'deploy'
    def tearDown(self):self.temp.cleanup()
    def export(self,**kwargs):return export_deployment(self.project,self.path,self.dest,kwargs.get('name','Demo'),kwargs.get('version','1.0.0'))
    def test_kit_contains_selected_resources_and_platform_scripts(self):
        (self.root/'assets').mkdir();(self.root/'assets/readme.txt').write_text('resource');(self.root/'unselected.txt').write_text('private')
        (self.root/'helper.py').write_text('ANSWER=42');self.project['files']=['assets','helper.py'];self.project['imports']='import helper'
        original=copy.deepcopy(self.project);target=self.export();self.assertEqual(self.project,original)
        self.assertEqual((target/'src/assets/readme.txt').read_text(),'resource');self.assertFalse((target/'src/unselected.txt').exists())
        for name in ['Run_Mac.command','Build_Mac.command','Install_Mac.command','Run_Windows.cmd','Build_Windows.cmd','Install_Windows.cmd','Installer_Windows.iss','deploy_build.py','requirements.txt','README_DEPLOY.md']:self.assertTrue((target/name).is_file(),name)
        self.assertTrue((target/'Build_Mac.command').stat().st_mode&0o111)
        subprocess.run(['bash','-n',str(target/'Build_Mac.command')],check=True)
        compile((target/'src/main.py').read_text(),'main.py','exec');compile((target/'deploy_build.py').read_text(),'deploy_build.py','exec')
        # Load the exported module from its source folder without creating a Tk root.
        result=subprocess.check_output([sys.executable,'-c','import runpy; scope=runpy.run_path("main.py",run_name="check");print(scope["helper"].ANSWER)'],cwd=target/'src',text=True)
        self.assertEqual(result.strip(),'42')
        self.assertIn('PrivilegesRequired=lowest',(target/'Installer_Windows.iss').read_text())
    def test_never_overwrites_existing_kit(self):
        target=self.export();(target/'keep').write_text('keep')
        with self.assertRaises(FileExistsError):self.export()
        self.assertEqual((target/'keep').read_text(),'keep')
    def test_names_cannot_inject_commands_or_installer_directives(self):
        for name in ['bad name','../bad','Demo\n[Run]','Demo;touch','3demo']:
            with self.assertRaises(ValueError):self.export(name=name)
        for version in ['1\n[Run]','latest','1;touch']:
            with self.assertRaises(ValueError):self.export(version=version)
    def test_missing_resources_and_reserved_main_fail(self):
        self.project['files']=['missing.png']
        with self.assertRaises(ValueError):self.export()
        (self.root/'main.py').write_text('print("do not overwrite")');self.project['files']=['main.py']
        with self.assertRaises(ValueError):self.export()
        self.assertFalse((self.dest/'Demo-1.0.0').exists())
    def test_destination_cannot_be_inside_included_folder(self):
        (self.root/'assets').mkdir();self.project['files']=['assets'];self.dest=self.root/'assets'
        with self.assertRaises(ValueError):self.export()
    def test_failed_copy_leaves_no_partial_kit(self):
        with patch('deployment.shutil.copy2',side_effect=OSError('failed')):
            with self.assertRaises(OSError):self.export()
        self.assertEqual(list(self.dest.iterdir()),[])

class NativeBuildPlanTests(unittest.TestCase):
    def test_build_tool_caches_stay_inside_the_kit(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            with patch.object(deploy_build,'ROOT',root),patch.object(deploy_build.subprocess,'run') as run:
                deploy_build.call(['python','--version'])
            env=run.call_args.kwargs['env']
            self.assertEqual(env['PYINSTALLER_CONFIG_DIR'],str(root/'.pyinstaller-cache'))
            self.assertEqual(env['PIP_CACHE_DIR'],str(root/'.pip-cache'))

    def prepare(self,root):
        (root/'src').mkdir();(root/'src/main.py').write_text('pass');(root/'requirements.txt').write_text('SQLAlchemy\npsycopg[binary]\n')
        (root/'deploy.json').write_text(json.dumps({'name':'Demo','version':'1.0.0'}));(root/'Installer_Windows.iss').write_text('[Setup]')
        for relative in ['.venv/bin/python','.venv/Scripts/python.exe']:
            p=root/relative;p.parent.mkdir(parents=True,exist_ok=True);p.touch()
    def test_mac_build_has_resources_and_dmg(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.prepare(root);info=root/'dist/Demo.app/Contents/Info.plist';info.parent.mkdir(parents=True);info.write_bytes(plistlib.dumps({}))
            with patch.object(deploy_build,'ROOT',root),patch.object(deploy_build.sys,'platform','darwin'),patch.object(deploy_build,'call') as call:deploy_build.main('build')
            commands=[c.args[0] for c in call.call_args_list];pyinstaller=next(cmd for cmd in commands if 'PyInstaller' in cmd)
            self.assertIn('--add-data',pyinstaller);self.assertIn(str(root/'src')+':.',pyinstaller)
            self.assertTrue(any(cmd[0]=='hdiutil' for cmd in commands));self.assertIn('NSCameraUsageDescription',plistlib.loads(info.read_bytes()))
    def test_mac_dmg_failure_preserves_app_and_creates_zip(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.prepare(root);info=root/'dist/Demo.app/Contents/Info.plist';info.parent.mkdir(parents=True);info.write_bytes(plistlib.dumps({}))
            def invoke(args):
                if args[0]=='hdiutil':raise subprocess.CalledProcessError(1,args)
            with patch.object(deploy_build,'ROOT',root),patch.object(deploy_build.sys,'platform','darwin'),patch.object(deploy_build,'call',side_effect=invoke) as call:
                deploy_build.main('build')
            self.assertTrue(info.exists());self.assertTrue(any(c.args[0][0]=='ditto' for c in call.call_args_list))

    def test_windows_build_emits_installer_when_compiler_available(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.prepare(root)
            with patch.object(deploy_build,'ROOT',root),patch.object(deploy_build.sys,'platform','win32'),patch.object(deploy_build,'call') as call,patch.object(deploy_build.shutil,'make_archive') as archive,patch.object(deploy_build.shutil,'which',return_value='ISCC.exe'):
                deploy_build.main('build')
            archive.assert_called_once();self.assertTrue(any(c.args[0][0]=='ISCC.exe' for c in call.call_args_list))
