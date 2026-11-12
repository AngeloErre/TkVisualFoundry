import copy
import io
import json
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from components import BUILTINS, descriptor, registry, requirements, install_args
from core import new_project, generate
from library_explorer import package_info

class ExtensionTests(unittest.TestCase):
    def project(self):
        p=new_project()
        for name,d in BUILTINS.items():p['forms'][0]['widgets'].append({'name':name+'1','kind':name,'x':0,'y':0,'width':400,'height':200,'props':copy.deepcopy(d['defaults']),'events':{'Load':'pass'}})
        return p
    def test_embedded_source_and_dependencies(self):
        p=self.project();source=generate(p);compile(source,'media.py','exec')
        self.assertIn('class ImageGallery(tk.Frame):',source)
        self.assertNotIn('from visualtk_runtime import',source)
        for name,d in BUILTINS.items():
            constructor=d['class'] if d['module'] in ('visualtk_runtime','database_runtime') else '_component_'+name
            self.assertIn('self.'+name+'1 = '+constructor+'(',source)
        for spec in ['Pillow>=10','pygame-ce>=2.5.8','opencv-python>=4.10','pyusb>=1.2','pyserial>=3.5']:self.assertIn(spec,requirements(p))
        self.assertEqual(source.count('class WebcamView(tk.Frame):'),1)
    def test_unused_dependencies_not_required(self):self.assertEqual(requirements(new_project()),[])
    def test_external_descriptor_is_not_imported_by_designer(self):
        p=new_project();p['components']={'ExternalButton':{'module':'nonexistent_package','class':'CustomButton','defaults':{'text':'Hello'},'requirements':['example-package>=1']}}
        p['forms'][0]['widgets']=[{'name':'MyButton','kind':'ExternalButton','x':0,'y':0,'width':100,'height':30,'props':{'text':'Hi'},'events':{'Click':'print("hello")'}}]
        source=generate(p);self.assertIn('from nonexistent_package import CustomButton as _component_ExternalButton',source);self.assertIn('self.MyButton = _component_ExternalButton',source)
        self.assertIn('example-package>=1',requirements(p))
    def test_disallow_commands_urls_and_options(self):
        for spec in ['--target /tmp/x','git+https://github.com/a/b','foo; os_name=="posix"','foo\n--extra-index-url=x']:
            with self.assertRaises(ValueError):install_args('/python',[spec])
        with self.assertRaises(ValueError):descriptor({'module':'os;exit()','class':'Widget'})
        args=install_args('/python',['Pillow==11.0.0']);self.assertEqual(args[:4],['/python','-m','pip','install']);self.assertIn('https://pypi.org/simple',args)
    def test_pypi_metadata_protocol(self):
        response=io.BytesIO(json.dumps({'info':{'name':'Pillow','version':'11.0.0','summary':'Images'}}).encode())
        with patch('library_explorer.urlopen',return_value=response) as get:
            self.assertEqual(package_info('Pillow')['name'],'Pillow');self.assertEqual(get.call_args.args[0].full_url,'https://pypi.org/pypi/Pillow/json');self.assertEqual(get.call_args.kwargs['timeout'],15)
        with self.assertRaises(ValueError):package_info('../../wrong')
    def test_existing_project_compatibility(self):
        from core import load
        p=load(Path(__file__).resolve().parents[1]/'examples/Saluto.vtk.json');compile(generate(p),'old.py','exec')
    def test_runtime_import_without_optional_packages(self):
        import visualtk_runtime
        self.assertTrue(issubclass(visualtk_runtime.ImageGallery,__import__('tkinter').Frame))
    def test_usb_and_serial_virtual_events(self):
        p=self.project()
        for w in p['forms'][0]['widgets']:w['events']['DeviceError']='print("device error")'
        self.assertIn(".bind('<<DeviceError>>'",generate(p))

class OptionalWidgetUITests(unittest.TestCase):
    def test_optional_widgets_construct_without_opening_devices(self):
        from test_studio import GUI
        if not GUI:self.skipTest('Sessione grafica macOS non disponibile')
        import tkinter as tk
        import visualtk_runtime
        root=tk.Tk();root.withdraw()
        try:
            for name,d in BUILTINS.items():
                import importlib
                try:cls=getattr(importlib.import_module(d['module']),d['class'])
                except ImportError:continue
                widget=cls(root,**d['defaults']);widget.place(x=0,y=0,width=500,height=250);root.update();self.assertTrue(widget.winfo_exists());widget.destroy()
        finally:root.destroy()
