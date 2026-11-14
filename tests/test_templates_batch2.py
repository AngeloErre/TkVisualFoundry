from collections import Counter
import random
import types
import unittest
from unittest.mock import Mock
from project_templates import instantiate

class StarterBatchTwoTests(unittest.TestCase):
    def ns(self,key):
        ns={'messagebox':Mock(),'filedialog':Mock()};exec(instantiate(key)['imports'],ns);return ns
    def odd_app(self):
        rng=Mock();rng.choice.return_value=('A','B');rng.randrange.return_value=2
        return types.SimpleNamespace(odd_rng=rng,PromptLabel=Mock(),FeedbackLabel=Mock(),ScoreLabel=Mock(),**{'Card'+str(i):Mock() for i in range(9)})
    def memory_app(self):return types.SimpleNamespace(root=Mock(),StatusLabel=Mock(),**{'Card'+str(i):Mock() for i in range(16)})
    def puzzle_app(self):return types.SimpleNamespace(StatusLabel=Mock(),**{'Tile'+str(i):Mock() for i in range(16)})
    def paint_app(self,tool='Brush'):
        canvas=Mock();canvas.create_line.return_value=11;canvas.create_rectangle.return_value=12;canvas.create_oval.return_value=13
        return types.SimpleNamespace(Form1=Mock(),PaintCanvas=canvas,ToolChoice=Mock(get=lambda:tool),StrokeScale=Mock(get=lambda:4),StatusLabel=Mock(),paint_color='red',paint_last=None,paint_shape=None)
    def test_odd_correct_answers_finish_and_ignore_extra_clicks(self):
        ns=self.ns('odd');app=self.odd_app();ns['odd_reset'](app)
        for _ in range(5):ns['odd_choose'](app,2)
        self.assertEqual((app.odd_score,app.odd_round),(5,5));app.Card0.configure.assert_called_with(state='disabled')
        ns['odd_choose'](app,2);self.assertEqual(app.odd_score,5);ns['odd_reset'](app);self.assertEqual(app.odd_round,0)
    def test_odd_incorrect_answer_advances_without_points(self):
        ns=self.ns('odd');app=self.odd_app();ns['odd_reset'](app);ns['odd_choose'](app,1);self.assertEqual((app.odd_score,app.odd_round),(0,1))
    def test_memory_deck_contains_exactly_eight_pairs(self):
        ns=self.ns('memory');app=self.memory_app();ns['memory_reset'](app)
        self.assertEqual(Counter(app.memory_deck),Counter({key:2 for key in 'ABCDEFGH'}));self.assertEqual(app.memory_moves,0)
    def test_memory_duplicate_and_matching_cards_count_once(self):
        ns=self.ns('memory');app=self.memory_app();ns['memory_reset'](app);app.memory_deck=list('AABBCCDDEEFFGGHH')
        ns['memory_choose'](app,0);ns['memory_choose'](app,0);self.assertEqual(app.memory_open,[0]);ns['memory_choose'](app,1);self.assertEqual(app.memory_matched,{0,1});self.assertEqual(app.memory_moves,1)
        ns['memory_choose'](app,0);self.assertEqual(app.memory_open,[])
    def test_memory_mismatch_lock_and_restart_reject_stale_timer(self):
        ns=self.ns('memory');app=self.memory_app();app.root.after.return_value='timer';ns['memory_reset'](app);app.memory_deck=list('ABCDEFGHABCDEFGH')
        ns['memory_choose'](app,0);ns['memory_choose'](app,1);self.assertTrue(app.memory_locked);callback=app.root.after.call_args.args[1]
        ns['memory_choose'](app,2);self.assertEqual(app.memory_open,[0,1]);callback();self.assertFalse(app.memory_locked);self.assertEqual(app.memory_open,[])
        ns['memory_choose'](app,0);ns['memory_choose'](app,1);old_callback=app.root.after.call_args.args[1];ns['memory_reset'](app);app.root.after_cancel.assert_called_with('timer')
        app.memory_open=[3];old_callback();self.assertEqual(app.memory_open,[3]);self.assertFalse(app.memory_locked)
    def test_memory_all_pairs_complete(self):
        ns=self.ns('memory');app=self.memory_app();ns['memory_reset'](app);app.memory_deck=list('AABBCCDDEEFFGGHH')
        for index in range(16):ns['memory_choose'](app,index)
        self.assertEqual(len(app.memory_matched),16);self.assertEqual(app.memory_moves,8);self.assertIn('Complete!',app.StatusLabel.configure.call_args.kwargs['text'])
    def test_sliding_puzzle_shuffles_are_solvable_and_not_already_solved(self):
        ns=self.ns('puzzle15')
        for seed in range(100):
            board=ns['puzzle_new_board'](random.Random(seed));self.assertEqual(sorted(board),list(range(16)));self.assertNotEqual(board,list(range(1,16))+[0])
            values=[v for v in board if v];inversions=sum(a>b for i,a in enumerate(values) for b in values[i+1:]);blank_from_bottom=4-board.index(0)//4
            self.assertEqual((inversions+blank_from_bottom)%2,1)
    def test_sliding_puzzle_rejects_illegal_move_and_detects_win(self):
        ns=self.ns('puzzle15');app=self.puzzle_app();app.puzzle_board=list(range(1,15))+[0,15];app.puzzle_moves=0;before=app.puzzle_board[:]
        ns['puzzle_choose'](app,0);self.assertEqual(app.puzzle_board,before);self.assertEqual(app.puzzle_moves,0)
        ns['puzzle_choose'](app,15);self.assertEqual(app.puzzle_board,list(range(1,16))+[0]);self.assertEqual(app.puzzle_moves,1);self.assertIn('Solved!',app.StatusLabel.configure.call_args.kwargs['text'])
        ns['puzzle_choose'](app,14);self.assertEqual(app.puzzle_moves,1)
    def test_paint_brush_stroke_and_end_guard(self):
        ns=self.ns('paint');app=self.paint_app();ns['paint_start'](app,types.SimpleNamespace(x=10,y=20));ns['paint_drag'](app,types.SimpleNamespace(x=30,y=40))
        app.PaintCanvas.create_line.assert_called_with(10,20,30,40,fill='red',width=4,capstyle='round')
        ns['paint_end'](app,types.SimpleNamespace(x=35,y=45));self.assertIsNone(app.paint_last);count=app.PaintCanvas.create_line.call_count;ns['paint_drag'](app,types.SimpleNamespace(x=40,y=50));self.assertEqual(app.PaintCanvas.create_line.call_count,count)
    def test_paint_shapes_and_white_eraser(self):
        ns=self.ns('paint')
        for tool,shape in [('Line',11),('Rectangle',12),('Oval',13)]:
            app=self.paint_app(tool);ns['paint_start'](app,types.SimpleNamespace(x=1,y=2));ns['paint_end'](app,types.SimpleNamespace(x=3,y=4));app.PaintCanvas.coords.assert_called_with(shape,1,2,3,4)
        app=self.paint_app('Eraser');ns['paint_start'](app,types.SimpleNamespace(x=1,y=2));self.assertEqual(app.PaintCanvas.create_oval.call_args.kwargs['fill'],'white')
    def test_paint_clear_confirmation_and_export_cancellation(self):
        ns=self.ns('paint');app=self.paint_app();ns['messagebox'].askyesno.return_value=False;ns['paint_clear'](app);app.PaintCanvas.delete.assert_not_called()
        ns['messagebox'].askyesno.return_value=True;ns['paint_clear'](app);app.PaintCanvas.delete.assert_called_with('all')
        ns['filedialog'].asksaveasfilename.return_value='';ns['paint_export'](app);app.PaintCanvas.postscript.assert_not_called()
        ns['filedialog'].asksaveasfilename.return_value='/tmp/example.eps';ns['paint_export'](app);app.PaintCanvas.postscript.assert_called_once_with(file='/tmp/example.eps',colormode='color')
