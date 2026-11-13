"""Geometry and contrast checks that do not require a desktop session."""
import unittest
from vb6_ui import resize_handle,resized_geometry,CLASSIC
from ux_theme import editor_palette

class ClassicInteractionTests(unittest.TestCase):
    def test_handles_resolve_all_edges(self):
        points={'nw':(20,30),'n':(70,30),'ne':(120,30),'w':(20,60),'e':(120,60),'sw':(20,90),'s':(70,90),'se':(120,90)}
        for expected,(x,y) in points.items():self.assertEqual(resize_handle(20,30,100,60,x,y),expected)
        self.assertEqual(resize_handle(20,30,100,60,70,60),'')
    def test_resize_preserves_opposite_edges(self):
        original={'x':20,'y':30,'width':100,'height':60}
        result=resized_geometry(original,'nw',15,10,5)
        self.assertEqual(result,{'x':35,'y':40,'width':85,'height':50})
        self.assertEqual(original['width'],100)
    def test_resize_clamps_size_and_position(self):
        original={'x':20,'y':30,'width':100,'height':60}
        for handle in ('nw','n','ne','w','e','sw','s','se'):
            for delta in (-500,500):
                result=resized_geometry(original,handle,delta,delta,10)
                self.assertGreaterEqual(result['width'],10);self.assertGreaterEqual(result['height'],10)
                self.assertGreaterEqual(result['x'],0);self.assertGreaterEqual(result['y'],0)
    def test_editor_colors_follow_light_and_dark_surfaces(self):
        self.assertNotEqual(editor_palette('#ffffff'),editor_palette('#111827'))
        self.assertEqual(set(editor_palette(CLASSIC['editor_bg'])),{'kw','str','num','comment'})
