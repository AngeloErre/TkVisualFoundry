"""Compact VB6-inspired chrome, independent of generated application themes."""
from tkinter import ttk


def editor_palette(background,rgb=None):
    rgb=[v/257 for v in rgb] if rgb is not None else [int(background[i:i+2],16) for i in (1,3,5)]
    light=sum(v*w for v,w in zip(rgb,(.2126,.7152,.0722)))>145
    return ({'kw':'#0000a0','str':'#8a2020','comment':'#187034','num':'#804000'} if light else
            {'kw':'#c792ea','str':'#c3e88d','comment':'#a2b4c5','num':'#f78c6c'})


def apply_theme(root):
    style=ttk.Style(root)
    if 'clam' in style.theme_names():style.theme_use('clam')
    root.configure(background='#d4d0c8');root.option_add('*Font',('Helvetica',11))
    style.configure('.',background='#d4d0c8',foreground='#202020',font=('Helvetica',11))
    style.configure('TFrame',background='#d4d0c8');style.configure('TLabel',background='#d4d0c8')
    style.configure('Brand.TLabel',font=('Helvetica',17,'bold'))
    style.configure('Title.TLabel',font=('Helvetica',11,'bold'))
    style.configure('Muted.TLabel',foreground='#505050',font=('Helvetica',10))
    style.configure('TButton',padding=(6,3),background='#d4d0c8',borderwidth=1,relief='raised')
    style.map('TButton',background=[('pressed','#b8bec8'),('active','#e5e5e5')])
    style.configure('Toolbar.TButton',padding=(6,3),relief='flat')
    style.configure('Accent.TButton',background='#153d73',foreground='white',padding=(7,4))
    style.map('Accent.TButton',background=[('pressed','#09244c'),('active','#254f86')],foreground=[('disabled','#aeb9c8'),('!disabled','white')])
    style.configure('TEntry',fieldbackground='white',padding=3,bordercolor='#808080')
    style.configure('TCombobox',padding=3,fieldbackground='white')
    style.configure('Treeview',background='white',fieldbackground='white',rowheight=23,borderwidth=1)
    style.map('Treeview',background=[('selected','#153d73')],foreground=[('selected','white')])
    style.configure('TNotebook',borderwidth=1,tabmargins=(2,2,2,0))
    style.configure('TNotebook.Tab',padding=(7,4),background='#d4d0c8')
    style.map('TNotebook.Tab',background=[('selected','#eeeeee')],foreground=[('selected','#202020')])
    style.configure('TPanedwindow',background='#a6a6a6');style.configure('Sash',sashthickness=5)
    style.configure('Caption.TFrame',background='#153d73')
    style.configure('Caption.TLabel',background='#153d73',foreground='white',font=('Helvetica',11,'bold'))
    style.configure('PropertyGroup.TLabel',background='#b8bec8',foreground='#202020',font=('Helvetica',10,'bold'))
    style.configure('PropertyName.TLabel',background='#e8e6e0',foreground='#202020',borderwidth=1,relief='groove')
    style.configure('PropertyHelp.TLabel',background='#ffffdf',foreground='#303030',font=('Helvetica',10))


def style_editor(widget):
    widget.configure(background='#ffffff',foreground='#202020',insertbackground='#202020',
                     selectbackground='#153d73',selectforeground='#ffffff',
                     borderwidth=0,highlightthickness=0,padx=8,pady=6,spacing1=1,spacing3=1)
