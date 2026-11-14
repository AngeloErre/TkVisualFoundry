"""Offline final starter regression tests; no live API, audio output or GUI."""
import json
import math
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import Mock, patch
from components import requirements
from core import generate
from project_templates import instantiate

GAMES=('invaders','chase','platformer','blocks','neural')
class FinalStarterTests(unittest.TestCase):
    def ns(self,key):
        ns={'messagebox':Mock(),'filedialog':Mock()};exec(instantiate(key)['imports'],ns);return ns
    def app(self,ns):
        app=types.SimpleNamespace(root=Mock(),Board=Mock(),Status=Mock(),timer=None,generation=0,running=False)
        ns['game_reset'](app);return app
    def test_all_game_timer_pause_reset_and_stale_callbacks(self):
        for key in GAMES:
            ns=self.ns(key);app=self.app(ns);ns['game_start'](app);old=app.generation
            self.assertTrue(app.running);self.assertIsNotNone(app.timer)
            ns['game_reset'](app);app.root.after_cancel.assert_called();app.root.after.reset_mock()
            ns['game_tick'](app,old);app.root.after.assert_not_called();self.assertFalse(app.running)
            ns['game_close'](app);app.root.destroy.assert_called_once()
    def test_game_start_is_idempotent_and_finished_is_guarded(self):
        for key in GAMES:
            ns=self.ns(key);app=self.app(ns);ns['game_start'](app);generation=app.generation
            ns['game_start'](app);self.assertEqual(app.generation,generation)
            ns['game_pause'](app);app.over=True;ns['game_start'](app);self.assertFalse(app.running)
    def test_invader_shots_score_and_clear(self):
        ns=self.ns('invaders');app=self.app(ns);app.running=True;app.enemies=[[100,100]];app.bullets=[[103,120]]
        ns['game_step'](app);self.assertEqual(app.score,10);self.assertTrue(app.over);self.assertFalse(app.running)
    def test_invader_bounds_bullet_limit_and_loss(self):
        ns=self.ns('invaders');app=self.app(ns);app.running=True
        ns['invader_move'](app,-10000);self.assertEqual(app.player,15)
        for _ in range(8):ns['invader_shoot'](app)
        self.assertEqual(len(app.bullets),5);app.enemies=[[20,466]];ns['game_step'](app);self.assertTrue(app.over)
    def test_chase_map_connected_and_pursuit_legal(self):
        ns=self.ns('chase');start=(1,1);seen={start};todo=[start]
        while todo:
            for n in ns['maze_neighbors'](todo.pop()):
                if n not in seen:seen.add(n);todo.append(n)
        dots={(x,y) for y,row in enumerate(ns['MAZE']) for x,c in enumerate(row) if c=='.'}
        self.assertEqual(seen,dots);self.assertIn(ns['chase_next']((13,9),(1,1)),ns['maze_neighbors']((13,9)))
    def test_chase_walls_collection_win_and_collision(self):
        ns=self.ns('chase');app=self.app(ns);app.running=True;app.intent=(-1,0);app.frames=2
        ns['game_step'](app);self.assertEqual(app.player,(1,1))
        app.intent=(1,0);app.dots={(2,1)};app.frames=2;ns['game_step'](app);self.assertTrue(app.over);self.assertEqual(app.score,1)
        ns['game_reset'](app);app.running=True;app.enemy=app.player;app.frames=2;ns['game_step'](app);self.assertTrue(app.over)
    def test_platform_jump_landing_and_no_double_jump(self):
        ns=self.ns('platformer');app=self.app(ns);app.running=True;ns['platform_jump'](app);v=app.vy
        ns['platform_jump'](app);self.assertEqual(app.vy,v)
        app.x=220;app.y=390;app.vy=12;ns['game_step'](app);self.assertEqual(app.y,400);self.assertTrue(app.grounded)
    def test_platform_fall_goal_and_focus_release(self):
        ns=self.ns('platformer');app=self.app(ns);app.running=True;app.y=550;ns['game_step'](app);self.assertTrue(app.over)
        ns['game_reset'](app);app.running=True;app.x=560;app.y=240;ns['game_step'](app);self.assertTrue(app.won)
        self.assertIn('<FocusOut>',instantiate('platformer')['startup'])
    def test_blocks_clear_and_bounds(self):
        ns=self.ns('blocks');board=[[0]*10 for _ in range(18)]+[[1]*10,[1]*10]
        cleared,count=ns['blocks_clear'](board);self.assertEqual(count,2);self.assertEqual(cleared,[[0]*10 for _ in range(20)])
        self.assertFalse(ns['blocks_valid'](cleared,[(0,0)],-1,0));self.assertFalse(ns['blocks_valid'](cleared,[(0,0)],0,20))
    def test_all_block_rotations_return_to_original(self):
        ns=self.ns('blocks');app=self.app(ns);app.running=True
        for i,piece in enumerate(ns['PIECES']):
            app.cells=[[0]*10 for _ in range(20)];app.piece=list(piece);app.piece_size=4 if i==0 else 2 if i==1 else 3;app.bx=3;app.by=3
            for _ in range(4):self.assertTrue(ns['blocks_move'](app,rotate=True))
            self.assertEqual(set(app.piece),set(piece))
    def test_blocks_hard_drop_and_spawn_collision(self):
        ns=self.ns('blocks');app=self.app(ns);app.running=True;ns['blocks_drop'](app)
        self.assertEqual(sum(map(sum,app.cells)),4);app.cells=[[1]*10 for _ in range(20)];ns['blocks_spawn'](app);self.assertTrue(app.over);self.assertFalse(app.running)
    def test_network_is_deterministic_and_training_reduces_error(self):
        ns=self.ns('neural');a=ns['neural_create']();b=ns['neural_create']();self.assertEqual(a,b)
        samples=[[x/5,y/5,z/5] for x in range(-4,5,2) for y in (-3,3) for z in (-2,2)]
        def loss():return sum((ns['neural_forward'](a,x)[1]-ns['neural_target'](x))**2 for x in samples)/len(samples)
        before=loss();ns['neural_train'](a);self.assertLess(loss(),before/10)
        self.assertTrue(all(-1<=ns['neural_forward'](a,x)[1]<=1 for x in samples))
    def test_neural_steering_and_offroad_stop(self):
        ns=self.ns('neural');app=self.app(ns);app.running=True;ns['game_step'](app);self.assertEqual(app.distance,4)
        app.car=1000;ns['game_step'](app);self.assertTrue(app.over);self.assertFalse(app.running)
    def test_study_send_prompt_validation_and_no_key_in_project(self):
        ns=self.ns('study');app=types.SimpleNamespace(Topic=Mock(get=lambda:'Fractions'),Tutor=Mock(),Form1=Mock())
        ns['study_send'](app);self.assertIn('Fractions',app.Tutor.send.call_args.args[0]);self.assertIn('three practice questions',app.Tutor.send.call_args.args[0])
        app.Tutor.reset_mock();app.Topic.get=lambda:' ';ns['study_send'](app);app.Tutor.send.assert_not_called()
        self.assertNotIn('.send(',instantiate('study')['startup']);self.assertIn('OPENAI_API_KEY',json.dumps(instantiate('study')))
    def test_sound_assign_play_unassigned_and_cancel(self):
        ns=self.ns('soundboard');app=types.SimpleNamespace(sounds={},Slot=Mock(get=lambda:'2'),Pad2=Mock(),Player=Mock(),Form1=Mock())
        ns['sound_play'](app,2);app.Player.play.assert_not_called()
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'sample.wav';path.write_bytes(b'RIFF')
            ns['filedialog'].askopenfilename.return_value=str(path);ns['sound_assign'](app);ns['sound_play'](app,2)
            self.assertEqual(app.Player.source,str(path));app.Player.play.assert_called_once()
            ns['filedialog'].askopenfilename.return_value='';ns['sound_assign'](app);self.assertEqual(len(app.sounds),1)
    def test_optional_dependencies_declared_and_lazy(self):
        self.assertEqual(requirements(instantiate('soundboard')),['pygame-ce>=2.5.8'])
        self.assertIn('openai', ' '.join(requirements(instantiate('study'))))
        self.assertEqual(len(requirements(instantiate('codes'))),4)
        for key in ('codes','soundboard','study'):
            source=instantiate(key)['imports']
            original=__import__
            def checked(name,*args,**kwargs):
                if name in ('qrcode','barcode','zxingcpp','pygame','openai'):
                    raise AssertionError('Optional package imported eagerly')
                return original(name,*args,**kwargs)
            with patch('builtins.__import__',side_effect=checked):
                exec(source,{'messagebox':Mock(),'filedialog':Mock()})
    def test_code_validation_cancellation_and_errors(self):
        ns=self.ns('codes')
        for value,kind in [('', 'QR'),('x'*1001,'QR'),('caffè','Code128')]:
            with self.assertRaises(ValueError):ns['code_generate'](value,kind,'unused.png')
        app=types.SimpleNamespace(Form1=Mock(),Result=Mock(),Value=Mock(get=lambda:'hello'),Format=Mock(get=lambda:'QR'))
        ns['filedialog'].asksaveasfilename.return_value='';ns['code_save'](app);app.Result.insert.assert_not_called()
        ns['filedialog'].askopenfilename.return_value='/nonexistent/image.png';ns['code_open'](app);ns['messagebox'].showerror.assert_called_once()
    def test_actual_qr_and_code128_roundtrips(self):
        try:import qrcode,barcode,zxingcpp
        except ImportError:self.skipTest('Install optional QR/barcode packages for real round trips')
        ns=self.ns('codes')
        with tempfile.TemporaryDirectory() as d:
            for kind,value in [('QR','Hello world 123'),('Code128','ITEM-12345')]:
                path=Path(d)/(kind+'.png');ns['code_generate'](value,kind,path);self.assertIn(value,ns['code_read'](path))
    def test_generated_combobox_options_have_no_invalid_value(self):
        for key in ('codes','soundboard'):
            p=instantiate(key)
            for w in p['forms'][0]['widgets']:
                if w['kind']=='Combobox':self.assertNotIn('value',w['props'])
            self.assertIn('.set(',p['startup']);compile(generate(p),key,'exec')
if __name__=='__main__':unittest.main()
