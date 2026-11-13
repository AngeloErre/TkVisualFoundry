"""Flat project storage with explicit, validated container relationships."""
CONTAINERS={'Frame','Canvas','LabelFrame','TFrame','TLabelframe','Notebook','CTkFrame','CTkScrollableFrame','CTkTabview'}
TABS={'Notebook','CTkTabview'}

def ordered_widgets(form):
    widgets=form['widgets'];by_name={w['name']:w for w in widgets};result=[];visiting=set();done=set()
    def visit(widget):
        name=widget['name']
        if name in visiting:raise ValueError('Container cycle: '+name)
        if name in done:return
        visiting.add(name);parent=widget.get('parent')
        if parent and parent!=form['name']:
            if parent not in by_name:raise ValueError('Unknown parent: '+str(parent))
            container=by_name[parent]
            if container['kind'] not in CONTAINERS:raise ValueError('Parent is not a container: '+parent)
            visit(container)
            page=widget.get('page','')
            if container['kind'] in TABS:
                pages=container.get('props',{}).get('pages',[])
                if page not in pages:raise ValueError('Select a valid container page: '+name)
            elif page:raise ValueError('Only tab containers accept a page.')
        elif widget.get('page'):raise ValueError('A form does not have pages.')
        if widget['kind'] in TABS:
            pages=widget.get('props',{}).get('pages',['Page 1','Page 2'])
            if not isinstance(pages,list) or not pages or not all(isinstance(p,str) and p for p in pages) or len(pages)!=len(set(pages)):raise ValueError('Tab pages must be non-empty unique names.')
        visiting.remove(name);done.add(name);result.append(widget)
    for w in widgets:visit(w)
    return result

def descendants(form,name):
    result=set();changed=True
    while changed:
        changed=False
        for w in form['widgets']:
            if w.get('parent') in result|{name} and w['name'] not in result:result.add(w['name']);changed=True
    return result

def widget_origin(form,widget):
    by_name={w['name']:w for w in form['widgets']};x=widget['x'];y=widget['y'];seen={widget['name']};parent=widget.get('parent')
    while parent in by_name:
        if parent in seen:raise ValueError('Container cycle')
        seen.add(parent);w=by_name[parent];x+=w['x'];y+=w['y']+(28 if w['kind'] in TABS else 0);parent=w.get('parent')
    return x,y

def visible_widgets(form,pages):
    by_name={w['name']:w for w in form['widgets']};visible=[]
    for w in ordered_widgets(form):
        parent=by_name.get(w.get('parent'))
        if parent and parent not in visible:continue
        if parent and parent['kind'] in TABS and w.get('page')!=pages.get(parent['name'],parent['props']['pages'][0]):continue
        visible.append(w)
    return visible
