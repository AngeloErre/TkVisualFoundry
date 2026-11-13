"""Editor-local breakpoint controls, kept separate from active session locations."""
from tkinter import messagebox
from event_breakpoints import remap_lines,resolve_breakpoints
from i18n import tr

class BreakpointMixin:
    def toggle_event_breakpoint(self,event=None):
        if getattr(self,'debug_source',None):
            self.write_log(tr('Arresta il debug prima di cambiare i breakpoint.')+'\n');return 'break'
        if not self.code_target:return 'break'
        line=int(self.code.index('insert').split('.')[0]);text=self.code.get(f'{line}.0',f'{line}.end').strip()
        self.commit_code();obj,key,global_=self.code_target;field='code_breakpoints' if global_ else 'breakpoints'
        existing=obj.get(field,{}).get(key,[])
        if line not in existing and (not text or text.startswith('#')):
            messagebox.showinfo(tr('Breakpoint'),tr('Scegli una riga di codice, non vuota o di solo commento.'),parent=self);return 'break'
        self.checkpoint();points=obj.setdefault(field,{});lines=points.setdefault(key,[])
        if line in lines:lines.remove(line)
        else:lines.append(line);lines.sort()
        if not lines:points.pop(key,None)
        if not points:obj.pop(field,None)
        self.paint_event_breakpoints();self.update_source();return 'break'
    def clear_event_breakpoints(self):
        if getattr(self,'debug_source',None):
            self.write_log(tr('Arresta il debug prima di cambiare i breakpoint.')+'\n');return
        if not self.code_target:return
        self.commit_code();obj,key,global_=self.code_target;field='code_breakpoints' if global_ else 'breakpoints'
        if key not in obj.get(field,{}):return
        self.checkpoint();obj[field].pop(key)
        if not obj[field]:obj.pop(field)
        self.paint_event_breakpoints();self.update_source()
    def remap_event_breakpoints(self,obj,key,global_,old,new):
        field='code_breakpoints' if global_ else 'breakpoints';data=obj.get(field,{})
        if key in data:
            previous=data[key];points=remap_lines(old,new,previous)
            if len(points)<len(previous):self.write_log(tr('Breakpoint rimossi da righe eliminate: ')+str(len(previous)-len(points))+'\n')
            if points:data[key]=points
            else:data.pop(key)
            if not data:obj.pop(field,None)
    def paint_event_breakpoints(self):
        self.code.tag_remove('event_break','1.0','end')
        if not self.code_target:return
        obj,key,global_=self.code_target;field='code_breakpoints' if global_ else 'breakpoints';old=(obj if global_ else obj.get('events',{})).get(key,'')
        lines=remap_lines(old,self.code.get('1.0','end-1c'),obj.get(field,{}).get(key,[]))
        for line in lines:self.code.tag_add('event_break',f'{line}.0',f'{line}.end')
        self.code.tag_raise('event_break')
    def prepare_session_breakpoints(self,source):
        resolved,unresolved=resolve_breakpoints(self.project,source);self.session_breaks=set(self.breaks)|resolved
        for obj,event,line in unresolved:self.write_log(tr('Breakpoint non eseguibile: ')+obj+' → '+event+':'+str(line)+'\n')
