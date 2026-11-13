import json
from pathlib import Path
import tempfile
import unittest
import plistlib
from unittest.mock import patch
import deploy_build
from PIL import Image
from core import new_project
from deploy_icons import import_icon,icon_image
from deployment import export_deployment

class IconTests(unittest.TestCase):
    def test_formats_runtime_and_installer(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'source.png';Image.new('RGBA',(1024,1024),(30,100,200,180)).save(source)
            relative=import_icon(source,root);p=new_project();p['deployment']={'icon':relative}
            original=source.read_bytes();kit=export_deployment(p,root/'project.vtk.json',root/'deploy','IconDemo','1.0')
            meta=json.loads((kit/'deploy.json').read_text())
            for key,fmt in [('mac','ICNS'),('windows','ICO')]:
                with Image.open(kit/meta['icons'][key]) as icon:self.assertEqual(icon.format,fmt)
            self.assertTrue((kit/'src/_visualtk_icon.png').exists());self.assertIn('iconphoto(True', (kit/'src/main.py').read_text())
            compile((kit/'src/main.py').read_text(),'main','exec')
            for executable in ('.venv/bin/python','.venv/Scripts/python.exe'):
                executable=kit/executable;executable.parent.mkdir(parents=True,exist_ok=True);executable.touch()
            plist=kit/'dist/IconDemo.app/Contents/Info.plist';plist.parent.mkdir(parents=True);plist.write_bytes(plistlib.dumps({}))
            for platform,key in (('darwin','mac'),('win32','windows')):
                with patch.object(deploy_build,'ROOT',kit),patch.object(deploy_build.sys,'platform',platform),patch.object(deploy_build,'call') as call,patch.object(deploy_build.shutil,'make_archive'),patch.object(deploy_build.shutil,'which',return_value=None):
                    deploy_build.main('build')
                    command=next(c.args[0] for c in call.call_args_list if 'PyInstaller' in c.args[0])
                    self.assertEqual(command[command.index('--icon')+1],str((kit/meta['icons'][key]).resolve()))
            self.assertIn('SetupIconFile=build-assets', (kit/'Installer_Windows.iss').read_text());self.assertEqual(source.read_bytes(),original)
            from project_files import rename_file,trash_file
            rename_file(p,root,'assets/app-icons','assets/branding');self.assertTrue(p['deployment']['icon'].startswith('assets/branding/'))
            trash_file(p,root,'assets/branding');self.assertEqual(p['deployment']['icon'],'')
    def test_invalid_artwork_and_missing_file(self):
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/'bad.png'
            for size in ((100,100),(500,300)):
                Image.new('RGB',size).save(source)
                with self.assertRaises(ValueError):icon_image(source)
            source.write_text('not an image')
            with self.assertRaises(OSError):icon_image(source)
    def test_missing_icon_cleans_partial_kit(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);p=new_project();p['deployment']={'icon':'missing.png'}
            with self.assertRaises(FileNotFoundError):export_deployment(p,root/'project.vtk.json',root/'deploy','Missing','1.0')
            self.assertEqual(list((root/'deploy').iterdir()),[])
