"""Designer selection geometry; nested children move only through their selected root."""
from hierarchy import descendants

def selected_roots(form,widgets):
    names={w['name'] for w in widgets}
    return [w for w in widgets if not any(w['name'] in descendants(form,name) for name in names-{w['name']})]

def moved_geometry(widgets,dx,dy):
    if not widgets:return {}
    dx=max(dx,-min(w['x'] for w in widgets));dy=max(dy,-min(w['y'] for w in widgets))
    return {w['name']:{'x':w['x']+dx,'y':w['y']+dy} for w in widgets}

def layout_geometry(form,widgets,primary,operation):
    if len(widgets)<2:raise ValueError('Select at least two controls.')
    parents={(w.get('parent') or form['name'],w.get('page','')) for w in widgets}
    if len(parents)!=1:raise ValueError('Layout operations require controls in the same container and page.')
    result={w['name']:{} for w in widgets}
    if operation in ('width','height'):
        for w in widgets:result[w['name']][operation]=primary[operation]
    elif operation in ('left','top','right','bottom'):
        axis='x' if operation in ('left','right') else 'y';size='width' if axis=='x' else 'height'
        for w in widgets:
            value=primary[axis]+(primary[size]-w[size] if operation in ('right','bottom') else 0)
            if value<0:raise ValueError('Alignment would place controls outside their container.')
            result[w['name']][axis]=value
    elif operation in ('horizontal','vertical'):
        axis='x' if operation=='horizontal' else 'y';size='width' if axis=='x' else 'height';ordered=sorted(widgets,key=lambda w:w[axis])
        start=ordered[0][axis];end=ordered[-1][axis]+ordered[-1][size]
        gap=(end-start-sum(w[size] for w in ordered))/(len(ordered)-1)
        if gap<0:raise ValueError('Not enough space to distribute controls without overlap.')
        for w in ordered:result[w['name']][axis]=round(start);start+=w[size]+gap
    else:raise ValueError('Unknown layout operation.')
    return result
