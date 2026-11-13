import types
import unittest
from component_palette import LayoutMixin
class Pane:
    def __init__(self,width=1,height=1,positions=None):self.width=width;self.height=height;self.positions=positions or [0,0]
    def winfo_width(self):return self.width
    def winfo_height(self):return self.height
    def sashpos(self,index,*args):
        if args:self.positions[index]=args[0]
        return self.positions[index]
class InitialLayoutTests(unittest.TestCase):
    def test_initial_unmapped_geometry_is_retried_after_mapping(self):
        app=types.SimpleNamespace(main_panes=Pane(),right_panes=Pane(),layout_initialized=False,right_layout_initialized=False,layout_guard_timer=None)
        LayoutMixin.ensure_layout_visible(app);self.assertFalse(app.layout_initialized);self.assertFalse(app.right_layout_initialized)
        app.main_panes.width=1400;app.right_panes.height=760
        LayoutMixin.ensure_layout_visible(app)
        self.assertEqual(app.main_panes.positions,[205,1060]);self.assertEqual(app.right_panes.positions[0],260)
        self.assertTrue(app.layout_initialized);self.assertTrue(app.right_layout_initialized)
    def test_collapsed_panes_recover_but_valid_custom_sizes_remain(self):
        app=types.SimpleNamespace(main_panes=Pane(1050,positions=[205,1040]),right_panes=Pane(height=400,positions=[2]),layout_initialized=True,right_layout_initialized=True,layout_guard_timer=None)
        LayoutMixin.ensure_layout_visible(app)
        self.assertEqual(app.main_panes.positions[1],750);self.assertEqual(app.right_panes.positions[0],150)
        app.main_panes.positions=[190,700];app.right_panes.positions=[200]
        LayoutMixin.ensure_layout_visible(app)
        self.assertEqual(app.main_panes.positions,[190,700]);self.assertEqual(app.right_panes.positions,[200])
