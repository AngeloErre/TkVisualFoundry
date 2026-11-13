"""Lazy document, MIDI, cloud and LLM operations. No network activity at import time."""
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
from urllib.parse import urlsplit,urljoin,quote,unquote


def atomic_output(destination,write):
    target=Path(destination).expanduser().resolve()
    if not target.parent.is_dir():raise ValueError('Destination directory does not exist')
    handle=tempfile.NamedTemporaryFile(dir=target.parent,prefix='.visualtk-',suffix=target.suffix,delete=False);temporary=Path(handle.name);handle.close()
    try:write(temporary);temporary.replace(target)
    finally:temporary.unlink(missing_ok=True)
    return str(target)


def env_value(name,required=True):
    if not isinstance(name,str) or not name.isidentifier():raise ValueError('Enter an environment variable NAME, not its secret value')
    value=os.environ.get(name,'')
    if required and not value:raise ValueError('Set environment variable '+name+' before starting the application')
    return value


def safe_error(error,names=(),values=()):
    text=str(error)
    for value in [os.environ.get(name,'') for name in names]+list(values):
        if value:text=text.replace(value,'[REDACTED]')
    return re.sub(r'(?i)(access_token|api_key|refresh_token)=([^&\s]+)',r'\1=[REDACTED]',text)[:2500]


def excel_open(path):
    from openpyxl import load_workbook
    path=Path(path)
    if path.suffix.lower() not in ('.xlsx','.xlsm'):raise ValueError('Supported Excel formats: .xlsx and .xlsm')
    return load_workbook(path,keep_vba=path.suffix.lower()=='.xlsm',keep_links=True)


def excel_save(book,path):
    suffix=Path(path).suffix.lower()
    if suffix not in ('.xlsx','.xlsm'):raise ValueError('Choose .xlsx or .xlsm')
    if book.vba_archive is not None and suffix!='.xlsm':raise ValueError('Use .xlsm to preserve VBA content')
    return atomic_output(path,book.save)


def pdf_open(path,password=None):
    from pypdf import PdfReader
    # Keep an in-memory source so Windows can replace/save files after reading.
    reader=PdfReader(io.BytesIO(Path(path).read_bytes()))
    if reader.is_encrypted and not reader.decrypt(password or ''):raise ValueError('PDF password required or incorrect')
    return reader


def pdf_extract(reader,pages,destination):
    from pypdf import PdfWriter
    selected=list(pages)
    if not selected or any(not isinstance(i,int) or i<0 or i>=len(reader.pages) for i in selected):raise ValueError('Invalid page indexes (zero-based)')
    writer=PdfWriter()
    try:
        for index in selected:writer.add_page(reader.pages[index])
        return atomic_output(destination,lambda path:writer.write(str(path)))
    finally:writer.close()


def pdf_merge(paths,destination):
    from pypdf import PdfWriter
    paths=list(paths)
    if not paths:raise ValueError('Select at least one PDF')
    writer=PdfWriter()
    try:
        for path in paths:writer.append(pdf_open(path))
        return atomic_output(destination,lambda path:writer.write(str(path)))
    finally:writer.close()


def midi_ports():
    import mido
    return mido.Backend('mido.backends.rtmidi').get_output_names()


def midi_play(path,port_name,stop,pause,on_started=lambda:None):
    import mido
    if not port_name:raise ValueError('Choose a MIDI output connected to a synthesizer')
    midi=mido.MidiFile(path)
    with mido.Backend('mido.backends.rtmidi').open_output(port_name) as output:
        on_started()
        try:
            for message in midi:
                remaining=message.time;was_paused=False
                while remaining>0 or pause.is_set():
                    if stop.is_set():return 'stopped'
                    if pause.is_set() and not was_paused:output.reset();was_paused=True
                    if not pause.is_set():was_paused=False
                    start=time.monotonic();stop.wait(min(.02,remaining) if remaining>0 and not pause.is_set() else .02)
                    if not pause.is_set():remaining-=time.monotonic()-start
                if stop.is_set():return 'stopped'
                if not message.is_meta:output.send(message)
            return 'finished'
        finally:output.reset()


def open_document(path):
    path=str(Path(path).expanduser().resolve())
    if not Path(path).is_file():raise FileNotFoundError(path)
    if sys.platform=='darwin':subprocess.Popen(['open',path])
    elif sys.platform=='win32':os.startfile(path)
    else:subprocess.Popen(['xdg-open',path])
    return path


def print_document(path,printer='',copies=1):
    path=str(Path(path).expanduser().resolve());copies=int(copies)
    if not Path(path).is_file():raise FileNotFoundError(path)
    if not 1<=copies<=100:raise ValueError('Copies must be between 1 and 100')
    if sys.platform=='win32':
        if printer or copies!=1:raise ValueError('Windows uses the default associated application/printer. Set copies and printer in that application.')
        os.startfile(path,'print');return 'Submitted to the associated Windows print application'
    result=subprocess.run(['lp',*(['-d',printer] if printer else []),'-n',str(copies),'--',path],capture_output=True,text=True,timeout=30,check=True)
    return result.stdout.strip()


def llm_call(provider,model,prompt,key_env,max_tokens=1024,models=False,api_key=None):
    key=api_key or env_value(key_env)
    if provider not in ('openai','anthropic','gemini'):raise ValueError('Provider must be openai, anthropic or gemini')
    if not models and (not model.strip() or not prompt.strip()):raise ValueError('Choose a model and enter a prompt')
    limit=int(max_tokens)
    if not 1<=limit<=32768:raise ValueError('Output token limit must be 1–32768')
    from itertools import islice
    if provider=='openai':
        from openai import OpenAI
        with OpenAI(api_key=key,timeout=60,max_retries=1) as client:
            if models:return [item.id for item in islice(client.models.list(),100)]
            response=client.responses.create(model=model,input=prompt,max_output_tokens=limit)
            return {'text':response.output_text,'usage':response.usage.model_dump() if response.usage else {},'model':model,'provider':provider}
    if provider=='anthropic':
        from anthropic import Anthropic
        with Anthropic(api_key=key,timeout=60,max_retries=1) as client:
            if models:return [item.id for item in islice(client.models.list(),100)]
            response=client.messages.create(model=model,max_tokens=limit,messages=[{'role':'user','content':prompt}])
            return {'text':'\n'.join(block.text for block in response.content if block.type=='text'),'usage':response.usage.model_dump(),'model':model,'provider':provider}
    from google import genai
    with genai.Client(api_key=key,http_options={'timeout':60000}) as client:
        if models:return [item.name.removeprefix('models/') for item in islice(client.models.list(),100) if item.name]
        response=client.models.generate_content(model=model,contents=prompt,config={'max_output_tokens':limit})
        return {'text':response.text or '', 'usage':response.usage_metadata.model_dump() if response.usage_metadata else {},'model':model,'provider':provider}


class DriveStorage:
    def __init__(self,client_env='GOOGLE_OAUTH_CLIENT_FILE',token_env='GOOGLE_TOKEN_FILE',auth_mode='desktop',scope='app',client_file=None):
        from googleapiclient.discovery import build
        import google_auth_httplib2
        import httplib2
        scopes=['https://www.googleapis.com/auth/drive.file' if scope=='app' else 'https://www.googleapis.com/auth/drive']
        if auth_mode=='adc':
            import google.auth
            credentials,_=google.auth.default(scopes=scopes)
        else:
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request
            from google_auth_oauthlib.flow import InstalledAppFlow
            configured=env_value(token_env,False)
            token=Path(configured).expanduser() if configured else Path.home()/'.visualtkstudio-credentials'/('drive-'+scope+'.json')
            credentials=Credentials.from_authorized_user_file(str(token)) if token.exists() else None
            if credentials and not credentials.has_scopes(scopes):credentials=None
            if credentials and credentials.expired and credentials.refresh_token:credentials.refresh(Request())
            if not credentials or not credentials.valid:
                flow=InstalledAppFlow.from_client_secrets_file(client_file or env_value(client_env),scopes)
                credentials=flow.run_local_server(port=0,timeout_seconds=120)
            token.parent.mkdir(parents=True,exist_ok=True)
            atomic_output(token,lambda path:path.write_text(credentials.to_json(),encoding='utf-8'))
            try:token.chmod(0o600)
            except OSError:pass
        http=google_auth_httplib2.AuthorizedHttp(credentials,http=httplib2.Http(timeout=30))
        self.service=build('drive','v3',http=http,cache_discovery=False)
    def list_files(self,folder='root',limit=100):
        if not re.fullmatch(r'[A-Za-z0-9_-]+',folder):raise ValueError('Use a Drive folder ID')
        result=[];token=None
        while len(result)<limit:
            data=self.service.files().list(q="trashed = false and '"+folder+"' in parents",pageSize=min(100,limit-len(result)),pageToken=token,fields='nextPageToken,files(id,name,mimeType,size)').execute()
            result.extend(data.get('files',[]));token=data.get('nextPageToken')
            if not token:break
        return result
    def upload(self,path,folder='root'):
        from googleapiclient.http import MediaFileUpload
        if not re.fullmatch(r'[A-Za-z0-9_-]+',folder):raise ValueError('Use a Drive folder ID')
        request=self.service.files().create(body={'name':Path(path).name,'parents':[folder]},media_body=MediaFileUpload(str(path),resumable=True),fields='id,name,mimeType')
        result=None
        while result is None:_,result=request.next_chunk()
        return result
    def download(self,file_id,destination):
        from googleapiclient.http import MediaIoBaseDownload
        meta=self.service.files().get(fileId=file_id,fields='mimeType').execute();mime=meta['mimeType']
        if mime=='application/vnd.google-apps.folder':raise ValueError('Select a file, not a Drive folder')
        request=self.service.files().export_media(fileId=file_id,mimeType='application/pdf') if mime.startswith('application/vnd.google-apps.') else self.service.files().get_media(fileId=file_id)
        def write(path):
            with path.open('wb') as stream:
                download=MediaIoBaseDownload(stream,request);done=False
                while not done:_,done=download.next_chunk()
        return atomic_output(destination,write)


def cloud_endpoint(value):
    parts=urlsplit(value)
    if parts.username or parts.password or parts.query or parts.fragment:raise ValueError('Endpoint must not embed credentials, query strings or fragments')
    if parts.scheme!='https' and not (parts.scheme=='http' and parts.hostname in ('localhost','127.0.0.1','::1')):raise ValueError('Use an HTTPS endpoint (HTTP allowed only for localhost)')
    if not parts.netloc:raise ValueError('Endpoint host is required')
    return value.rstrip('/')+'/'


class S3Storage:
    def __init__(self,bucket,endpoint_env='S3_ENDPOINT_URL',access_key=None,secret_key=None,session_token=None,endpoint=None):
        import boto3
        from botocore.config import Config
        if not re.fullmatch(r'[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]',bucket):raise ValueError('Enter a valid S3 bucket name')
        endpoint=endpoint or env_value(endpoint_env,False)
        session={}
        if access_key or secret_key:
            if not access_key or not secret_key:raise ValueError('Both access key and secret key are required')
            session={'aws_access_key_id':access_key,'aws_secret_access_key':secret_key,'aws_session_token':session_token}
        self.client=boto3.client('s3',**session,endpoint_url=cloud_endpoint(endpoint) if endpoint else None,config=Config(connect_timeout=15,read_timeout=45,retries={'max_attempts':2}));self.bucket=bucket
    def list_files(self,folder='',limit=100):
        result=[]
        for page in self.client.get_paginator('list_objects_v2').paginate(Bucket=self.bucket,Prefix=folder,PaginationConfig={'MaxItems':limit}):
            result.extend({'id':item['Key'],'name':item['Key'],'size':item['Size']} for item in page.get('Contents',[]))
        return result[:limit]
    def upload(self,path,folder=''):
        key=folder.rstrip('/')+('/' if folder else '')+Path(path).name
        with open(path,'rb') as stream:self.client.put_object(Bucket=self.bucket,Key=key,Body=stream,IfNoneMatch='*')
        return {'id':key,'name':key}
    def download(self,key,destination):return atomic_output(destination,lambda path:self.client.download_file(self.bucket,key,str(path)))


class WebDAVStorage:
    def __init__(self,url_env='WEBDAV_URL',user_env='WEBDAV_USER',password_env='WEBDAV_PASSWORD',url=None,username=None,password=None):
        import requests
        self.base=cloud_endpoint(url or env_value(url_env));self.session=requests.Session();self.session.auth=(username or env_value(user_env),password or env_value(password_env))
    def url(self,key):
        candidate=urljoin(self.base,quote(key.lstrip('/'),safe='/'))
        if not candidate.startswith(self.base):raise ValueError('Path outside the configured WebDAV root')
        return candidate
    def list_files(self,folder='',limit=100):
        from xml.etree import ElementTree
        base=self.url(folder);response=self.session.request('PROPFIND',base,headers={'Depth':'1'},timeout=30);response.raise_for_status();tree=ElementTree.fromstring(response.content);result=[]
        for item in tree.findall('{DAV:}response'):
            href=item.findtext('{DAV:}href','');absolute=urljoin(base,href)
            if not absolute.startswith(self.base) or absolute.rstrip('/')==base.rstrip('/'):continue
            if item.find('.//{DAV:}collection') is not None:continue
            key=unquote(absolute[len(self.base):]);result.append({'id':key,'name':Path(key).name})
            if len(result)>=limit:break
        return result
    def upload(self,path,folder=''):
        key=folder.rstrip('/')+('/' if folder else '')+Path(path).name
        # Do not replace existing cloud content silently.
        with open(path,'rb') as stream:
            result=self.session.put(self.url(key),data=stream,headers={'If-None-Match':'*'},timeout=45);result.raise_for_status()
        return {'id':key,'name':key}
    def download(self,key,destination):
        def write(path):
            with self.session.get(self.url(key),stream=True,timeout=45) as response:
                response.raise_for_status()
                with path.open('wb') as stream:
                    for chunk in response.iter_content(1024*1024):stream.write(chunk)
        return atomic_output(destination,write)
