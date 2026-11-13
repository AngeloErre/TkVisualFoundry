"""Standalone project theme initialization; no third-party imports until used."""
from pathlib import Path

def apply_project_theme(root,config):
    provider=config.get('provider','none');name=config.get('name','');mode=config.get('mode','light')
    if provider=='ttkbootstrap':
        import ttkbootstrap
        return ttkbootstrap.Style(theme=name or 'litera')
    if provider=='ttkthemes':
        from ttkthemes import ThemedStyle
        style=ThemedStyle(root);style.set_theme(name or 'arc');return style
    if provider=='sv-ttk':
        import sv_ttk
        sv_ttk.set_theme(mode);return None
    if provider in ('azure','forest'):
        path=Path(config['file']).resolve();root.tk.call('source',str(path))
        if provider=='azure':root.tk.call('set_theme',mode)
        else:
            from tkinter import ttk
            ttk.Style(root).theme_use('forest-'+mode)
    if provider not in ('none','ttkbootstrap','ttkthemes','sv-ttk','azure','forest'):raise ValueError('Unsupported theme provider')
    return None
