"""IDE-only bounded variable snapshots. Never evaluate expressions or user reprs."""
import json
import os
from pathlib import Path
import sys
import threading
import time
import types
import weakref


def value_node(name,value,budget=None,depth=0,seen=None):
    if budget is None:budget=[1500]
    if seen is None:seen=set()
    budget[0]-=1;t=type(value)
    typename=type.__dict__['__name__'].__get__(t)
    node={'name':str(name)[:180],'type':typename[:100],'value':'','children':[]}
    if t is str:node['value']=repr(value[:400])+(' …' if len(value)>400 else '')
    elif t in (int,float,bool,type(None)):
        try:node['value']=str(value)[:400]
        except ValueError:node['value']='<large integer>'
    elif t is bytes:node['value']=repr(value[:80])+(' …' if len(value)>80 else '')
    elif t in (list,tuple,dict,set,frozenset):
        node['value']=f'{typename} ({len(value)})'
        if id(value) in seen:node['value']+=' <cycle>';return node
        if depth>=3 or budget[0]<=0:node['value']+=' …';return node
        seen=seen|{id(value)}
        try:
            import itertools
            items=list(itertools.islice(value.items() if t is dict else enumerate(value),31))
            for key,item in items[:30]:
                if budget[0]<=0:break
                label=repr(key)[:100] if type(key) in (str,int,float,bool,type(None)) else '<key>'
                node['children'].append(value_node(label,item,budget,depth+1,seen))
            if len(value)>len(node['children']):node['value']+=' …'
        except (RuntimeError,ValueError):node['value']+=' <changed during sample>'
    else:node['value']='<'+typename[:100]+' object>'
    return node


def instance_attributes(value):
    t=type(value)
    for base in type.__dict__['__mro__'].__get__(t):
        descriptor=type.__dict__['__dict__'].__get__(base).get('__dict__')
        if descriptor is not None:
            if type(descriptor) is types.GetSetDescriptorType:return descriptor.__get__(value,t)
            return {}
    return {}


def variable_nodes(values,budget=None):
    budget=budget if budget is not None else [1500];nodes=[]
    try:
        import itertools
        if issubclass(type(values),dict):items=list(itertools.islice(dict.items(values),512))
        elif type(values) is types.FrameLocalsProxyType:items=list(itertools.islice(types.FrameLocalsProxyType.items(values),512))
        else:return nodes
    except RuntimeError:return nodes
    for name,value in items:
        if type(name) is not str or (name.startswith('__') and name.endswith('__')):continue
        if budget[0]<=0:break
        nodes.append(value_node(name,value,budget))
    return nodes


class Inspector:
    def __init__(self,target,output,tracked=()):
        self.target=os.path.realpath(target);self.tracked={self.target,*map(os.path.realpath,tracked),*map(os.path.abspath,tracked)}
        self.output=Path(output);self.stop_event=threading.Event();self.paused=None;self.paused_stack=[];self.selected_index=None;self.pause_id=None;self.last_locals=None;self.modules={};self.app=None;self.sequence=0;self.lock=threading.RLock();self.last_return=0;self.last_return_code=None
    def profile(self,frame,event,arg):
        if event not in ('call','return') or frame.f_code.co_filename not in self.tracked:return
        with self.lock:
            filename=os.path.realpath(frame.f_code.co_filename);self.modules[filename]=frame.f_globals
            obj=frame.f_locals.get('self');app_class=frame.f_globals.get('Application')
            if filename==self.target and app_class is not None and type(obj) is app_class:
                try:self.app=weakref.ref(obj)
                except TypeError:pass
            if event=='return' and frame.f_code.co_name!='<module>' and (frame.f_code is not self.last_return_code or time.monotonic()-self.last_return>=0.1):
                self.last_return=time.monotonic();self.last_return_code=frame.f_code;self.last_locals={'file':filename,'function':frame.f_code.co_name,'line':frame.f_lineno,'values':variable_nodes(frame.f_locals,[400])}
    def start(self):
        self.previous_profile=sys.getprofile();sys.setprofile(self.profile)
        self.thread=threading.Thread(target=self.loop,daemon=True);self.thread.start()
    def loop(self):
        while not self.stop_event.wait(0.5):
            try:self.write()
            except (OSError,RuntimeError,ValueError):pass
    def pause(self,frame,stack=None,index=None,pause_id=None):
        with self.lock:self.paused=frame;self.paused_stack=list(stack or []);self.selected_index=index;self.pause_id=pause_id
        self.write()
    def resume(self):
        with self.lock:self.paused=None;self.paused_stack=[];self.selected_index=None;self.pause_id=None
    def snapshot(self):
        with self.lock:
            frames=[];stack=[];paused=self.paused
            if paused is not None:
                entries=list(enumerate(self.paused_stack))
                if entries:
                    for index,(frame,line) in reversed(entries[-40:]):
                        stack.append({'file':os.path.realpath(frame.f_code.co_filename),'line':line,'function':frame.f_code.co_name,'index':index,'selected':index==self.selected_index})
                    frames.append(paused)
                else:
                    frame=paused
                    while frame is not None and len(stack)<40:
                        filename=os.path.realpath(frame.f_code.co_filename);stack.append({'file':filename,'line':frame.f_lineno,'function':frame.f_code.co_name})
                        if filename in self.tracked:frames.append(frame)
                        frame=frame.f_back
            else:
                for thread_id,frame in sys._current_frames().items():
                    count=0
                    while frame is not None and count<100 and len(frames)<20:
                        if os.path.realpath(frame.f_code.co_filename) in self.tracked:
                            frames.append(frame);stack.append({'file':os.path.realpath(frame.f_code.co_filename),'line':frame.f_lineno,'function':frame.f_code.co_name,'thread':thread_id})
                        frame=frame.f_back;count+=1
            groups=[];budget=[1500]
            for frame in frames[:20]:
                filename=os.path.realpath(frame.f_code.co_filename)
                if filename in self.tracked:self.modules[filename]=frame.f_globals
                if frame.f_code.co_name!='<module>':groups.append({'scope':'locals','name':frame.f_code.co_name,'file':filename,'line':frame.f_lineno,'values':variable_nodes(frame.f_locals,budget)})
            if not groups and self.last_locals:groups.append({'scope':'last locals','name':self.last_locals['function'],**self.last_locals})
            modules=list(self.modules.items())
            if paused is not None:
                selected_file=os.path.realpath(paused.f_code.co_filename);modules=[(selected_file,paused.f_globals)]+[item for item in modules if item[0]!=selected_file]
            for filename,values in modules[:20]:groups.append({'scope':'globals','name':Path(filename).name,'file':filename,'values':variable_nodes(values,budget)})
            app=self.app() if self.app else None
            if app is not None:
                try:values=instance_attributes(app);groups.append({'scope':'self','name':'Application','values':variable_nodes(values,budget)})
                except AttributeError:pass
            self.sequence+=1
            return {'version':1,'sequence':self.sequence,'state':'paused' if paused is not None else 'running','time':time.time(),'groups':groups,'stack':stack,'pause_id':self.pause_id,'selected_index':self.selected_index}
    def write(self,state=None):
        with self.lock:
            data=self.snapshot()
            if state is not None:data['state']=state
            temporary=self.output.with_suffix('.tmp')
            with open(temporary,'w',encoding='utf-8') as stream:
                os.chmod(temporary,0o600);json.dump(data,stream,ensure_ascii=True)
            os.replace(temporary,self.output)
    def close(self):
        self.stop_event.set();sys.setprofile(self.previous_profile)
        self.thread.join(timeout=1)
        with self.lock:self.paused=None;self.paused_stack=[];self.selected_index=None;self.pause_id=None
        try:
            self.write(state='finished')
        except (OSError,RuntimeError,ValueError):pass
