import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock,patch
from core import new_project,generate,validate
from components import BUILTINS,requirements
from hierarchy import ordered_widgets,descendants,widget_origin,visible_widgets
from library_catalog import LIBRARIES,theme_config,packaging_flags,component_family
from library_checks import check_library
from workspace_ui import duplicate_form
from container_ui import ContainerMixin
from code_assist import methods,examples
from deployment import export_deployment
import integration_runtime
from theme_runtime import apply_project_theme

def widget(name,kind='Frame',parent=None,page=None,props=None):
    result=dict(name=name,kind=kind,x=10,y=20,width=200,height=100,props=props or {},events={})
    if parent:result['parent']=parent
    if page:result['page']=page
    return result

class HierarchyTests(unittest.TestCase):
    def project(self):
        p=new_project();p['forms'][0]['widgets']=[widget('Child','Button','Inner',props={'text':'OK'}),widget('Inner','Frame','Tabs','One'),widget('Tabs','Notebook',props={'pages':['One','Two']}),widget('Other','Label','Tabs','Two')];return p
    def test_generation_orders_containers_and_uses_page_master(self):
        p=self.project();validate(p);source=generate(p)
        self.assertLess(source.index('self.Tabs ='),source.index('self.Inner ='));self.assertLess(source.index('self.Inner ='),source.index('self.Child ='))
        self.assertIn("self.Inner = tk.Frame(self.Tabs.pages['One']",source);self.assertIn('self.Child = tk.Button(self.Inner',source)
    def test_runtime_parent_relationships_without_display(self):
        p=new_project();p['forms'][0]['widgets']=[widget('Child','Button','Frame1'),widget('Frame1','Frame')]
        class W:
            def __init__(self,parent=None,**kw):self.parent=parent
            def __getattr__(self,name):return lambda *a,**k:None
        fake=types.ModuleType('tkinter');fake.Tk=fake.Toplevel=fake.Frame=fake.Button=W
        for name in ('ttk','messagebox','filedialog','simpledialog','colorchooser','font'):setattr(fake,name,types.SimpleNamespace())
        with patch.dict(sys.modules,{'tkinter':fake}):
            scope={'__name__':'test'};exec(generate(p),scope);app=scope['Application']()
        self.assertIs(app.Child.parent,app.Frame1);self.assertIs(app.Frame1.parent,app.Form1)
    def test_cycle_noncontainer_foreign_parent_and_invalid_page_are_rejected(self):
        for change in [lambda ws:ws[2].update(parent='Child'),lambda ws:ws[0].update(parent='Other'),lambda ws:ws[0].update(parent='Missing'),lambda ws:ws[1].update(page='Missing')]:
            p=self.project();change(p['forms'][0]['widgets'])
            with self.assertRaises(ValueError):validate(p)
    def test_coordinates_pages_and_descendants(self):
        form=self.project()['forms'][0];child=form['widgets'][0]
        self.assertEqual(widget_origin(form,child),(30,88));self.assertEqual(descendants(form,'Tabs'),{'Inner','Child','Other'})
        self.assertEqual({w['name'] for w in visible_widgets(form,{'Tabs':'Two'})},{'Tabs','Other'})
    def test_form_duplication_remaps_parents_preserving_events(self):
        p=self.project();p['forms'][0]['widgets'][0]['events']={'Click':'print("unchanged")'};new=duplicate_form(p,0);p['forms'].append(new);validate(p)
        names={w['name'] for w in new['widgets']};self.assertTrue(all(not w.get('parent') or w['parent'] in names for w in new['widgets']))
        self.assertEqual(new['widgets'][0]['events'],{'Click':'print("unchanged")'})
    def test_widget_subtree_duplication_remaps_descendants(self):
        p=self.project();form=p['forms'][0];root=next(w for w in form['widgets'] if w['name']=='Tabs');fake=types.SimpleNamespace(selected=root,project=p,form=form)
        ContainerMixin.duplicate_widget_tree(fake);self.assertNotEqual(fake.selected['name'],'Tabs');self.assertEqual(len(form['widgets']),8);validate(p)
    def test_duplicate_tab_names_rejected(self):
        p=self.project();p['forms'][0]['widgets'][2]['props']['pages']=['One','One']
        with self.assertRaises(ValueError):validate(p)

class LibraryIntegrationTests(unittest.TestCase):
    def test_catalog_contains_every_requested_family(self):
        self.assertGreaterEqual(len(LIBRARIES),19);names={row[0] for row in LIBRARIES}
        self.assertTrue({'CustomTkinter','ttkbootstrap','ttkthemes','sv-ttk','Azure','Forest','Pmw','Tix','PySimpleGUI','FreeSimpleGUI','guizero'}.issubset(names))
        for name in ('PySimpleGUI','FreeSimpleGUI','guizero'):self.assertEqual(check_library(sys.executable,name)['state'],'separate')
        self.assertEqual(check_library(sys.executable,'Tix')['state'],'unsupported')
    def test_descriptors_and_source_for_new_widgets(self):
        p=new_project()
        for name in ('TButton','TLabelframe','CTkFrame','CTkScrollableFrame','CTkTabview','CTkSlider','CTkTextbox','Sheet','MapView','PmwComboBox'):
            desc=BUILTINS[name];p['forms'][0]['widgets'].append(widget(name+'1',name,props=copy.deepcopy(desc['defaults'])))
        source=generate(p);compile(source,'app.py','exec');self.assertIn('Pmw.initialise(self.root)',source);self.assertIn('class SheetView',source)
        self.assertIn('tksheet>=7,<8',requirements(p));self.assertIn('--collect-all=tkintermapview',packaging_flags(p));self.assertIn('--collect-all=customtkinter',packaging_flags(p))
    def test_customtkinter_geometry_is_passed_to_constructor(self):
        p=new_project();p['forms'][0]['widgets']=[widget('Modern1','CTkButton',props={'text':'OK'})]
        source=generate(p);self.assertIn("'width': 200, 'height': 100",source);self.assertIn('self.Modern1.place(x=10, y=20)',source);self.assertNotIn('self.Modern1.place(x=10, y=20, width=',source)
    def test_contextual_help_uses_adapter_methods_not_constructor_options(self):
        for kind,method in [('Sheet','set_cell'),('MapView','add_marker'),('CTkTabview','set')]:
            p=new_project();obj=widget('Control1',kind,props=BUILTINS[kind]['defaults']);p['forms'][0]['widgets']=[obj]
            self.assertIn(method,methods(obj));snippets='\n'.join(item[1] for item in examples(obj,p));self.assertNotIn('.configure(latitude=',snippets);self.assertNotIn('.configure(data=',snippets);self.assertIn('self.Control1.'+method+'(',snippets)
    def test_theme_requirements_and_legacy_theme_migration(self):
        p=new_project();p['theme']='darkly';self.assertEqual(theme_config(p),{'provider':'ttkbootstrap','name':'darkly'});self.assertIn('ttkbootstrap>=1.10,<2',requirements(p))
        p['theme_config']={'provider':'sv-ttk','mode':'dark'};self.assertNotIn('ttkbootstrap>=1.10,<2',requirements(p));self.assertIn('sv-ttk>=2,<3',requirements(p))
        source=generate(p);self.assertIn('def apply_project_theme',source);self.assertIn("'provider': 'sv-ttk'",source)
    def test_theme_path_validation(self):
        for path in ['/tmp/azure.tcl','../azure.tcl','C:/azure.tcl','.git/theme.tcl','theme.py']:
            with self.assertRaises(ValueError):theme_config({'theme_config':{'provider':'azure','file':path}})
    def test_deploy_copies_theme_assets_and_collection_flags(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'theme').mkdir();(root/'theme/azure.tcl').write_text('# test theme');(root/'theme/image.png').write_bytes(b'placeholder')
            path=root/'project.vtk.json';path.write_text('{}');p=new_project();p['files']=['theme'];p['theme_config']={'provider':'azure','file':'theme/azure.tcl','mode':'light'};p['appearance_mode']='Dark'
            target=export_deployment(p,path,root/'deploy','ThemeDemo','1.0');self.assertTrue((target/'src/theme/image.png').is_file());self.assertIn('--collect-all=customtkinter',json.loads((target/'deploy.json').read_text())['packaging_flags'])
            p['files']=[]
            with self.assertRaises(ValueError):export_deployment(p,path,root/'deploy','OtherDemo','1.0')
    def test_theme_api_calls(self):
        root=Mock();style=Mock()
        with patch.dict(sys.modules,{'ttkbootstrap':types.SimpleNamespace(Style=style)}):apply_project_theme(root,{'provider':'ttkbootstrap','name':'litera'})
        style.assert_called_once_with(theme='litera')
        sun=Mock()
        with patch.dict(sys.modules,{'sv_ttk':sun}):apply_project_theme(root,{'provider':'sv-ttk','mode':'dark'})
        sun.set_theme.assert_called_once_with('dark')
        apply_project_theme(root,{'provider':'azure','file':'themes/azure.tcl','mode':'dark'});self.assertIn(unittest.mock.call('set_theme','dark'),root.tk.call.call_args_list)
    def test_sheet_and_map_adapter_forwarding_and_events(self):
        sheet=types.SimpleNamespace(sheet=Mock());integration_runtime.SheetView.set_cell(sheet,0,1,'value');sheet.sheet.set_cell_data.assert_called_once_with(0,1,'value')
        panel=types.SimpleNamespace(map=Mock(),event_generate=Mock(),selected_position=None)
        integration_runtime.MapView._click(panel,(1,2));self.assertEqual(panel.selected_position,(1,2));panel.event_generate.assert_called_once_with('<<MapClicked>>',when='tail')
    @unittest.skipUnless(all(importlib.util.find_spec(name) for name in ('customtkinter','ttkbootstrap','ttkthemes','sv_ttk','Pmw','tksheet','tkintermapview')),'Optional packages not installed')
    def test_actual_package_imports_in_selected_python(self):
        for name in ('CustomTkinter','ttkbootstrap','ttkthemes','sv-ttk','Pmw','tksheet','tkintermapview'):
            self.assertEqual(check_library(sys.executable,name)['state'],'installed',name)
    @unittest.skipUnless(importlib.util.find_spec('jedi') and importlib.util.find_spec('customtkinter'),'Optional analysis packages not installed')
    def test_jedi_resolves_new_adapter_and_customtkinter_members(self):
        from semantic_engine import SemanticEngine
        engine=SemanticEngine(cache_directory=self.enterContext(tempfile.TemporaryDirectory()))
        for kind,body,expected in [('Sheet','self.Control1.set_',{'set_cell','set_data'}),('CTkButton','self.Control1.',{'configure','invoke'})]:
            p=new_project();p['forms'][0]['widgets']=[widget('Control1',kind,props=BUILTINS[kind]['defaults'])]
            result=engine.analyze({'project':p,'body':body,'cursor':'1.'+str(len(body)),'cwd':str(Path(__file__).resolve().parents[1])})
            self.assertTrue(expected.issubset({item['name'] for item in result['items']}),kind)
    def test_family_grouping(self):
        p=new_project();self.assertEqual(component_family('TButton',p),'tkinter.ttk');self.assertEqual(component_family('CTkFrame',p),'CustomTkinter');self.assertEqual(component_family('Sheet',p),'tksheet')
