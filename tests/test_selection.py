import unittest
from multi_selection import selected_roots,moved_geometry,layout_geometry
class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.a=dict(name='A',kind='Frame',x=10,y=20,width=100,height=50)
        self.b=dict(name='B',kind='Button',x=150,y=30,width=50,height=30)
        self.child=dict(name='Child',kind='Label',parent='A',x=5,y=5,width=20,height=20)
        self.form={'name':'Form1','widgets':[self.a,self.b,self.child]}
    def test_move_parent_and_child_only_once(self):
        roots=selected_roots(self.form,[self.a,self.b,self.child]);self.assertEqual([w['name'] for w in roots],['A','B'])
        changed=moved_geometry(roots,-50,-50);self.assertEqual(changed['A'],{'x':0,'y':0});self.assertEqual(changed['B'],{'x':140,'y':10})
    def test_layout_and_container_isolation(self):
        self.assertEqual(layout_geometry(self.form,[self.a,self.b],self.a,'width')['B'],{'width':100})
        self.assertEqual(layout_geometry(self.form,[self.a,self.b],self.b,'left')['A'],{'x':150})
        with self.assertRaises(ValueError):layout_geometry(self.form,[self.a,self.child],self.a,'width')
    def test_even_distribution(self):
        c={**self.b,'name':'C','x':300}
        result=layout_geometry(self.form,[self.a,self.b,c],self.a,'horizontal');self.assertEqual(result['B']['x']-110,300-result['B']['x']-50)
