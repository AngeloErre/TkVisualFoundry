"""Bounded background checks. No package installation or user code execution."""
import json
import ssl
from functools import lru_cache
import subprocess
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor
from packaging.requirements import Requirement
from packaging.version import Version, InvalidVersion
from packaging.specifiers import SpecifierSet, InvalidSpecifier
from packaging.utils import canonicalize_name

@lru_cache(maxsize=1)
def https_context():
    context=ssl.create_default_context()
    # Keep system/custom trust roots and add the maintained Mozilla CA bundle.
    import certifi
    context.load_verify_locations(cafile=certifi.where())
    return context

INVENTORY='''import json, sys, importlib.metadata as m
print(json.dumps({'python':'.'.join(map(str,sys.version_info[:3])), 'packages':{d.metadata['Name']:d.version for d in m.distributions() if d.metadata['Name']}}))'''

def installed(python):
    result=subprocess.run([python,'-c',INVENTORY],capture_output=True,text=True,timeout=20)
    if result.returncode:raise RuntimeError(result.stderr[-1000:])
    return json.loads(result.stdout)

def stable_versions(data,spec,python):
    candidates=[]
    for raw,files in data.get('releases',{}).items():
        try:v=Version(raw)
        except InvalidVersion:continue
        if v.is_prerelease or v.is_devrelease or v not in spec:continue
        for f in files:
            try:compatible=not f.get('requires_python') or Version(python) in SpecifierSet(f['requires_python'])
            except (InvalidVersion,InvalidSpecifier):compatible=False
            if not f.get('yanked',False) and compatible:
                candidates.append(v);break
    return str(max(candidates)) if candidates else None

def package_check(name,version,requirements,python):
    spec=SpecifierSet(','.join(str(r.specifier) for r in requirements))
    row={'name':name,'installed':version,'required':bool(requirements),'latest':None,'status':'missing' if version is None and requirements else 'unknown'}
    try:
        with urllib.request.urlopen('https://pypi.org/pypi/'+name+'/json',timeout=8,context=https_context()) as response:data=json.load(response)
        latest=stable_versions(data,spec,python);row['latest']=latest
        row['status']='missing' if version is None else ('incompatible' if Version(version) not in spec else ('update' if latest and Version(latest)>Version(version) else 'current'))
    except Exception as exc:row['error']=str(exc)[:160]
    return row

def check_link(url):
    for method in ('HEAD','GET'):
        try:
            request=urllib.request.Request(url,method=method,headers={'User-Agent':'TkVisualFoundry/1.30 documentation check'})
            with urllib.request.urlopen(request,timeout=8,context=https_context()) as response:
                return {'url':url,'status':'ok','resolved':response.url}
        except urllib.error.HTTPError as exc:
            if exc.code==405 and method=='HEAD':exc.close();continue
            code=exc.code;exc.close()
            return {'url':url,'status':'broken' if code in (404,410) else 'unverified','detail':str(code)}
        except Exception as exc:return {'url':url,'status':'unverified','detail':str(exc)[:160]}

def audit(python,specs,urls,cancelled=None):
    def stopped():return cancelled is not None and cancelled.is_set()
    if stopped():return {'cancelled':True}
    inventory=installed(python)
    if stopped():return {'cancelled':True}
    packages={canonicalize_name(k):v for k,v in inventory['packages'].items()}
    grouped={}
    for spec in specs:
        req=Requirement(spec)
        if req.marker and not req.marker.evaluate({'python_version':'.'.join(inventory['python'].split('.')[:2]),'python_full_version':inventory['python']}):continue
        grouped.setdefault(canonicalize_name(req.name),[]).append(req)
    # All installed distributions, including optional and transitive libraries, are checked.
    names=sorted(set(packages)|set(grouped))
    with ThreadPoolExecutor(max_workers=6) as pool:
        rows=list(pool.map(lambda name:None if stopped() else package_check(name,packages.get(name),grouped.get(name,[]),inventory['python']),names))
        links=list(pool.map(lambda url:None if stopped() else check_link(url),urls))
    if stopped():return {'cancelled':True}
    try:
        check=subprocess.run([python,'-m','pip','check'],capture_output=True,text=True,timeout=20)
        consistency=(check.stdout+check.stderr).strip()[:8000]
    except Exception as exc:consistency=str(exc)
    return {'python':python,'version':inventory['python'],'packages':rows,'links':links,'specs':specs,'consistency':consistency}
