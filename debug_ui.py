"""Current debug position in the immutable source of the running session."""
from debug_view import DebugOutput
from i18n import tr

class DebugViewMixin:
    def start_debug_view(self,path):
        self.debug_output=DebugOutput(str(path));self.debug_source=path.read_text(encoding='utf-8');self.debug_position=None;self.debug_process=None;self.debug_paused=False
        self.debug_location.set(tr('Debug: in attesa del programma'));self.debug_jump.configure(state='disabled')
    def observe_debug(self,process,text,finished=False):
        if process is not getattr(self,'debug_process',None):return
        if finished:
            self.debug_output=None;self.debug_source=None;self.debug_position=None;self.debug_process=None;self.debug_paused=False
            self.debug_location.set(tr('Debug terminato'));self.debug_jump.configure(state='disabled');self.update_source();return
        parser=getattr(self,'debug_output',None)
        if parser is None:return
        for position in parser.feed(text):
            self.debug_paused=True
            self.debug_position=position
            if position:
                line,context=position
                self.debug_location.set(tr('Debug fermo alla riga {v0}',v0=line)+' · '+context[:100]);self.debug_jump.configure(state='normal')
            else:
                self.debug_location.set(tr('Debug fermo fuori dal sorgente generato'));self.debug_jump.configure(state='disabled')
            self.paint_debug_position()
    def paint_debug_position(self):
        self.generated.tag_remove('debug_current','1.0','end')
        position=getattr(self,'debug_position',None)
        if position and self.generated.get('1.0','end-1c')==getattr(self,'debug_source',None):
            line=position[0];self.generated.tag_add('debug_current',f'{line}.0',f'{line}.end');self.generated.tag_raise('debug_current');self.generated.tag_raise('sel')
    def show_debug_position(self):
        if not getattr(self,'debug_position',None):return
        self.update_source();self.tabs.select(self.generated);line=self.debug_position[0];self.generated.see(f'{line}.0');self.generated.mark_set('insert',f'{line}.0');self.generated.focus_set()
    def debug_resuming(self,text):
        command=text.strip().split(' ',1)[0]
        if command in ('c','cont','continue','n','next','s','step','r','return','until','unt','j','jump','q','quit','exit','restart','run'):
            self.debug_paused=False;self.debug_position=None;self.generated.tag_remove('debug_current','1.0','end');self.debug_jump.configure(state='disabled');self.debug_location.set(tr('Debug: esecuzione in corso'))
