"""Latest-request client. Analysis and subprocess reads never run on Tk's thread."""
from i18n import tr
import json
from pathlib import Path
import queue
import subprocess
import threading
PREFIX='VTS_INTELLISENSE '

class AnalysisClient:
    def __init__(self,worker=None,timeout=15):
        self.worker=Path(worker or Path(__file__).with_name('intellisense_worker.py'));self.timeout=timeout;self.requests=queue.Queue(maxsize=1);self.results=queue.Queue();self.closed=False;self.process=None;self.python=None;self.sequence=0
        self.process_lock=threading.Lock()
        self.thread=threading.Thread(target=self.run,daemon=True);self.thread.start()
    def submit(self,python,request):
        if self.closed:return None
        if request.get('action')=='detail' and not self.requests.empty():return None
        self.sequence+=1;request={**request,'id':self.sequence}
        try:self.requests.get_nowait()
        except queue.Empty:pass
        self.requests.put_nowait((python,request));return self.sequence
    def stop_process(self):
        with self.process_lock:
            process=self.process;self.process=None
        if process and process.poll() is None:
            try:process.terminate()
            except OSError:return
            def kill():
                try:
                    if process.poll() is None:process.kill()
                except OSError:pass
            timer=threading.Timer(1,kill);timer.daemon=True;timer.start()
    def start(self,python):
        self.stop_process()
        process=subprocess.Popen([python,'-u',str(self.worker)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,encoding='utf-8',errors='replace',bufsize=1)
        self.process=process;self.python=python;responses=queue.Queue()
        def read():
            try:
                for line in process.stdout:
                    if line.startswith(PREFIX):
                        try:responses.put(json.loads(line[len(PREFIX):]))
                        except ValueError:pass
            finally:
                process.stdout.close()
                try:process.stdin.close()
                except (OSError,ValueError):pass
                try:process.wait(timeout=2)
                except subprocess.TimeoutExpired:pass
                responses.put({'transport_error':tr('Motore di analisi terminato.')})
        threading.Thread(target=read,daemon=True).start();self.responses=responses
        if self.closed:self.stop_process()
    def run(self):
        while not self.closed:
            item=self.requests.get()
            if item is None:break
            python,request=item
            try:
                if self.closed:break
                if self.process is None or self.process.poll() is not None or python!=self.python:self.start(python)
                if self.closed:break
                self.process.stdin.write(json.dumps(request,ensure_ascii=False)+'\n');self.process.stdin.flush()
                result=self.responses.get(timeout=self.timeout)
                if 'transport_error' in result:raise RuntimeError(result['transport_error'])
                self.results.put(result)
            except Exception as exc:
                self.stop_process();self.results.put({'id':request['id'],'action':request.get('action','complete'),'error':tr('Analisi non disponibile o troppo lenta: ')+str(exc),'items':[]})
        self.stop_process()
    def close(self):
        if self.closed:return
        self.closed=True;self.stop_process()
        try:self.requests.get_nowait()
        except queue.Empty:pass
        self.requests.put_nowait(None)
