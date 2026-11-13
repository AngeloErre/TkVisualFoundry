"""Separate-process F5/F9 launcher; never included in exported applications."""
import argparse
import json
from pathlib import Path
import pdb
import sys
import uuid
from inspector_runtime import Inspector

class InspectorPdb(pdb.Pdb):
    def __init__(self,inspector):
        super().__init__(readrc=False);self.inspector=inspector
    def preloop(self):
        super().preloop();self.inspector.pause(self.curframe,self.stack,self.curindex,self.pause_token)
    def postcmd(self,stop,line):
        result=super().postcmd(stop,line)
        if stop:self.inspector.resume()
        else:self.inspector.pause(self.curframe,self.stack,self.curindex,self.pause_token)
        return result
    def do_vtsframe(self,arg):
        try:
            token,index=arg.split();index=int(index)
        except (ValueError,TypeError):return self.error('Invalid frame request')
        if token!=self.pause_token or not 0<=index<len(self.stack):return self.error('Stale or invalid frame request')
        if index<self.curindex:self.do_up(str(self.curindex-index))
        elif index>self.curindex:self.do_down(str(index-self.curindex))
    def interaction(self,frame,tb_or_exc):
        self.pause_token=uuid.uuid4().hex
        try:return super().interaction(frame,tb_or_exc)
        finally:self.inspector.resume()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--config',required=True);parser.add_argument('--debug',action='store_true');parser.add_argument('--break',dest='breaks',type=int,action='append',default=[]);parser.add_argument('target');args=parser.parse_args()
    target=Path(args.target).resolve();config=json.loads(Path(args.config).read_text(encoding='utf-8'));inspector=Inspector(str(target),config['output'],config.get('tracked',[]))
    sys.argv=[str(target)];sys.path.insert(0,str(target.parent));namespace={'__name__':'__main__','__file__':str(target),'__package__':None,'__builtins__':__builtins__}
    code=compile(target.read_text(encoding='utf-8'),str(target),'exec');inspector.modules[str(target)]=namespace;inspector.start()
    try:
        if args.debug:
            debugger=InspectorPdb(inspector)
            for line in args.breaks:debugger.set_break(str(target),line)
            debugger.run(code,namespace,namespace)
        else:exec(code,namespace,namespace)
    finally:inspector.close()

if __name__=='__main__':main()
