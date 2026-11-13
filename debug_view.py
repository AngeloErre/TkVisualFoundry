"""Bounded, non-executing observation of the standard pdb text protocol."""
import os
import re

class DebugOutput:
    def __init__(self,path):
        self.path=os.path.normcase(os.path.realpath(path));self.buffer='';self.location=None
    def feed(self,text):
        self.buffer=(self.buffer+text)[-65536:];result=[]
        while '(Pdb) ' in self.buffer:
            segment,self.buffer=self.buffer.split('(Pdb) ',1)
            matches=list(re.finditer(r'^> (.+)\((\d+)\)([^\r\n]*)',segment,re.MULTILINE))
            if matches:
                match=matches[-1];path,line,context=match.groups()
                self.location=(int(line),context.strip()) if os.path.normcase(os.path.realpath(path))==self.path else None
            result.append(self.location)
        return result
