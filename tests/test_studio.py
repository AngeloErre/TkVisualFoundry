import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core import new_project, generate, load, validate, KINDS

# Probe in a child: on GUI-less macOS, Tk may abort instead of raising TclError.
probe = subprocess.run([sys.executable, '-c', 'import tkinter; r=tkinter.Tk(); r.withdraw(); r.destroy()'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
GUI = probe.returncode == 0

class CoreTests(unittest.TestCase):
    def test_generated_source(self):
        p=new_project()
        for i,k in enumerate(KINDS):
            p['forms'][0]['widgets'].append({'name':k+'1','kind':k,'x':10,'y':i*10,'width':100,'height':30,'props':{},'events':{'Click':'print("clicked")'}})
        source=generate(p)
        compile(source,'test.py','exec')
        self.assertEqual(source,generate(copy.deepcopy(p)))
        self.assertIn('def event_Button1_Click',source)
        self.assertIn("self.Button1.bind('<Button-1>'",source)
        self.assertIn('self.startup()',source)

    @unittest.skipUnless(GUI, 'Sessione grafica macOS non disponibile')
    def test_source_and_callbacks(self):
        p=new_project(); f=p['forms'][0]
        f['widgets']=[{'name':'Button1','kind':'Button','x':10,'y':20,'width':100,'height':30,'props':{'text':'Clicca'},'events':{'Click':'self.Button1.configure(text="OK")'}}]
        p['forms'].append({'name':'Form2','title':'Seconda','width':300,'height':200,'bg':'white','widgets':[],'events':{'Load':'self.Form2.title("Caricata")'}})
        scope={'__name__':'test'}; exec(generate(p),scope)
        a=scope['Application'](); a.root.update(); a.event_Button1_Click(); self.assertEqual(a.Button1['text'],'OK'); self.assertEqual(a.Form2.title(),'Caricata'); a.show('Form2'); a.root.update(); self.assertEqual(a.Form2.state(),'normal'); a.root.destroy()
    def test_invalid_and_incomplete_roundtrip(self):
        p=new_project(); p['forms'][0]['events']['Load']='if'
        with tempfile.TemporaryDirectory() as d:
            file=Path(d)/'test.json'; file.write_text(json.dumps(p)); self.assertEqual(load(file),p)
        with self.assertRaises(SyntaxError):generate(p)
        p=new_project(); p['forms'][0]['name']='class'
        with self.assertRaises(ValueError):generate(p)
    def test_unique_names(self):
        p=new_project(); p['forms'].append(copy.deepcopy(p['forms'][0]))
        with self.assertRaises(ValueError):validate(p)
    @unittest.skipUnless(GUI, "Sessione grafica macOS non disponibile")
    def test_standalone_subprocess(self):
        p=new_project(); p['startup']='self.Form1.deiconify()\nself.root.after(100, self.root.destroy)'
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'app.py'; path.write_text(generate(p)); result=subprocess.run([sys.executable,str(path)],capture_output=True,timeout=15)
            self.assertEqual(result.returncode,0,result.stderr.decode())
    @unittest.skipUnless(GUI, "Sessione grafica macOS non disponibile")
    def test_debugger_breakpoint(self):
        p=new_project(); p['startup']='print("DEBUG_OK")\nself.root.after(50, self.root.destroy)'
        source=generate(p); line=source.splitlines().index('        print("DEBUG_OK")')+1
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'app.py'; path.write_text(source)
            result=subprocess.run([sys.executable,'-m','pdb','-c',f'break {line}',str(path)],input='continue\np self.Form1.title()\ncontinue\nquit\n',text=True,capture_output=True,timeout=15)
            self.assertIn("'Form1'",result.stdout); self.assertIn('DEBUG_OK',result.stdout)

@unittest.skipUnless(GUI, "Sessione grafica macOS non disponibile")
class UITests(unittest.TestCase):
    def setUp(self):
        from studio import Studio
        self.app=Studio(); self.app.withdraw(); self.app.update()
    def tearDown(self):
        self.app.temp.cleanup(); self.app.destroy()
    def test_designer_properties_event_undo(self):
        a=self.app
        from unittest.mock import patch
        a.palette.selection_set(0)
        with patch('studio.simpledialog.askstring',return_value='Button1'):a.add_widget()
        a.propvars['text'].set('Premi'); a.propvars['width'].set('180'); a.apply_props(); a.update()
        self.assertEqual(a.selected['width'],180)
        a.edit_event(); a.code.delete('1.0','end'); a.code.insert('1.0','self.Button1.configure(text="Fatto")'); a.commit_code()
        self.assertIn('Fatto',generate(a.project)); a.undo(); self.assertNotIn('Fatto',generate(a.project)); a.redo(); self.assertIn('Fatto',generate(a.project))
    def test_every_widget_and_generation(self):
        a=self.app
        from unittest.mock import patch
        for i,kind in enumerate(KINDS):
            a.palette.selection_clear(0,'end'); a.palette.selection_set(i)
            with patch('studio.simpledialog.askstring',return_value=kind+'1'):a.add_widget()
        scope={'__name__':'test'}; exec(generate(a.project),scope); runtime=scope['Application'](); runtime.root.update()
        for kind in KINDS:self.assertTrue(getattr(runtime,kind+'1').winfo_exists())
        runtime.root.destroy()

if __name__=='__main__':unittest.main(verbosity=2)

class MockRuntimeTests(unittest.TestCase):
    def test_generated_multiform_event_wiring_without_display(self):
        import types
        from unittest.mock import patch
        class Widget:
            def __init__(self,*args,**kwargs):self.options=kwargs; self.bindings={}; self.callbacks=[]; self.visible=False
            def withdraw(self):self.visible=False
            def deiconify(self):self.visible=True
            def title(self,*value):
                if value:self.options['title']=value[0]
                return self.options.get('title')
            def geometry(self,v):self.options['geometry']=v
            def configure(self,**kwargs):self.options.update(kwargs)
            def place(self,**kwargs):self.options['place']=kwargs
            def protocol(self,*args):pass
            def bind(self,event,callback,**kwargs):self.bindings[event]=callback
            def after_idle(self,callback):self.callbacks.append(callback)
            def destroy(self):pass
        fake=types.ModuleType('tkinter'); fake.Tk=Widget;fake.Toplevel=Widget
        for kind in KINDS:setattr(fake,kind,Widget)
        fake.ttk=types.SimpleNamespace(Combobox=Widget,Progressbar=Widget)
        fake.messagebox=types.SimpleNamespace(showerror=lambda *a:None); fake.filedialog=types.SimpleNamespace();fake.simpledialog=types.SimpleNamespace();fake.colorchooser=types.SimpleNamespace();fake.font=types.SimpleNamespace()
        p=new_project()
        for i,kind in enumerate(KINDS):p['forms'][0]['widgets'].append({'name':kind+'1','kind':kind,'x':i,'y':0,'width':100,'height':30,'props':{},'events':{'Click':'self.'+kind+'1.configure(text="OK")','Load':'self.'+kind+'1.configure(state="normal")'}})
        with patch.dict(sys.modules,{'tkinter':fake}):
            scope={'__name__':'test'}; exec(generate(p),scope); app=scope['Application']()
        self.assertTrue(app.Form1.visible)
        for callback in app.root.callbacks:callback()
        for kind in KINDS:
            obj=getattr(app,kind+'1'); obj.bindings['<Button-1>'](); self.assertEqual(obj.options['text'],'OK'); self.assertEqual(obj.options['state'],'normal')
