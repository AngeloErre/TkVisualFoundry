"""Offline checks for the four additional editable starter applications."""
import copy
from contextlib import closing
import csv
import json
from pathlib import Path
import sqlite3
import tempfile
import types
import unittest
from unittest.mock import Mock,patch
from project_templates import instantiate

class AdditionalStarterTests(unittest.TestCase):
    def ns(self,key):
        ns={'messagebox':Mock(),'filedialog':Mock()};exec(instantiate(key)['imports'],ns);return ns
    def kanban(self):
        ns=self.ns('kanban')
        app=types.SimpleNamespace(cards=[],selected=None,dragging=None,dirty=False,focus_sessions=0,Board=Mock(canvasx=lambda x:x,canvasy=lambda y:y),Summary=Mock(),Title=Mock(get=lambda:'Task'),Due=Mock(get=lambda:'2027-01-05'),Stage=Mock(get=lambda:'To do'),Form1=Mock(),root=Mock(),focus_timer=None,focus_generation=0,focus_running=False,focus_remaining=0,Minutes=Mock(get=lambda:'1'),TimerLabel=Mock())
        return ns,app
    def test_kanban_crud_and_unique_card_ids(self):
        ns,a=self.kanban();ns['kanban_edit'](a);first=a.cards[0]['id'];ns['kanban_edit'](a);self.assertNotEqual(a.cards[1]['id'],first)
        a.Title.get=lambda:'Updated';ns['kanban_edit'](a,True);self.assertEqual(a.cards[1]['title'],'Updated')
        ns['messagebox'].askyesno.return_value=False;ns['kanban_delete'](a);self.assertEqual(len(a.cards),2)
        ns['messagebox'].askyesno.return_value=True;ns['kanban_delete'](a);self.assertEqual(len(a.cards),1)
    def test_kanban_schema_dates_and_limits(self):
        ns,a=self.kanban();ns['kanban_edit'](a);valid={'type':'tkvf-kanban','version':1,'cards':a.cards}
        for mutate in (lambda d:d.update(type='wrong'),lambda d:d['cards'].append(dict(d['cards'][0])),lambda d:d['cards'][0].update(due='2026-02-30'),lambda d:d['cards'][0].update(stage='Other'),lambda d:d['cards'][0].update(title=''),lambda d:d.update(cards=[d['cards'][0]]*121)):
            bad=copy.deepcopy(valid);mutate(bad)
            with self.assertRaises(ValueError):ns['kanban_validate'](bad)
        self.assertEqual(ns['kanban_validate'](valid),a.cards)
    def test_kanban_drag_between_stages_and_outside_drop(self):
        ns,a=self.kanban();ns['kanban_edit'](a);ns['kanban_select'](a,types.SimpleNamespace(x=30,y=60));self.assertEqual(a.dragging,a.selected)
        ns['kanban_release'](a,types.SimpleNamespace(x=650,y=80));self.assertEqual(a.cards[0]['stage'],'Done')
        a.dragging=a.selected;ns['kanban_release'](a,types.SimpleNamespace(x=-5,y=80));self.assertEqual(a.cards[0]['stage'],'Done');self.assertIsNone(a.dragging)
    def test_kanban_atomic_json_roundtrip_and_failed_replace(self):
        ns,a=self.kanban();ns['kanban_edit'](a)
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'board.json';ns['filedialog'].asksaveasfilename.return_value=str(path);ns['kanban_file'](a);self.assertFalse(a.dirty)
            stored=path.read_bytes();a.cards=[];ns['filedialog'].askopenfilename.return_value=str(path);ns['kanban_file'](a,True);self.assertEqual(len(a.cards),1)
            with patch.object(ns['os'],'replace',side_effect=OSError('disk full')):
                with self.assertRaises(OSError):ns['write_json'](path,{'new':'data'})
            self.assertEqual(path.read_bytes(),stored);self.assertEqual(list(Path(d).iterdir()),[path])
    def test_kanban_open_cancel_and_dirty_close_guard(self):
        ns,a=self.kanban();a.dirty=True;ns['messagebox'].askyesno.return_value=False
        ns['kanban_file'](a,True);ns['filedialog'].askopenfilename.assert_not_called();ns['kanban_close'](a);a.root.destroy.assert_not_called()
        ns['messagebox'].askyesno.return_value=True;ns['filedialog'].askopenfilename.return_value='';ns['kanban_file'](a,True);self.assertTrue(a.dirty)
        ns['kanban_close'](a);a.root.destroy.assert_called_once()
    def test_focus_pause_resume_monotonic_deadline_and_stale_tick(self):
        ns,a=self.kanban()
        with patch.object(ns['time'],'monotonic',return_value=100):ns['focus_start'](a)
        old=a.focus_generation;self.assertEqual(a.focus_deadline,160)
        with patch.object(ns['time'],'monotonic',return_value=120):ns['focus_pause'](a)
        self.assertEqual(a.focus_remaining,40);a.root.after.reset_mock();ns['focus_tick'](a,old);a.root.after.assert_not_called()
        with patch.object(ns['time'],'monotonic',return_value=200):ns['focus_start'](a)
        self.assertEqual(a.focus_deadline,240)
        with patch.object(ns['time'],'monotonic',return_value=241):ns['focus_tick'](a,a.focus_generation)
        self.assertEqual(a.focus_sessions,1);self.assertFalse(a.focus_running)
    def test_focus_bad_duration_and_reset(self):
        ns,a=self.kanban();a.Minutes.get=lambda:'0';ns['focus_start'](a);self.assertFalse(a.focus_running);ns['messagebox'].showerror.assert_called_once()
        a.focus_remaining=5;ns['focus_reset'](a);self.assertEqual(a.focus_remaining,0)
    def data_app(self):
        ns=self.ns('data');a=types.SimpleNamespace(headers=['Name','Value'],rows=[['Alpha','2'],['Beta','10'],['Gamma','bad']],visible=[],source=None,truncated=False,page=0,descending=False,Column=Mock(get=lambda:'Value'),Filter=Mock(get=lambda:''),Grid=Mock(get_children=lambda:()),Summary=Mock(),Chart=Mock(),Table=Mock(),Form1=Mock())
        return ns,a
    def test_csv_utf8_delimiters_duplicates_and_row_limits(self):
        ns=self.ns('data')
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'data.csv';path.write_text('\ufeffName;Name;\ncaffè;2;3\n',encoding='utf-8');h,r,t,tables=ns['data_load'](path)
            self.assertEqual(h,['Name','Name (2)','Column 3']);self.assertEqual(r,[['caffè','2','3']]);self.assertFalse(t)
            path.write_text('A,B\n'+'1,2\n'*5001);h,r,t,_=ns['data_load'](path);self.assertEqual(len(r),5000);self.assertTrue(t)
    def test_csv_empty_and_unsupported_format(self):
        ns=self.ns('data')
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'empty.csv';p.write_text('')
            with self.assertRaises(ValueError):ns['data_load'](p)
            p=Path(d)/'old.xls';p.write_text('binary')
            with self.assertRaises(ValueError):ns['data_load'](p)
    def test_sqlite_quoted_table_selection_and_readonly_source(self):
        ns=self.ns('data')
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'data ?.db'
            with closing(sqlite3.connect(path)) as db:
                db.execute('CREATE TABLE "odd""table" (name TEXT, n REAL)');db.execute('INSERT INTO "odd""table" VALUES (?,?)',('caffè',12.5));db.commit()
            before=path.read_bytes();h,r,t,tables=ns['data_sqlite'](path)
            self.assertEqual(h,['name','n']);self.assertEqual(r,[['caffè','12.5']]);self.assertEqual(tables,['odd"table']);self.assertEqual(path.read_bytes(),before)
            with self.assertRaises(ValueError):ns['data_sqlite'](path,'other; DROP TABLE x')
            missing=Path(d)/'missing.db'
            with self.assertRaises(sqlite3.OperationalError):ns['data_sqlite'](missing)
            self.assertFalse(missing.exists())
    def test_sqlite_row_cap_and_binary_marker(self):
        ns=self.ns('data')
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'many.db'
            with closing(sqlite3.connect(path)) as db:
                db.execute('CREATE TABLE items (payload BLOB)');db.executemany('INSERT INTO items VALUES (?)',[(b'abc',)]*5001);db.commit()
            h,r,t,_=ns['data_sqlite'](path);self.assertTrue(t);self.assertEqual(len(r),5000);self.assertEqual(r[0],['<binary 3 bytes>'])
    def test_real_xlsx_values_and_formulas_not_executed(self):
        try:import openpyxl
        except ImportError:self.skipTest('Optional openpyxl missing')
        ns=self.ns('data')
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'book.xlsx';book=openpyxl.Workbook();book.active.append(['Name','Value']);book.active.append(['Example',12]);book.active.append(['Formula','=1+2']);book.save(path);book.close();before=path.read_bytes()
            h,r,t,_=ns['data_load'](path);self.assertEqual(h,['Name','Value']);self.assertEqual(r,[['Example','12'],['Formula','']]);self.assertEqual(path.read_bytes(),before)
    def test_data_filters_numeric_order_and_finite_stats(self):
        ns,a=self.data_app();self.assertEqual(ns['data_filter'](a.rows,'',1)[0][1],'2');self.assertEqual(ns['data_filter'](a.rows,'BETA'),[['Beta','10']])
        stats=ns['data_summary'](a.rows+[ ['Other','NaN'],['Other','inf'] ],1);self.assertEqual(stats['numeric'],2);self.assertEqual(stats['mean'],6)
        self.assertIsNone(ns['data_summary']([],1)['mean'])
    def test_data_pagination_preserves_descending_order(self):
        ns,a=self.data_app();a.rows=[[str(i),str(i)] for i in range(205)];ns['data_refresh'](a,True);self.assertEqual(a.visible[0][1],'204')
        ns['data_page'](a,1);self.assertEqual(a.page,1);self.assertTrue(a.descending);self.assertEqual(a.visible[0][1],'204')
        ns['data_page'](a,100);self.assertEqual(a.page,2)
    def test_csv_export_filter_formula_escape_and_source_guard(self):
        ns,a=self.data_app();a.visible=[['=CMD()','-4'],['safe','2']]
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/'source.csv';source.write_text('original');a.source=str(source);ns['filedialog'].asksaveasfilename.return_value=str(source);ns['data_export'](a);self.assertEqual(source.read_text(),'original')
            target=Path(d)/'export.csv';ns['filedialog'].asksaveasfilename.return_value=str(target);ns['data_export'](a)
            with target.open(newline='') as stream:rows=list(csv.reader(stream))
            self.assertEqual(rows[1],["'=CMD()",'-4']);self.assertEqual(len(rows),3)
    def lab(self):
        ns=self.ns('cognitive');a=types.SimpleNamespace(timer=None,generation=0,phase='idle',Mode=Mock(get=lambda:'Memory'),Answer=Mock(get=lambda:''),Board=Mock(),Feedback=Mock(),Trend=Mock(),Summary=Mock(),Form1=Mock(),root=Mock(),levels={'Memory':3,'Attention':6},results=[])
        return ns,a
    def test_memory_display_guard_hidden_response_and_adaptive_level(self):
        ns,a=self.lab();ns['lab_start'](a);self.assertEqual(a.phase,'showing');ns['lab_submit'](a);self.assertEqual(a.results,[])
        with patch.object(ns['time'],'monotonic',return_value=10):ns['lab_memory_hide'](a,a.generation)
        a.Answer.get=lambda:' '.join(a.expected)
        with patch.object(ns['time'],'monotonic',return_value=10.25):ns['lab_submit'](a)
        self.assertEqual(a.results[0]['response_ms'],250);self.assertTrue(a.results[0]['correct']);self.assertEqual(a.levels['Memory'],4)
        ns['lab_submit'](a);self.assertEqual(len(a.results),1)
    def test_memory_reset_cancels_stale_hiding(self):
        ns,a=self.lab();ns['lab_start'](a);old=a.generation;ns['lab_start'](a);a.Board.reset_mock();ns['lab_memory_hide'](a,old);a.Board.delete.assert_not_called();a.root.after_cancel.assert_called()
        ns['lab_cancel'](a);self.assertEqual(a.phase,'idle')
    def test_memory_adaptation_bounds_and_result_cap(self):
        ns,a=self.lab();a.phase='answer';a.trial_mode='Memory';a.trial_level=9;a.started=ns['time'].monotonic();ns['lab_finish'](a,True);self.assertEqual(a.levels['Memory'],9)
        a.phase='answer';a.trial_level=2;ns['lab_finish'](a,False);self.assertEqual(a.levels['Memory'],2)
        a.results=a.results*110;a.phase='answer';ns['lab_finish'](a,False);self.assertEqual(len(a.results),200)
    def test_attention_hit_miss_and_click_gaps(self):
        ns,a=self.lab();a.Mode.get=lambda:'Attention';ns['lab_start'](a);ns['lab_click'](a,types.SimpleNamespace(x=10,y=10));self.assertEqual(a.results,[])
        x=220+(a.target%6)*75+30;y=20+(a.target//6)*50+20;ns['lab_click'](a,types.SimpleNamespace(x=x,y=y));self.assertTrue(a.results[-1]['correct'])
        ns['lab_start'](a);other=(a.target+1)%36;ns['lab_click'](a,types.SimpleNamespace(x=220+(other%6)*75+30,y=20+(other//6)*50+20));self.assertFalse(a.results[-1]['correct'])
    def test_lab_export_exact_session_and_close_guard(self):
        ns,a=self.lab();a.phase='answer';a.trial_mode='Memory';a.trial_level=3;a.started=ns['time'].monotonic();ns['lab_finish'](a,True)
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'results.csv';ns['filedialog'].asksaveasfilename.return_value=str(path);ns['lab_export'](a)
            with path.open(newline='') as stream:rows=list(csv.DictReader(stream))
            self.assertEqual(len(rows),1);self.assertEqual(rows[0]['mode'],'Memory')
        ns['messagebox'].askyesno.return_value=False;ns['lab_close'](a);a.root.destroy.assert_not_called()
        ns['messagebox'].askyesno.return_value=True;ns['lab_close'](a);a.root.destroy.assert_called_once()
    def escape_state(self):return {'type':'tkvf-escape','version':1,'room':'foyer','inventory':[],'solved':[],'ending':'','moves':0}
    def escape_path(self,ns,rescue=False):
        state=self.escape_state();apply=ns['escape_apply']
        if rescue:state,_=apply(state,'take','compass')
        for action,arg,answer in [('take','note',''),('solve','','314'),('go','workshop',''),('take','inscription',''),('solve','',' SUN '),('go','garden','')]:state,_=apply(state,action,arg,answer)
        return apply(state,'end','rescued' if rescue else 'solo')[0]
    def test_escape_both_endings_and_original_state_unchanged(self):
        ns=self.ns('escape');self.assertEqual(self.escape_path(ns)['ending'],'solo');self.assertEqual(self.escape_path(ns,True)['ending'],'rescued')
        state=self.escape_state();ns['escape_apply'](state,'take','note');self.assertEqual(state['inventory'],[])
    def test_escape_locked_doors_wrong_answers_and_missing_compass(self):
        ns=self.ns('escape');state=self.escape_state();same,notice=ns['escape_apply'](state,'go','workshop');self.assertEqual(same,state);self.assertIn('locked',notice)
        same,notice=ns['escape_apply'](state,'solve','','wrong');self.assertEqual(same,state)
        end=self.escape_path(ns);end['ending']='';same,notice=ns['escape_apply'](end,'end','rescued');self.assertEqual(same,end);self.assertIn('compass',notice)
    def test_escape_rejects_impossible_or_malformed_saves(self):
        ns=self.ns('escape');base=self.escape_state()
        for mutate in (lambda d:d.update(room='garden'),lambda d:d.update(ending='rescued'),lambda d:d.update(moves=-1),lambda d:d.update(inventory=['unknown']),lambda d:d.update(solved=['box']),lambda d:d.update(inventory=['note','note'])):
            bad=copy.deepcopy(base);mutate(bad)
            with self.assertRaises(ValueError):ns['escape_validate'](bad)
        with self.assertRaises(ValueError):ns['escape_apply'](base,'go','garden')
    def test_escape_real_save_roundtrip_and_finished_actions(self):
        ns=self.ns('escape');end=self.escape_path(ns,True)
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'progress.json';ns['write_json'](path,end);self.assertEqual(ns['escape_validate'](ns['read_json'](path)),end)
        self.assertEqual(ns['escape_actions'](end),[])
        with self.assertRaises(ValueError):ns['escape_apply'](end,'end','solo')
if __name__=='__main__':unittest.main()
