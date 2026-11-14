import datetime
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import Mock,patch
from project_templates import instantiate

class StarterBatchThreeTests(unittest.TestCase):
    def ns(self,key):
        ns={'messagebox':Mock(),'filedialog':Mock(),'colorchooser':Mock()};exec(instantiate(key)['imports'],ns);return ns
    def clock_app(self):
        return types.SimpleNamespace(root=Mock(),StopwatchLabel=Mock(),CountdownLabel=Mock(),StatusLabel=Mock(),SecondsEntry=Mock(get=lambda:'10'),AlarmEntry=Mock(get=lambda:'07:30'),sw_elapsed=0.0,sw_started=None,count_deadline=None,alarm_target=None,clock_job=None)
    def test_stopwatch_pause_resume_and_reset(self):
        ns=self.ns('clocks');app=self.clock_app()
        with patch.object(ns['time'],'monotonic',side_effect=[100,110,120,125]):
            ns['stopwatch_toggle'](app);ns['stopwatch_toggle'](app);self.assertEqual(app.sw_elapsed,10);ns['stopwatch_toggle'](app);ns['clock_refresh'](app)
        app.StopwatchLabel.configure.assert_called_with(text='00:00:15');ns['stopwatch_reset'](app);self.assertEqual(app.sw_elapsed,0);self.assertIsNone(app.sw_started)
    def test_countdown_input_finish_and_single_bell(self):
        ns=self.ns('clocks');app=self.clock_app()
        with patch.object(ns['time'],'monotonic',return_value=100):ns['countdown_start'](app)
        self.assertEqual(app.count_deadline,110);app.SecondsEntry.get=lambda:'invalid';ns['countdown_start'](app);self.assertEqual(app.count_deadline,110)
        with patch.object(ns['time'],'monotonic',return_value=111):ns['clock_refresh'](app);ns['clock_refresh'](app)
        self.assertIsNone(app.count_deadline);app.root.bell.assert_called_once();app.CountdownLabel.configure.assert_called_with(text='00:00:00')
    def test_alarm_rollover_and_trigger(self):
        ns=self.ns('clocks');app=self.clock_app()
        class Fixed(datetime.datetime):
            @classmethod
            def now(cls):return cls(2026,11,14,8,0)
        ns['datetime']=types.SimpleNamespace(datetime=Fixed,timedelta=datetime.timedelta)
        ns['alarm_set'](app);self.assertEqual(app.alarm_target,Fixed(2026,11,15,7,30));app.alarm_target=Fixed(2026,11,14,7,30);ns['clock_refresh'](app);ns['clock_refresh'](app);app.root.bell.assert_called_once()
        app.AlarmEntry.get=lambda:'99:00';ns['alarm_set'](app);self.assertIsNone(app.alarm_target)
    def test_clock_scheduler_and_owned_close(self):
        ns=self.ns('clocks');app=self.clock_app();app.root.after.return_value='tick';ns['clock_tick'](app);app.root.after.assert_called_once();ns['clock_close'](app);app.root.after_cancel.assert_called_once_with('tick');app.root.destroy.assert_called_once()
    def test_habit_streak_today_yesterday_and_gap(self):
        f=self.ns('habits')['habit_streak'];today=datetime.date(2026,11,14)
        self.assertEqual(f(['2026-11-12','2026-11-13'],today),2);self.assertEqual(f(['2026-11-12','2026-11-13','2026-11-14'],today),3);self.assertEqual(f(['2026-11-12'],today),0)
    def test_habit_validation_rejects_bad_records(self):
        f=self.ns('habits')['habit_validate'];self.assertEqual(f([{'name':'Read','days':['2026-11-14']*2}])[0]['days'],['2026-11-14'])
        for data in ({},[{'name':'','days':[]}],[{'name':'Read','days':['bad']}],[{'name':'Read','days':[]},{'name':'READ','days':[]}]):
            with self.assertRaises(ValueError):f(data)
    def test_habit_toggle_twice_and_reject_duplicate_name(self):
        ns=self.ns('habits');app=types.SimpleNamespace(habits=[{'name':'Read','days':[]}],HabitList=Mock(curselection=lambda:(0,)),StatusLabel=Mock(),HabitEntry=Mock(get=lambda:'read'))
        ns['habit_toggle'](app);self.assertEqual(len(app.habits[0]['days']),1);ns['habit_toggle'](app);self.assertEqual(app.habits[0]['days'],[]);ns['habit_add'](app);self.assertEqual(len(app.habits),1);ns['messagebox'].showerror.assert_called_once()
    def test_habit_save_open_and_failed_replace_preserves_original(self):
        ns=self.ns('habits');app=types.SimpleNamespace(Form1=Mock(),habits=[{'name':'Read','days':[]}],HabitList=Mock(),StatusLabel=Mock())
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'habits.json';path.write_text('original');ns['filedialog'].asksaveasfilename.return_value=str(path)
            with patch.object(ns['os'],'replace',side_effect=OSError('disk error')):ns['habit_save'](app)
            self.assertEqual(path.read_text(),'original');self.assertEqual(list(Path(d).iterdir()),[path]);ns['habit_save'](app);self.assertEqual(json.loads(path.read_text()),app.habits)
            ns['filedialog'].askopenfilename.return_value=str(path);ns['messagebox'].askyesno.return_value=True;app.habits=[];ns['habit_open'](app);self.assertEqual(app.habits[0]['name'],'Read')
            path.write_text('[42]');before=app.habits;ns['habit_open'](app);self.assertIs(app.habits,before)
    def note_app(self,text='changed'):
        editor=Mock(get=lambda *a:text);note={'text':editor,'path':None,'title':'Note 1','saved':''};tabs=Mock();tabs.select.return_value='tab1';return types.SimpleNamespace(Form1=Mock(),root=Mock(),notes={'tab1':note},NotesTabs=tabs,StatusLabel=Mock()),note
    def test_notepad_save_cancel_and_close_guard(self):
        ns=self.ns('notepad');app,note=self.note_app();ns['filedialog'].asksaveasfilename.return_value='';self.assertFalse(ns['tabs_save'](app));self.assertEqual(note['saved'],'')
        ns['messagebox'].askyesnocancel.return_value=None;ns['tabs_close_app'](app);app.root.destroy.assert_not_called();self.assertIn('tab1',app.notes)
        ns['messagebox'].askyesnocancel.return_value=False;ns['tabs_close_app'](app);app.root.destroy.assert_called_once()
    def test_notepad_atomic_save_and_failure_keeps_dirty_state(self):
        ns=self.ns('notepad');app,note=self.note_app('caffè')
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'note.txt';path.write_text('original');ns['filedialog'].asksaveasfilename.return_value=str(path)
            with patch.object(ns['os'],'replace',side_effect=OSError('disk error')):self.assertFalse(ns['tabs_save'](app))
            self.assertEqual(path.read_text(),'original');self.assertEqual(note['saved'],'');self.assertEqual(list(Path(d).iterdir()),[path]);self.assertTrue(ns['tabs_save'](app));self.assertEqual(path.read_text(),'caffè');self.assertEqual(note['saved'],'caffè')
    def test_notepad_duplicate_open_focuses_existing_buffer(self):
        ns=self.ns('notepad');app,note=self.note_app('unsaved changes')
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'note.txt';path.write_text('disk');note['path']=str(path);ns['filedialog'].askopenfilename.return_value=str(path);ns['tabs_open'](app);app.NotesTabs.select.assert_called_with('tab1');note['text'].insert.assert_not_called();note['text'].focus_set.assert_called_once()
    def test_notepad_title_marks_unsaved_changes(self):
        ns=self.ns('notepad');app,note=self.note_app();ns['tabs_title'](app,'tab1');app.NotesTabs.tab.assert_called_with('tab1',text='Note 1 *');note['saved']='changed';ns['tabs_title'](app,'tab1');app.NotesTabs.tab.assert_called_with('tab1',text='Note 1')
    def test_notepad_adds_dynamic_page_and_enforces_limit(self):
        ns=self.ns('notepad');app,note=self.note_app();app.note_counter=1
        class Frame:
            def __str__(self):return 'tab2'
        frame=Frame();app.NotesTabs.add_page.return_value=frame;editor=Mock();ns['ScrolledText']=Mock(return_value=editor)
        self.assertEqual(ns['tabs_add'](app),'tab2');self.assertEqual(len(app.notes),2);self.assertIs(app.notes['tab2']['text'],editor);app.NotesTabs.select.assert_called_with(frame)
        app.notes={str(i):note for i in range(20)};self.assertIsNone(ns['tabs_add'](app));self.assertEqual(len(app.notes),20)
    def test_notepad_close_cancel_and_frame_cleanup(self):
        ns=self.ns('notepad');app,note=self.note_app();frame=Mock();frame.__str__=Mock(return_value='tab1');app.NotesTabs.pages={'Note 1':frame};app.notes['other']={'text':Mock(get=lambda *a:''),'saved':'','path':None,'title':'Other'}
        ns['messagebox'].askyesnocancel.return_value=None;ns['tabs_close'](app);app.NotesTabs.forget.assert_not_called()
        ns['messagebox'].askyesnocancel.return_value=False;ns['tabs_close'](app);app.NotesTabs.forget.assert_called_with('tab1');self.assertNotIn('tab1',app.notes);self.assertNotIn('Note 1',app.NotesTabs.pages);frame.destroy.assert_called_once()
    def pixel_app(self):return types.SimpleNamespace(Form1=Mock(),root=Mock(),PixelCanvas=Mock(),StatusLabel=Mock(),pixel_grid=[['#FFFFFF']*16 for _ in range(16)],pixel_color='#000000')
    def test_pixel_edges_palette_and_clear_guard(self):
        ns=self.ns('pixels');app=self.pixel_app();ns['pixel_draw'](app,types.SimpleNamespace(x=511,y=511));self.assertEqual(app.pixel_grid[15][15],'#000000');ns['pixel_draw'](app,types.SimpleNamespace(x=512,y=512));self.assertEqual(app.PixelCanvas.itemconfigure.call_count,1)
        ns['pixel_choose'](app,'bad');self.assertEqual(app.pixel_color,'#000000');ns['pixel_choose'](app,'#ff0000');self.assertEqual(app.pixel_color,'#FF0000')
        ns['messagebox'].askyesno.return_value=False;ns['pixel_clear'](app);self.assertEqual(app.pixel_grid[15][15],'#000000')
        ns['messagebox'].askyesno.return_value=True;ns['pixel_clear'](app);self.assertEqual(app.pixel_grid[15][15],'#FFFFFF');self.assertEqual(app.PixelCanvas.create_rectangle.call_count,256)
    def test_pixel_ppm_and_svg_are_real_image_payloads(self):
        ns=self.ns('pixels');app=self.pixel_app();app.pixel_grid[0][0]='#FF0000';payload=ns['pixel_ppm'](app.pixel_grid);header=b'P6\n16 16\n255\n';self.assertTrue(payload.startswith(header));self.assertEqual(len(payload),len(header)+16*16*3);self.assertEqual(payload[len(header):len(header)+3],b'\xff\x00\x00')
        import xml.etree.ElementTree as ET
        root=ET.fromstring(ns['pixel_svg'](app.pixel_grid));self.assertEqual(len(root),256);self.assertEqual(root[0].attrib['fill'],'#FF0000')
    def test_pixel_exports_to_temp_files_and_cancel_is_noop(self):
        ns=self.ns('pixels');app=self.pixel_app()
        with tempfile.TemporaryDirectory() as d:
            for kind in ('ppm','svg'):
                path=Path(d)/('image.'+kind);ns['filedialog'].asksaveasfilename.return_value=str(path);ns['pixel_export'](app,kind);self.assertGreater(path.stat().st_size,100)
            ns['filedialog'].asksaveasfilename.return_value='';ns['pixel_export'](app,'ppm');self.assertEqual(len(list(Path(d).iterdir())),2)
