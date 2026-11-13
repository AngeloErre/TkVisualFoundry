"""Interpreter-scoped checks. A successful import is not a GUI/deploy certification."""
import json
from pathlib import Path
import subprocess
import time
from library_catalog import LIBRARIES
from dependency_manager import probe_interpreter

SAMPLES={'tkinter':'import tkinter as tk\nw = tk.Button(root,text="Test")','tkinter.ttk':'from tkinter import ttk\nw = ttk.Button(root,text="Test")','CustomTkinter':'import customtkinter as ctk\nw = ctk.CTkButton(root,text="Test")','Pmw':'import Pmw\nPmw.initialise(root)\nw = Pmw.EntryField(root)','tkcalendar':'from tkcalendar import DateEntry\nw = DateEntry(root)','tksheet':'from integration_runtime import SheetView\nw = SheetView(root,data=[["Test",1]],headers=["Name","Value"])','tkintermapview':'from integration_runtime import MapView\nw = MapView(root)','tkinterweb':'from visualtk_runtime import WebView\nw = WebView(root)','tkVideoPlayer':'from visualtk_runtime import LegacyVideoPlayer\nw = LegacyVideoPlayer(root)','TkinterDnD2':'from tkinterdnd2 import TkinterDnD\nTkinterDnD._require(root)\nw = tk.Label(root,text="tkDnD loaded")'}

def check_library(python,name,runtime=False,config=None,cwd=None):
    row=next(item for item in LIBRARIES if item[0]==name)
    if row[4] in ('unsupported','separate'):return {'state':row[4],'detail':row[5]}
    if row[2]:
        checks=probe_interpreter(python,row[2])
        if any(item['state']!='ready' for item in checks):return {'state':'missing','detail':json.dumps(checks,ensure_ascii=False)}
    if not runtime:
        if row[4]=='assets':return {'state':'assets','detail':'Configure and import the theme folder, then run its isolated test.'}
        result=subprocess.run([python,'-c','import importlib; importlib.import_module('+repr(row[3])+')'],capture_output=True,text=True,timeout=20)
        return {'state':'installed' if result.returncode==0 else 'error','detail':(result.stderr or 'Import OK')[-4000:],'checked_at':time.time(),'python':python,'theme':config if row[1]=='theme' else None}
    setup=SAMPLES.get(name)
    if row[1]=='theme':
        if not config or config.get('provider')!=({'Azure':'azure','Forest':'forest'}.get(name,name)):return {'state':'error','detail':'Select this theme in project theme settings first.'}
        setup='from theme_runtime import apply_project_theme\napply_project_theme(root,'+repr(config)+')\nw = tk.ttk.Button(root,text="Theme test")'
    if not setup:return {'state':'error','detail':'No runtime test configured'}
    script='import sys,json,tkinter as tk\nfrom tkinter import ttk\nsys.path.insert(0,'+repr(str(Path(__file__).resolve().parent))+')\nroot=tk.Tk(); root.withdraw()\nerrors=[]\nroot.report_callback_exception=lambda *args:errors.append(str(args[1]))\ntry:\n'+'\n'.join('    '+line for line in setup.splitlines())+'\n    w.pack()\n    root.after(400,root.quit)\n    root.mainloop()\nfinally:\n    root.destroy()\nif errors:raise RuntimeError("; ".join(errors))\nprint("VISUALTK_RUNTIME_OK")\n'
    result=subprocess.run([python,'-c',script],cwd=cwd,capture_output=True,text=True,timeout=25)
    return {'state':'runtime_ok' if result.returncode==0 and 'VISUALTK_RUNTIME_OK' in result.stdout else 'error','detail':(result.stdout+'\n'+result.stderr)[-5000:],'checked_at':time.time(),'python':python,'theme':config if row[1]=='theme' else None}
