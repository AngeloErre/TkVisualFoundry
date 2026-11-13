"""Recover usable IDE settings from partial or malformed local configuration."""
import json
from pathlib import Path

FLAGS={'dependency_before_insert':True,'dependency_before_run':True,'pip_auto_install':True,
       'pip_wheels_only':False,'startup_checks':True,'guided_values':True}
COLORS={'background','foreground','surface','accent','editor_bg','editor_fg','canvas'}

def normalized_settings(data,defaults,color_valid=None):
    result=dict(defaults)
    if not isinstance(data,dict):data={}
    for key in ('python','language'):
        value=data.get(key)
        if isinstance(value,str) and value.strip() and (key!='language' or value in ('it','en')):result[key]=value
    for key,low,high in (('grid',1,100),('font_size',8,32)):
        value=data.get(key,result.get(key,10 if key=='grid' else 13))
        try:
            if isinstance(value,bool) or not isinstance(value,(int,str)):raise ValueError()
            value=int(value)
            if not low<=value<=high:raise ValueError()
        except (ValueError,TypeError):value=defaults.get(key,10 if key=='grid' else 13)
        result[key]=value
    for key,default in FLAGS.items():result[key]=data.get(key) if isinstance(data.get(key),bool) else default
    appearance=data.get('appearance',{})
    if isinstance(appearance,dict):
        clean={}
        for key,value in appearance.items():
            if key not in COLORS or not isinstance(value,str) or not value.strip():continue
            try:
                if color_valid:color_valid(value)
                clean[key]=value
            except Exception:
                # Tk raises TclError for unavailable color names.
                continue
        if clean:result['appearance']=clean
    return result

def load_settings(path,defaults,color_valid=None):
    try:data=json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError,ValueError,UnicodeError):data={}
    return normalized_settings(data,defaults,color_valid)
