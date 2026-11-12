import json
from pathlib import Path
import queue
import sys
import types
import unittest
from unittest.mock import Mock,patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core import new_project,generate,EVENTS
from components import BUILTINS,requirements
from visualtk_runtime import FileDropZone,FileBrowserButton,MessageButton,YouTubePlayer,NativeWebButton

class IntegrationTests(unittest.TestCase):
    def test_native_drop_preserves_spaces_and_multiple_files(self):
        zone=types.SimpleNamespace(tk=types.SimpleNamespace(splitlist=lambda data:('/tmp/una foto.jpg','/tmp/b.png')),caption=Mock(),event_generate=Mock())
        result=FileDropZone.receive(zone,types.SimpleNamespace(data='{one} {two}',action='copy'))
        self.assertEqual(zone.paths,['/tmp/una foto.jpg','/tmp/b.png']);self.assertEqual(result,'copy');zone.event_generate.assert_called_once_with('<<FilesDropped>>',when='tail')
    def test_filedialog_multiple_selection(self):
        button=types.SimpleNamespace(advanced=False,mode='multiple',event_generate=Mock())
        with patch('visualtk_runtime.filedialog.askopenfilenames',return_value=('/a','/b')):FileBrowserButton.choose(button)
        self.assertEqual(button.paths,['/a','/b']);button.event_generate.assert_called_once()
    def test_dialog_returns_result(self):
        button=types.SimpleNamespace(mode='confirm',title='Conferma',message='Procedere?',event_generate=Mock())
        with patch('visualtk_runtime.messagebox.askyesno',return_value=True):MessageButton.show(button)
        self.assertIs(button.result,True)
    def test_theme_and_alternative_backend_dependencies(self):
        p=new_project();p['theme']='darkly';p['forms'][0]['widgets']=[{'name':'YT','kind':'YouTubePlayer','x':0,'y':0,'width':400,'height':250,'props':{'backend':'pytubefix'},'events':{}}]
        specs=requirements(p);self.assertIn('pytubefix',specs);self.assertIn('ttkbootstrap>=1.10',specs)
        source=generate(p);self.assertIn("ttkbootstrap.Style(theme='darkly')",source);self.assertIn('multiprocessing.freeze_support()',source)
    def test_youtube_resolves_without_downloading(self):
        class YDL:
            def __init__(self,options):self.options=options
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def extract_info(self,url,download):
                if download:raise AssertionError('Non deve scaricare')
                return {'url':'https://stream.example/video','http_headers':{'User-Agent':'Test'}}
        class ImmediateThread:
            def __init__(self,target,**kw):self.target=target
            def start(self):self.target()
        panel=types.SimpleNamespace(busy=False,address=types.SimpleNamespace(get=lambda:'https://www.youtube.com/watch?v=example'),backend='yt-dlp',status=Mock(),results=queue.Queue(),poll=Mock())
        with patch.dict(sys.modules,{'yt_dlp':types.SimpleNamespace(YoutubeDL=YDL)}),patch('visualtk_runtime.threading.Thread',ImmediateThread):YouTubePlayer.play(panel)
        state,data=panel.results.get_nowait();self.assertEqual(state,'ok');self.assertEqual(data[1],{'User-Agent':'Test'})
    def test_native_web_uses_spawn_and_own_main_thread(self):
        button=types.SimpleNamespace(title='Web',url='https://www.python.org',children_processes=[]);process=Mock();context=Mock();context.Process.return_value=process
        with patch('multiprocessing.get_context',return_value=context) as get:NativeWebButton.open(button)
        get.assert_called_once_with('spawn');process.start.assert_called_once();self.assertEqual(button.children_processes,[process])
    def test_descriptors_and_events_serialize(self):
        p=new_project()
        for kind,d in BUILTINS.items():
            p['forms'][0]['widgets'].append({'name':kind+'1','kind':kind,'x':10,'y':10,'width':400,'height':250,'props':d['defaults'].copy(),'events':{name:'pass' for name in EVENTS}})
        restored=json.loads(json.dumps(p));compile(generate(restored),'all.py','exec');self.assertIn('<<FilesDropped>>',generate(restored))
