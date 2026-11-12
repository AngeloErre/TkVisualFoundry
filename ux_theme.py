"""IDE styling, independent of the generated application's theme."""
from tkinter import ttk


def apply_theme(root):
    style = ttk.Style(root)
    if 'clam' in style.theme_names():
        style.theme_use('clam')
    root.configure(background='#f4f6fa')
    root.option_add('*Font', ('Helvetica', 12))
    style.configure('.', background='#f4f6fa', foreground='#25324a', font=('Helvetica', 12))
    style.configure('TFrame', background='#f4f6fa')
    style.configure('TLabel', background='#f4f6fa')
    style.configure('Brand.TLabel', font=('Helvetica', 20, 'bold'), foreground='#172744')
    style.configure('Title.TLabel', font=('Helvetica', 12, 'bold'), foreground='#30466a')
    style.configure('Muted.TLabel', foreground='#62718a', font=('Helvetica', 11))
    style.configure('TButton', padding=(10, 7), background='#ffffff', borderwidth=1, relief='flat')
    style.map('TButton', background=[('pressed', '#dce8ff'), ('active', '#e8effc')])
    style.configure('Toolbar.TButton', padding=(10, 8))
    style.configure('Accent.TButton', background='#2563eb', foreground='white', padding=(14, 8))
    style.map('Accent.TButton', background=[('pressed', '#1745b0'), ('active', '#3475f5')], foreground=[('disabled', '#c6d3ed'), ('!disabled', 'white')])
    style.configure('TEntry', fieldbackground='white', padding=6, bordercolor='#d5deeb')
    style.configure('TCombobox', padding=5, fieldbackground='white')
    style.configure('Treeview', background='white', fieldbackground='white', rowheight=28, borderwidth=0)
    style.map('Treeview', background=[('selected', '#dce8ff')], foreground=[('selected', '#174eb6')])
    style.configure('TNotebook', borderwidth=0, tabmargins=(8, 6, 8, 0))
    style.configure('TNotebook.Tab', padding=(18, 10), background='#e8edf5')
    style.map('TNotebook.Tab', background=[('selected', '#ffffff')], foreground=[('selected', '#1d5bcb')])
    style.configure('TPanedwindow', background='#dce3ee')


def style_editor(widget):
    widget.configure(background='#182234', foreground='#dbe6f5', insertbackground='#93b8ff',
                     selectbackground='#334f79', selectforeground='#ffffff',
                     borderwidth=0, highlightthickness=0, padx=14, pady=12,
                     spacing1=2, spacing3=2)
