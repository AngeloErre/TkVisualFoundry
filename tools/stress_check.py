"""Deterministic offline stress checks; temporary fixtures only. No GUI acceptance claim."""
import sys,json,tempfile,time,random,subprocess,sqlite3,concurrent.futures,threading,hashlib,io,tokenize,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from core import new_project,generate,validate,KINDS
from project_files import atomic_write_text
from inspector_runtime import value_node
from data_reader import preview
from data_viewer_ui import stop_reader


def main():
    report={};rng=random.Random(133)
    start=time.perf_counter()
    for trial in range(300):
     p=new_project();p['forms'][0]['events']={'Load':'pass'}
     for f in range(rng.randrange(1,5)):
      if f:p['forms'].append(dict(name=f'Form{f+1}',title='Form '+str(f),width=640,height=440,bg='#ffffff',widgets=[],events={}))
      form=p['forms'][f]
      for w in range(rng.randrange(1,31)):
       name=f'Control{trial}_{f}_{w}';kind=rng.choice(KINDS)
       form['widgets'].append(dict(name=name,kind=kind,x=rng.randrange(-20,1000),y=rng.randrange(-20,1000),width=rng.randrange(1,300),height=rng.randrange(1,200),props={},events={'Click':'value = "caffè 😀"\nprint(value)'}))
     a=generate(p);b=generate(copy.deepcopy(p));assert a==b;compile(a,'fuzz','exec');list(tokenize.generate_tokens(io.StringIO(a).readline))
    report['random_projects']={'count':300,'checks':'deterministic generation, compile and tokenization','seconds':round(time.perf_counter()-start,3)}
    with tempfile.TemporaryDirectory() as d:
     root=Path(d);p=root/'stress.sqlite';con=sqlite3.connect(p);con.execute('PRAGMA journal_mode=WAL');con.execute('CREATE TABLE data(id INTEGER PRIMARY KEY, value TEXT)');con.executemany('INSERT INTO data VALUES (?,?)',[(i,'row '+str(i)) for i in range(2000)]);con.commit()
     start=time.perf_counter()
     worker=ROOT/'data_reader.py'
     def read(i):
      r=subprocess.run([sys.executable,str(worker)],input=json.dumps({'path':str(p)}),text=True,capture_output=True,timeout=10);assert r.returncode==0,r.stderr;data=json.loads(r.stdout);assert data['ok'],data;assert len(data['data']['rows'])==500;return i
     with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
      pending=[pool.submit(read,i) for i in range(60)]
      for i in range(100):con.execute('UPDATE data SET value=? WHERE id=?',('updated '+str(i),i));con.commit()
      assert len([f.result() for f in pending])==60
     report['concurrent_readers']={'reads':60,'max_workers':4,'writer_commits':100,'rows_in_database':con.execute('SELECT COUNT(*) FROM data').fetchone()[0],'seconds':round(time.perf_counter()-start,3)};con.close()
     start=time.perf_counter()
     for i in range(100):
      path=root/'project.json';text=json.dumps({'iteration':i,'unicode':'caffè 😀'});atomic_write_text(path,text);assert path.read_text()==text
     assert not list(root.glob('*.tmp'));report['atomic_writes']={'count':100,'seconds':round(time.perf_counter()-start,3)}
     start=time.perf_counter()
     for i in range(40):
      proc=subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)']);stop_reader(proc);proc.wait(timeout=3)
     report['reader_cancellation']={'count':40,'seconds':round(time.perf_counter()-start,3),'all_reaped':True}
     start=time.perf_counter();cyclic=[];cyclic.append(cyclic)
     for i in range(500):
      node=value_node('stress',{'cycle':cyclic,'huge':list(range(10000))});assert len(json.dumps(node))<25000
     report['inspector_snapshots']={'count':500,'seconds':round(time.perf_counter()-start,3),'bounded':True}
    # Large source generation/tokenization throughput, without a GUI performance claim.
    report['large_source']=[]
    for count in (100,1000,3000):
     p=new_project();p['forms'][0]['widgets']=[dict(name='Button'+str(i),kind='Button',x=0,y=0,width=80,height=25,props={'text':str(i)},events={'Click':'pass'}) for i in range(count)]
     start=time.perf_counter();source=generate(p);compile(source,'large','exec');tokens=sum(1 for _ in tokenize.generate_tokens(io.StringIO(source).readline))
     report['large_source'].append({'widgets':count,'bytes':len(source.encode()),'tokens':tokens,'seconds':round(time.perf_counter()-start,3)})
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
