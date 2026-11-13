"""Independent preview process with asynchronous interpreter checks and output."""
import os
from pathlib import Path
import queue
import subprocess
import threading
from tkinter import messagebox
from form_preview import preview_source
from components import requirements
from runtime_requirements import validate_interpreter
from i18n import tr

class PreviewMixin:
    def init_preview(self):
        self.preview_process=None;self.preview_spawned=None;self.preview_lock=threading.Lock();self.preview_starting=False;self.preview_serial=0;self.preview_cancel=threading.Event();self.preview_results=queue.Queue();self.preview_alive=True
        self.preview_timer=self.after(100,self.poll_preview);self.bind('<Destroy>',self.preview_destroy,add='+')

    def preview_form(self,dependencies_checked=False):
        if self.preview_starting:return
        self.commit_code()
        try:source,snapshot,placeholders=preview_source(self.project,self.form_index,self.current_container_pages())
        except Exception as exc:return messagebox.showerror(tr('Anteprima'),str(exc),parent=self)
        specs=requirements(snapshot)
        if specs and not dependencies_checked:return self.open_dependencies(specs=specs,on_ready=lambda:self.preview_form(True))
        self.stop_preview();self.preview_cancel=threading.Event();cancel=self.preview_cancel;serial=self.preview_serial
        python=self.config_data['python'];cwd=str(self.path.parent if self.path else Path(__file__).resolve().parent)
        script=Path(self.temp.name)/f'preview-{serial}.py';script.write_text(source,encoding='utf-8');self.preview_starting=True
        self.show_log(True);self.write_log(tr('Anteprima reale: eventi e codice di avvio del progetto esclusi.\n'))
        if placeholders:self.write_log(tr('Componenti mostrati come segnaposto: ')+', '.join(placeholders)+'\n')
        def worker():
            proc=None
            try:
                validate_interpreter(python)
                if cancel.is_set():return
                proc=subprocess.Popen([python,'-u',str(script)],cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace',env={**os.environ,'PYTHONUNBUFFERED':'1'})
                with self.preview_lock:
                    stopped=cancel.is_set()
                    if not stopped:self.preview_spawned=proc
                if stopped:proc.terminate();proc.wait(timeout=2);return
                self.preview_results.put((serial,proc,None))
                for line in proc.stdout:self.messages.put('[Preview] '+line)
                self.messages.put(tr('\n[Anteprima terminata: {code}]\n',code=proc.wait()))
            except Exception as exc:self.preview_results.put((serial,None,str(exc)))
            finally:
                if proc and proc.stdout:proc.stdout.close()
                try:
                    if proc and cancel.is_set() and proc.poll() is None:proc.kill();proc.wait()
                except OSError:pass
                with self.preview_lock:
                    if self.preview_spawned is proc:self.preview_spawned=None
                script.unlink(missing_ok=True)
        threading.Thread(target=worker,daemon=True).start()

    def poll_preview(self):
        if not self.preview_alive:return
        try:
            while True:
                serial,proc,error=self.preview_results.get_nowait()
                if serial!=self.preview_serial:
                    if proc and proc.poll() is None:
                        try:proc.terminate()
                        except OSError:pass
                    continue
                self.preview_starting=False
                if error:self.write_log(tr('Errore anteprima: ')+error+'\n')
                else:self.preview_process=proc
        except queue.Empty:pass
        self.preview_timer=self.after(100,self.poll_preview)

    def stop_preview(self):
        self.preview_serial+=1;self.preview_cancel.set();self.preview_starting=False
        with self.preview_lock:
            proc=self.preview_spawned;self.preview_spawned=None
        self.preview_process=None
        if proc and proc.poll() is None:
            try:proc.terminate();proc.wait(timeout=1)
            except subprocess.TimeoutExpired:proc.kill();proc.wait()
            except OSError:pass

    def preview_destroy(self,event):
        if event.widget is self:
            self.preview_alive=False;self.stop_preview()
            try:self.after_cancel(self.preview_timer)
            except Exception:pass
