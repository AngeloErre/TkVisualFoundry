"""Persistent static analysis in the configured project interpreter."""
from i18n import tr
import json
import sys
import signal
import tempfile
from semantic_engine import SemanticEngine
PREFIX='VTS_INTELLISENSE '

def main():
    def stop(signum,frame):raise SystemExit(0)
    signal.signal(signal.SIGTERM,stop)
    with tempfile.TemporaryDirectory(prefix='visualtk-jedi-') as cache:
        engine=None;failure=None
        try:engine=SemanticEngine(cache)
        except ImportError as exc:failure=tr('Motore Jedi non disponibile: ')+str(exc)
        for line in sys.stdin:
            request={}
            try:
                request=json.loads(line)
                if failure:result={'error':failure,'missing_jedi':True,'items':[]}
                else:result=engine.analyze(request)
            except Exception as exc:result={'error':type(exc).__name__+': '+str(exc),'items':[]}
            result.update(id=request.get('id'),action=request.get('action','complete'))
            print(PREFIX+json.dumps(result,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
