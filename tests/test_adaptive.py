import unittest
import types
from unittest.mock import Mock
from adaptive_layout import anchored_geometry,_vts_install_anchors
from core import new_project,validate,generate
class AnchorTests(unittest.TestCase):
    def setUp(self):self.original={'x':100,'y':50,'width':100,'height':30}
    def test_right_bottom_preserve_distance(self):
        result=anchored_geometry(self.original,(400,300),(600,450),{'anchors':['right','bottom']})
        self.assertEqual(result,{'x':300,'y':200,'width':100,'height':30})
    def test_stretch_and_minimum_dimensions(self):
        spec={'anchors':['left','right','top','bottom'],'min_width':40,'min_height':20}
        self.assertEqual(anchored_geometry(self.original,(400,300),(600,450),spec)['width'],300)
        result=anchored_geometry(self.original,(400,300),(100,100),spec)
        self.assertEqual((result['width'],result['height']),(40,20))
    def test_center_and_fixed_defaults(self):
        self.assertEqual(anchored_geometry(self.original,(400,300),(600,400),{'anchors':[]})['x'],200)
        self.assertEqual(anchored_geometry(self.original,(400,300),(600,400),{}),self.original)
    def test_generator_embeds_runtime_and_rejects_unsupported_parent(self):
        p=new_project();frame=dict(name='Frame1',kind='Frame',x=0,y=0,width=300,height=200,props={},events={})
        child=dict(name='Button1',kind='Button',parent='Frame1',x=10,y=10,width=100,height=30,props={},events={},layout={'anchors':['left','right','top']})
        p['forms'][0]['widgets']=[frame,child];p['imports']='EDGES = {"user edges"}\nPARENTS = {"user parents"}';source=generate(p)
        scope={'__name__':'test_export'};exec(source,scope);self.assertEqual(scope['EDGES'],{'user edges'});self.assertEqual(scope['PARENTS'],{'user parents'})
        self.assertIn('_vts_install_anchors(self.Frame1',source);self.assertNotIn('from adaptive_layout import',source);compile(source,'adaptive','exec')
        child['layout']['anchors']=['wrong']
        with self.assertRaises(ValueError):validate(p)
        child['layout']['anchors']=['left'];frame['kind']='CTkFrame'
        with self.assertRaises(ValueError):validate(p)
    def test_configure_events_are_coalesced_and_keep_existing_bindings(self):
        pending=[];bindings={};widget=Mock();widget.winfo_exists.return_value=True
        parent=types.SimpleNamespace(winfo_exists=lambda:True,winfo_width=lambda:600,winfo_height=lambda:400,after_idle=lambda cb:pending.append(cb) or 'timer',after_cancel=Mock())
        parent.bind=lambda event,callback,add:bindings.__setitem__(event,(callback,add))
        _vts_install_anchors(parent,[(widget,self.original,{'anchors':['right','bottom']})],(400,300))
        self.assertEqual(bindings['<Configure>'][1],'+');pending.pop()()
        self.assertEqual(widget.place_configure.call_args.kwargs['x'],300)
        bindings['<Configure>'][0](types.SimpleNamespace(widget=object()));self.assertEqual(pending,[])
        bindings['<Configure>'][0](types.SimpleNamespace(widget=parent));bindings['<Configure>'][0](types.SimpleNamespace(widget=parent));self.assertEqual(len(pending),1)
