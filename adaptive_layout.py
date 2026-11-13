"""Opt-in edge anchoring for Tk/ttk coordinates and ordinary frame containers."""
EDGES={'left','top','right','bottom'}
PARENTS={'Frame','LabelFrame','TFrame','TLabelframe','Canvas'}

def validate_layout(form,widget,registry):
    spec=widget.get('layout')
    if spec is None:return
    if not isinstance(spec,dict):raise ValueError('Invalid adaptive layout settings.')
    anchors=spec.get('anchors',['left','top'])
    if not isinstance(anchors,list) or any(not isinstance(edge,str) or edge not in EDGES for edge in anchors) or len(anchors)!=len(set(anchors)):raise ValueError('Use unique left/top/right/bottom anchors.')
    for key in ('min_width','min_height'):
        value=spec.get(key,10)
        if type(value) is not int or not 1<=value<=10000:raise ValueError('Minimum layout dimensions must be integers from 1 to 10000.')
        if value>widget['width' if key=='min_width' else 'height']:raise ValueError('Minimum size cannot exceed the designed control size.')
    if registry.get(widget['kind'],{}).get('module','').startswith('customtkinter'):raise ValueError('Adaptive anchors currently support Tk/ttk geometry; CustomTkinter controls are not supported yet.')
    parent=next((w for w in form['widgets'] if w['name']==widget.get('parent')),None)
    if widget.get('page') or parent and parent['kind'] not in PARENTS:raise ValueError('Adaptive anchors currently require a form or ordinary Tk/ttk frame/canvas parent.')

def anchored_geometry(original,baseline,current,spec):
    result={key:original[key] for key in ('x','y','width','height')};edges=set(spec.get('anchors',['left','top']))
    for axis,size,near,far,delta,minimum in [('x','width','left','right',current[0]-baseline[0],spec.get('min_width',10)),('y','height','top','bottom',current[1]-baseline[1],spec.get('min_height',10))]:
        if near in edges and far in edges:result[size]=max(minimum,original[size]+delta)
        elif far in edges:result[axis]=max(0,original[axis]+delta)
        elif near not in edges:result[axis]=max(0,original[axis]+round(delta/2))
    return result

def _vts_install_anchors(parent,entries,baseline):
    pending=[None];alive=[True]
    def apply():
        pending[0]=None
        if not alive[0] or not parent.winfo_exists():return
        size=(parent.winfo_width(),parent.winfo_height())
        if min(size)<=1:return
        for widget,original,spec in entries:
            if widget.winfo_exists():widget.place_configure(**anchored_geometry(original,baseline,size,spec))
    def schedule(event=None):
        if event is not None and event.widget is not parent:return
        if alive[0] and pending[0] is None:pending[0]=parent.after_idle(apply)
    def destroy(event):
        if event.widget is parent:
            alive[0]=False
            if pending[0] is not None:
                try:parent.after_cancel(pending[0])
                except Exception:pass
    parent.bind('<Configure>',schedule,add='+');parent.bind('<Map>',schedule,add='+');parent.bind('<Destroy>',destroy,add='+');schedule()
