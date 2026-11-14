from collections import deque
import copy
import datetime
import json
from pathlib import Path
import random
import struct
import tempfile
import types
import unittest
from unittest.mock import Mock,patch
from project_templates import instantiate

class StarterBatchSixTests(unittest.TestCase):
    def ns(self,key):
        ns={'messagebox':Mock(),'filedialog':Mock()};exec(instantiate(key)['imports'],ns);return ns
    def mines_app(self):return types.SimpleNamespace(StatusLabel=Mock(),**{'Cell'+str(i):Mock() for i in range(81)})
    def test_mine_placement_first_neighborhood_safe(self):
        ns=self.ns('mines')
        for first in (0,4,40,80):
            for seed in range(20):
                cells=ns['mines_place'](first,random.Random(seed));self.assertEqual(len(cells),10);self.assertFalse(cells.intersection({first}|set(ns['mines_neighbors'](first))))
        self.assertEqual(set(ns['mines_neighbors'](0)),{1,9,10})
    def test_flags_limit_block_reveal_and_reset(self):
        ns=self.ns('mines');app=self.mines_app();ns['mines_reset'](app)
        for index in range(11):self.assertEqual(ns['mines_flag'](app,index),'break')
        self.assertEqual(len(app.mine_flags),10);ns['mines_reveal'](app,0);self.assertIsNone(app.mine_cells);ns['mines_flag'](app,0);ns['mines_reveal'](app,0);self.assertIn(0,app.mine_revealed)
        ns['mines_reset'](app);self.assertIsNone(app.mine_cells);self.assertEqual(app.mine_flags,set());self.assertFalse(app.mine_done)
    def test_flood_fill_and_safe_cell_win(self):
        ns=self.ns('mines');app=self.mines_app();ns['mines_reset'](app);app.mine_cells=set(range(10))
        ns['mines_reveal'](app,80);self.assertGreater(len(app.mine_revealed),1)
        for index in range(81):
            if index not in app.mine_cells:ns['mines_reveal'](app,index)
        self.assertTrue(app.mine_done);self.assertEqual(len(app.mine_revealed),71);self.assertIn('Won!',app.StatusLabel.configure.call_args.kwargs['text'])
        ns['mines_reveal'](app,0);self.assertEqual(len(app.mine_revealed),71)
    def test_mine_hit_ends_game(self):
        ns=self.ns('mines');app=self.mines_app();ns['mines_reset'](app);app.mine_cells=set(range(10));ns['mines_reveal'](app,0);self.assertTrue(app.mine_done);self.assertEqual(app.mine_revealed,set());app.Cell0.configure.assert_called_with(text='*',state='disabled',bg='#dbe6f5')
    def maze_path(self,grid):
        queue=deque([(1,1)]);previous={(1,1):None}
        while queue:
            row,column=queue.popleft()
            for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
                point=(row+dr,column+dc)
                if 0<=point[0]<21 and 0<=point[1]<21 and not grid[point[0]][point[1]] and point not in previous:previous[point]=(row,column);queue.append(point)
        path=[];point=(19,19)
        while point is not None:path.append(point);point=previous[point]
        return list(reversed(path)),previous
    def test_mazes_are_connected_and_have_reachable_exit(self):
        generate=self.ns('maze')['maze_generate']
        for seed in range(25):
            grid=generate(random.Random(seed));path,seen=self.maze_path(grid);self.assertGreater(len(path),1);self.assertEqual(len(seen),199);self.assertEqual(sum(value==0 for row in grid for value in row),199);self.assertTrue(all(grid[0]));self.assertTrue(all(grid[-1]))
    def test_maze_wall_and_path_to_win(self):
        ns=self.ns('maze');app=types.SimpleNamespace(MazeCanvas=Mock(),StatusLabel=Mock());ns['maze_reset'](app);self.assertFalse(ns['maze_move'](app,-1,0));self.assertEqual(app.maze_moves,0)
        path,seen=self.maze_path(app.maze_grid)
        for first,second in zip(path,path[1:]):self.assertTrue(ns['maze_move'](app,second[0]-first[0],second[1]-first[1]))
        self.assertTrue(app.maze_won);self.assertEqual(app.maze_moves,len(path)-1);self.assertFalse(ns['maze_move'](app,-1,0))
    def test_calendar_leap_year_padding_and_navigation(self):
        ns=self.ns('agenda');cells=ns['agenda_month_cells'](2024,2);self.assertEqual(len(cells),42);self.assertIn(29,cells);self.assertNotIn(29,ns['agenda_month_cells'](2025,2))
        app=types.SimpleNamespace(calendar_year=2026,calendar_month=1,calendar_day='2026-01-01',MonthLabel=Mock(),SelectedDayLabel=Mock(),archive_selected=None,archive_records=[],archive_visible=[],FilterEntry=Mock(),RecordList=Mock(),StatusLabel=Mock(),**{'Day'+str(i):Mock() for i in range(42)},**{'Field'+str(i):Mock() for i in range(6)})
        app.FilterEntry.get.return_value='';ns['agenda_shift'](app,-1);self.assertEqual((app.calendar_year,app.calendar_month),(2025,12));self.assertEqual(app.calendar_day,'2025-12-01');app.Field0.insert.assert_called_with(0,'2025-12-01')
        app.calendar_year=1;app.calendar_month=1;ns['agenda_shift'](app,-1);self.assertEqual(app.calendar_year,1)
    def agenda_app(self):
        ns=self.ns('agenda');sample={'id':'one','date':'2026-11-14','start':'09:00','end':'10:00','title':'Caffè meeting','place':'Room A','notes':'note'}
        app=types.SimpleNamespace(Form1=Mock(),root=Mock(),archive_records=[sample],archive_selected=None,archive_visible=[],FilterEntry=Mock(),RecordList=Mock(),StatusLabel=Mock(),calendar_year=2026,calendar_month=11,calendar_day='2026-11-14',MonthLabel=Mock(),SelectedDayLabel=Mock(),**{'Day'+str(i):Mock() for i in range(42)},**{'Field'+str(i):Mock() for i in range(6)})
        app.FilterEntry.get.return_value='';return ns,app
    def test_agenda_validation_and_json_persistence(self):
        ns,app=self.agenda_app();record=app.archive_records[0]
        for bad in (dict(record,date='2026-02-30'),dict(record,start='9:00'),dict(record,end='08:00')):
            with self.assertRaises(ValueError):ns['archive_validate_records']([bad])
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'agenda.json';ns['filedialog'].asksaveasfilename.return_value=str(path);ns['archive_save'](app);before=copy.deepcopy(app.archive_records);app.archive_records=[];ns['filedialog'].askopenfilename.return_value=str(path);ns['messagebox'].askyesno.return_value=True;ns['archive_open'](app);self.assertEqual(app.archive_records,before)
    def test_agenda_day_click_and_empty_cell_guard(self):
        ns,app=self.agenda_app();ns['agenda_draw'](app);empty=app.calendar_cells.index(0);before=app.calendar_day;ns['agenda_pick'](app,empty);self.assertEqual(app.calendar_day,before)
        ns['agenda_pick'](app,app.calendar_cells.index(20));self.assertEqual(app.calendar_day,'2026-11-20');app.FilterEntry.insert.assert_called_with(0,'2026-11-20');app.Field1.insert.assert_called_with(0,'09:00')
    def slide_app(self):
        app=types.SimpleNamespace(Form1=Mock(),root=Mock(),ImageLabel=Mock(),StatusLabel=Mock(),PlayButton=Mock(),IntervalScale=Mock(),slide_files=[],slide_index=0,slide_photo=None,slide_job=None,slide_playing=False,slide_generation=0);app.IntervalScale.get.return_value=3;app.root.after.return_value='timer';app.ImageLabel.winfo_width.return_value=210;app.ImageLabel.winfo_height.return_value=110;return app
    def png(self,path,width=400,height=200):path.write_bytes(b'\x89PNG\r\n\x1a\n'+b'\0'*8+struct.pack('>II',width,height))
    def test_slideshow_scan_formats_order_and_symlinks(self):
        ns=self.ns('slideshow')
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            for name in ('b.png','A.GIF','skip.jpg','text.txt'):(root/name).write_text('fixture')
            (root/'link.png').symlink_to(root/'b.png');self.assertEqual([p.name for p in ns['slide_scan'](root)],['A.GIF','b.png'])
    def test_slideshow_dimensions_and_invalid_files(self):
        ns=self.ns('slideshow')
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'image.png';self.png(path);self.assertEqual(ns['slide_dimensions'](path),(400,200));self.png(path,100000,100000)
            with self.assertRaises(ValueError):ns['slide_dimensions'](path)
            path.write_bytes(b'not an image')
            with self.assertRaises(ValueError):ns['slide_dimensions'](path)
    def test_slideshow_show_holds_thumbnail_and_handles_deleted_file(self):
        ns=self.ns('slideshow');app=self.slide_app()
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'image.png';self.png(path);app.slide_files=[path];image=Mock();thumb=Mock();image.subsample.return_value=thumb
            with patch.object(ns['tk'],'PhotoImage',return_value=image):ns['slide_show'](app)
            image.subsample.assert_called_once_with(2);self.assertIs(app.slide_photo,thumb);path.unlink();ns['slide_show'](app);self.assertIsNone(app.slide_photo);app.ImageLabel.configure.assert_called_with(text='Cannot display this image')
    def test_slideshow_pause_generation_and_close(self):
        ns=self.ns('slideshow');app=self.slide_app();app.slide_files=[Path('/missing/first.png'),Path('/missing/second.png')];ns['slide_toggle'](app);self.assertTrue(app.slide_playing);callback=app.root.after.call_args.args[1];ns['slide_pause'](app);before=app.slide_index;callback();self.assertEqual(app.slide_index,before);self.assertIsNone(app.slide_job)
        ns['slide_toggle'](app);ns['slide_close'](app);self.assertFalse(app.slide_playing);app.root.destroy.assert_called_once()
    def test_slideshow_tick_wrap_and_manual_step_pause(self):
        ns=self.ns('slideshow');app=self.slide_app();app.slide_files=[Path('/missing/a.png'),Path('/missing/b.png')];app.slide_playing=True;app.slide_index=1;ns['slide_tick'](app,0);self.assertEqual(app.slide_index,0);self.assertEqual(app.root.after.call_args.args[0],3000)
        ns['slide_step'](app,-1);self.assertEqual(app.slide_index,1);self.assertFalse(app.slide_playing)
    def test_slideshow_folder_cancel_and_empty_folder_keep_current_list(self):
        ns=self.ns('slideshow');app=self.slide_app();app.slide_files=[Path('/old.png')];ns['filedialog'].askdirectory.return_value='';ns['slide_open'](app);self.assertEqual(app.slide_files,[Path('/old.png')])
        with tempfile.TemporaryDirectory() as d:
            ns['filedialog'].askdirectory.return_value=d;ns['slide_open'](app);self.assertEqual(app.slide_files,[Path('/old.png')]);ns['messagebox'].showinfo.assert_called_once()
