import copy
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import types
import unittest
from unittest.mock import Mock,patch
from core import new_project,generate,validate
from components import BUILTINS,requirements
from dependency_manager import component_requirements
from library_catalog import packaging_flags
from productivity_specs import PRODUCTIVITY_COMPONENTS,validate_productivity
from service_backends import atomic_output,excel_open,excel_save,pdf_open,pdf_extract,pdf_merge,llm_call,safe_error,midi_play,print_document,cloud_endpoint,WebDAVStorage,S3Storage,DriveStorage
from productivity_runtime import _ServicePanel,PrintDocument
from code_assist import examples

class DocumentBackendTests(unittest.TestCase):
    def setUp(self):self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def test_excel_round_trip_multiple_sheets_and_formula(self):
        from openpyxl import Workbook
        book=Workbook();book.active.title='Data';book.active.append(['Name','Value']);book.active.append(['Alpha',42]);book.active['C2']='=B2*2';book.create_sheet('Results')['A1']='Saved'
        target=self.root/'book.xlsx';excel_save(book,target);loaded=excel_open(target)
        self.assertEqual(loaded['Data']['B2'].value,42);self.assertEqual(loaded['Data']['C2'].value,'=B2*2');self.assertEqual(loaded['Results']['A1'].value,'Saved');loaded.close()
    def test_excel_formats_and_vba_guard(self):
        with self.assertRaises(ValueError):excel_open(self.root/'old.xls')
        book=Mock();book.vba_archive=object()
        with self.assertRaises(ValueError):excel_save(book,self.root/'macros.xlsx')
        book.save.assert_not_called()
    def make_pdf(self,name,pages):
        from pypdf import PdfWriter
        writer=PdfWriter()
        for _ in range(pages):writer.add_blank_page(width=100,height=100)
        path=self.root/name;writer.write(path);writer.close();return path
    def test_pdf_merge_page_extraction_and_bounds(self):
        first=self.make_pdf('first.pdf',2);second=self.make_pdf('second.pdf',1);merged=self.root/'merged.pdf'
        pdf_merge([first,second],merged);reader=pdf_open(merged);self.assertEqual(len(reader.pages),3)
        selected=self.root/'selected.pdf';pdf_extract(reader,[2,0],selected);self.assertEqual(len(pdf_open(selected).pages),2)
        with self.assertRaises(ValueError):pdf_extract(reader,[3],self.root/'bad.pdf')
        self.assertFalse((self.root/'bad.pdf').exists())
    def test_encrypted_pdf_requires_password(self):
        from pypdf import PdfWriter
        writer=PdfWriter();writer.add_blank_page(width=100,height=100);writer.encrypt('secret',algorithm='AES-256');target=self.root/'encrypted.pdf';writer.write(target);writer.close()
        with self.assertRaises(ValueError):pdf_open(target,'wrong')
        self.assertEqual(len(pdf_open(target,'secret').pages),1)
    def test_atomic_failure_preserves_original(self):
        target=self.root/'safe.txt';target.write_text('original')
        def fail(path):path.write_text('partial');raise OSError('disk error')
        with self.assertRaises(OSError):atomic_output(target,fail)
        self.assertEqual(target.read_text(),'original');self.assertEqual(list(self.root.iterdir()),[target])

class ProviderTests(unittest.TestCase):
    def sdk(self,response,provider):
        client=Mock();client.__enter__=Mock(return_value=client);client.__exit__=Mock(return_value=False)
        if provider=='openai':client.responses.create.return_value=response
        else:client.messages.create.return_value=response
        return client
    def test_openai_responses_api_contract(self):
        response=types.SimpleNamespace(output_text='Hello',usage=types.SimpleNamespace(model_dump=lambda:{'output_tokens':2}));client=self.sdk(response,'openai');factory=Mock(return_value=client)
        with patch.dict(sys.modules,{'openai':types.SimpleNamespace(OpenAI=factory)}):result=llm_call('openai','test-model','hello','OPENAI_API_KEY',128,api_key='session-secret')
        self.assertEqual(result['text'],'Hello');self.assertEqual(result['usage']['output_tokens'],2);client.responses.create.assert_called_once_with(model='test-model',input='hello',max_output_tokens=128);factory.assert_called_once_with(api_key='session-secret',timeout=60,max_retries=1)
    def test_claude_messages_api_contract(self):
        response=types.SimpleNamespace(content=[types.SimpleNamespace(type='text',text='Claude answer')],usage=types.SimpleNamespace(model_dump=lambda:{}));client=self.sdk(response,'anthropic')
        with patch.dict(sys.modules,{'anthropic':types.SimpleNamespace(Anthropic=Mock(return_value=client))}):result=llm_call('anthropic','claude-test','hello','ANTHROPIC_API_KEY',64,api_key='secret')
        self.assertEqual(result['text'],'Claude answer');client.messages.create.assert_called_once_with(model='claude-test',max_tokens=64,messages=[{'role':'user','content':'hello'}])
    def test_gemini_generate_content_contract(self):
        client=self.sdk(None,'openai');client.models.generate_content.return_value=types.SimpleNamespace(text='Gemini answer',usage_metadata=None);factory=Mock(return_value=client)
        fake=types.ModuleType('google.genai');fake.Client=factory
        google=types.ModuleType('google');google.genai=fake
        with patch.dict(sys.modules,{'google':google,'google.genai':fake}):result=llm_call('gemini','gemini-test','hello','GEMINI_API_KEY',64,api_key='secret')
        self.assertEqual(result['text'],'Gemini answer');client.models.generate_content.assert_called_once_with(model='gemini-test',contents='hello',config={'max_output_tokens':64});factory.assert_called_once_with(api_key='secret',http_options={'timeout':60000})
    def test_missing_key_and_model_fail_before_call(self):
        with patch.dict(os.environ,{},clear=True),self.assertRaises(ValueError):llm_call('openai','model','hello','OPENAI_API_KEY')
        with self.assertRaises(ValueError):llm_call('openai','','hello','OPENAI_API_KEY',api_key='test')
    def test_secret_redaction_environment_and_session(self):
        with patch.dict(os.environ,{'OPENAI_API_KEY':'environment-secret'}):
            message=safe_error('environment-secret session-secret access_token=hidden',['OPENAI_API_KEY'],['session-secret'])
        for secret in ['environment-secret','session-secret','hidden']:self.assertNotIn(secret,message)
    def test_model_listing_does_not_generate_text(self):
        client=self.sdk(None,'openai');client.models.list.return_value=[types.SimpleNamespace(id='model-one')]
        with patch.dict(sys.modules,{'openai':types.SimpleNamespace(OpenAI=Mock(return_value=client))}):result=llm_call('openai','','','OPENAI_API_KEY',models=True,api_key='test')
        self.assertEqual(result,['model-one']);client.responses.create.assert_not_called()

class DeviceAndCloudTests(unittest.TestCase):
    def test_midi_messages_and_reset_without_hardware(self):
        output=Mock();output.__enter__=Mock(return_value=output);output.__exit__=Mock(return_value=False)
        message=types.SimpleNamespace(time=0,is_meta=False);backend=Mock();backend.open_output.return_value=output
        fake=types.SimpleNamespace(MidiFile=lambda path:[message],Backend=lambda name:backend)
        with patch.dict(sys.modules,{'mido':fake}):result=midi_play('song.mid','Synth',threading.Event(),threading.Event())
        self.assertEqual(result,'finished');output.send.assert_called_once_with(message);output.reset.assert_called_once()
    def test_stop_does_not_send_pending_midi(self):
        output=Mock();output.__enter__=Mock(return_value=output);output.__exit__=Mock(return_value=False);backend=Mock();backend.open_output.return_value=output;stop=threading.Event();stop.set()
        fake=types.SimpleNamespace(MidiFile=lambda path:[types.SimpleNamespace(time=1,is_meta=False)],Backend=lambda name:backend)
        with patch.dict(sys.modules,{'mido':fake}):self.assertEqual(midi_play('song.mid','Synth',stop,threading.Event()),'stopped')
        output.send.assert_not_called();output.reset.assert_called_once()
    def test_printing_uses_argument_list_and_submission_only(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'test ; file.pdf';path.write_bytes(b'test')
            with patch('service_backends.sys.platform','darwin'),patch('service_backends.subprocess.run',return_value=types.SimpleNamespace(stdout='request id is test-1')) as run:
                self.assertIn('test-1',print_document(path,'printer',2))
            self.assertEqual(run.call_args.args[0],['lp','-d','printer','-n','2','--',str(path.resolve())]);self.assertNotIn('shell',run.call_args.kwargs)
    def test_print_confirmation_cancellation_submits_nothing(self):
        panel=types.SimpleNamespace(path_var=types.SimpleNamespace(get=lambda:'report.pdf'),printer_var=types.SimpleNamespace(get=lambda:''),copies_var=types.SimpleNamespace(get=lambda:1),_start=Mock())
        with patch('productivity_runtime.messagebox.askyesno',return_value=False):self.assertFalse(PrintDocument.print_file(panel))
        panel._start.assert_not_called()
    def test_cloud_endpoints_and_webdav_path_boundary(self):
        for endpoint in ['http://example.com','https://user:secret@example.com','https://example.com?token=secret']:
            with self.assertRaises(ValueError):cloud_endpoint(endpoint)
        client=WebDAVStorage.__new__(WebDAVStorage);client.base='https://example.com/dav/'
        self.assertEqual(client.url('folder/test file.txt'),'https://example.com/dav/folder/test%20file.txt')
        with self.assertRaises(ValueError):client.url('../outside.txt')
    def test_drive_list_is_scoped_and_injection_rejected(self):
        client=DriveStorage.__new__(DriveStorage);client.service=Mock();client.service.files.return_value.list.return_value.execute.return_value={'files':[{'id':'123','name':'test'}]}
        self.assertEqual(client.list_files('root')[0]['name'],'test');self.assertIn("'root' in parents",client.service.files.return_value.list.call_args.kwargs['q'])
        with self.assertRaises(ValueError):client.list_files("' or true")
    def test_s3_upload_preserves_existing_objects(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'report.txt';path.write_text('test');client=S3Storage.__new__(S3Storage);client.client=Mock();client.bucket='bucket'
            result=client.upload(path,'reports');self.assertEqual(result['id'],'reports/report.txt');self.assertEqual(client.client.put_object.call_args.kwargs['IfNoneMatch'],'*')

class ProductivityModelTests(unittest.TestCase):
    def test_all_components_export_without_internal_module_imports(self):
        self.assertEqual(set(PRODUCTIVITY_COMPONENTS),{'MIDIPlayer','ExcelWorkbook','PDFDocument','PrintDocument','CloudStorage','LLMClient'})
        p=new_project()
        for kind,desc in PRODUCTIVITY_COMPONENTS.items():p['forms'][0]['widgets'].append(dict(name=kind+'1',kind=kind,x=0,y=0,width=600,height=300,props=copy.deepcopy(desc['defaults']),events={}))
        source=generate(p);compile(source,'app.py','exec');self.assertNotIn('from service_backends import ',source);self.assertNotIn('from productivity_runtime import ',source)
        for kind in PRODUCTIVITY_COMPONENTS:self.assertIn('class '+kind+'(',source)
    def test_dependencies_follow_provider_for_insert_and_export(self):
        self.assertEqual(component_requirements(new_project(),'LLMClient',{'provider':'gemini'}),['google-genai>=1,<3'])
        self.assertEqual(component_requirements(new_project(),'CloudStorage',{'provider':'s3'}),['boto3>=1.35,<2'])
        p=new_project();p['forms'][0]['widgets']=[dict(name='AI1',kind='LLMClient',x=0,y=0,width=300,height=200,props={'provider':'anthropic'},events={})]
        self.assertIn('anthropic>=0.70,<2',requirements(p));self.assertNotIn('openai>=2,<4',requirements(p));self.assertIn('--collect-all=anthropic',packaging_flags(p))
    def test_credentials_are_not_valid_project_properties(self):
        for props in [{'api_key':'secret'},{'api_key_env':'sk-secret'},{'password':'secret'}]:
            with self.assertRaises(ValueError):validate_productivity('LLMClient',props)
    def test_context_examples_use_async_apis(self):
        for kind in PRODUCTIVITY_COMPONENTS:
            obj=dict(name='Control1',kind=kind,props=copy.deepcopy(PRODUCTIVITY_COMPONENTS[kind]['defaults']));p=new_project();p['forms'][0]['widgets']=[obj]
            snippets='\n'.join(row[1] for row in examples(obj,p));self.assertNotIn('.configure(provider=',snippets)
    def test_job_errors_return_through_queue_without_tk_in_worker(self):
        import queue,time
        panel=types.SimpleNamespace(busy=False,error='',status=Mock(),_tasks=queue.Queue(),_secret_names=[],_secret_values=['secret'])
        def fail():raise RuntimeError('error secret')
        self.assertTrue(_ServicePanel._start(panel,fail));message=panel._tasks.get(timeout=2);self.assertEqual(message[0],'error');self.assertNotIn('secret',message[1]);self.assertTrue(panel.busy)
