import io
import json
from pathlib import Path
import tempfile
import tokenize
import types
import unittest
from unittest.mock import Mock,patch
from core import generate,validate,new_project
from components import requirements
from project_templates import catalog,instantiate

class StarterTemplateTests(unittest.TestCase):
    def test_catalog_unique_and_every_starter_compiles_without_pip(self):
        entries=catalog();self.assertEqual(len(entries),25);self.assertEqual(len({e['id'] for e in entries}),25)
        for entry in entries:
            p=instantiate(entry['id']);validate(p);compile(generate(p),entry['id'],'exec');self.assertEqual(requirements(p),[])
    def test_copies_are_independent_and_source_files_unchanged(self):
        p=instantiate('quiz');original=instantiate('quiz');p['forms'][0]['widgets'][0]['props']['text']='changed';p['startup']='pass'
        self.assertEqual(instantiate('quiz'),original)
        with self.assertRaises(ValueError):instantiate('../outside')
    def test_all_template_code_sections_have_comments(self):
        for key in ('quiz','dice','text','notes','odd','memory','puzzle15','paint','clocks','notepad','habits','pixels','calculator','timetable','recipes','books','contacts','expenses','inventory','media','mines','maze','agenda','slideshow'):
            p=instantiate(key);sections=[p['imports'],p['startup']]+[body for f in p['forms'] for w in f['widgets'] for body in w['events'].values()]
            for section in sections:self.assertTrue(any(t.type==tokenize.COMMENT for t in tokenize.generate_tokens(io.StringIO(section).readline)),key)
    def test_loading_templates_never_executes_their_imports(self):
        with patch('builtins.exec',side_effect=AssertionError('Template executed')):
            self.assertEqual(instantiate('dice')['name'],'Dice Roller')
    def namespace(self,key):
        ns={'messagebox':Mock(),'filedialog':Mock()};exec(instantiate(key)['imports'],ns);return ns
    def test_quiz_scoring_finish_and_restart(self):
        ns=self.namespace('quiz');app=types.SimpleNamespace(quiz_questions=[('Q',['A','B','C','D'],1)],QuestionLabel=Mock(),ScoreLabel=Mock(),**{'Answer'+str(i):Mock() for i in range(1,5)})
        ns['quiz_reset'](app);ns['quiz_answer'](app,1);self.assertEqual((app.quiz_index,app.quiz_score),(1,1));app.Answer1.configure.assert_called_with(state='disabled')
        ns['quiz_answer'](app,1);self.assertEqual(app.quiz_score,1);ns['quiz_reset'](app);self.assertEqual((app.quiz_index,app.quiz_score),(0,0))
    def test_dice_valid_total_and_invalid_inputs(self):
        ns=self.namespace('dice');app=types.SimpleNamespace(DieChoice=Mock(get=lambda:'D20'),CountEntry=Mock(get=lambda:'3'),BonusEntry=Mock(get=lambda:'-1'),ResultText=Mock())
        with patch.object(ns['random'],'randint',return_value=4):ns['roll_dice'](app)
        self.assertIn('Total: 11',app.ResultText.insert.call_args.args[1]);self.assertIn('\nBonus:',app.ResultText.insert.call_args.args[1])
        app.CountEntry.get=lambda:'100000';app.ResultText.reset_mock();ns['roll_dice'](app);ns['messagebox'].showerror.assert_called_once();app.ResultText.insert.assert_not_called()
    def test_text_conversions_unicode_and_empty_values(self):
        convert=self.namespace('text')['convert_text_value']
        self.assertEqual(convert('hello WORLD','camel'),'helloWorld');self.assertEqual(convert('caffè','upper'),'CAFFÈ');self.assertEqual(convert('A\n\nB','markdown'),'- A\n- B');self.assertEqual(convert('','camel'),'')
        with self.assertRaises(ValueError):convert('abc','unknown')
    def test_note_open_save_cancel_and_close_confirmation(self):
        ns=self.namespace('notes');text=Mock(get=lambda *a:'caffè');app=types.SimpleNamespace(Form1=Mock(),NoteText=text,root=Mock())
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'note.txt';ns['filedialog'].asksaveasfilename.return_value=str(path);ns['note_save'](app);self.assertEqual(path.read_text(),'caffè')
            ns['filedialog'].askopenfilename.return_value=str(path);ns['messagebox'].askyesno.return_value=False;ns['note_open'](app);text.delete.assert_not_called()
            ns['messagebox'].askyesno.return_value=True;ns['note_open'](app);text.insert.assert_called_with('1.0','caffè')
            ns['filedialog'].asksaveasfilename.return_value='';ns['note_save'](app);self.assertEqual(path.read_text(),'caffè')
        ns['messagebox'].askyesno.return_value=False;ns['note_close'](app);app.root.destroy.assert_not_called()
        ns['messagebox'].askyesno.return_value=True;ns['note_close'](app);app.root.destroy.assert_called_once()
    def test_new_project_cancellation_preserves_current_project(self):
        from studio import Studio
        original=new_project();fake=types.SimpleNamespace(project=original,dirty_guard=lambda:False)
        Studio.new_from_template(fake,instantiate('quiz'));self.assertIs(fake.project,original)
    def test_template_creation_resets_path_and_preserves_catalog_copy(self):
        from studio import Studio
        candidate=instantiate('quiz');fake=types.SimpleNamespace(dirty_guard=lambda:True,code=Mock(),refresh=Mock())
        Studio.new_from_template(fake,candidate)
        self.assertIsNone(fake.path);self.assertIsNot(fake.project,candidate);self.assertNotEqual(json.dumps(fake.project,sort_keys=True),fake.saved_state);fake.refresh.assert_called_once()
