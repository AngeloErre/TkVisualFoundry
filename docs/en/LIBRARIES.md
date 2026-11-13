# Libraries, themes and nested containers

Open **Components → Libraries and themes…**. The catalog lists 19 library families, integration type, requirements and the last check for the selected interpreter. The palette now offers a family filter.

Installation checks validate versions/imports in an external process. An isolated GUI test creates a representative widget, runs a short event loop and destroys it. It requires a usable graphical session and does not certify every widget or interaction. Results record the interpreter, date and theme configuration. They are historical checks; changes to the environment can make them stale. Library deployment is not automatically marked as validated.

## Supported integrations

- Expanded standard ttk palette, including buttons, labels, entries, check/radio, scale/spinbox, frames, separators, scrollbar, menubutton, sizegrip and panedwindow, alongside existing Combobox, Progressbar, Treeview and Notebook.
- CustomTkinter buttons, labels, entries, checkbox/radio/switch, slider/progressbar, option menu/combo, segmented buttons, textbox, frames, scrollable frames and tabs. Geometry is passed to constructors rather than place().
- ttkbootstrap 1.x themes (>=1.10,<2), ttkthemes and sv-ttk theme providers.
- Local Azure/Forest Tcl theme folder import.
- Pmw ComboBox, EntryField, Counter and ScrolledText with automatic initialization.
- Existing tkcalendar, tkinterweb, tkVideoPlayer and TkinterDnD2 adapters.
- Sheet (tksheet): get_data/set_data/get_cell/set_cell, SheetChanged/SheetSelected events.
- MapView (tkintermapview): position, zoom, address lookup, markers, MapClicked/MarkerSelected events. Tile/geocoding services may require network access.

Tix is unavailable because tkinter.tix was removed in Python 3.13; the IDE requires stable Python 3.15+. PySimpleGUI, FreeSimpleGUI and guizero are cataloged as separate application engines. They are not palette widgets and this release does not generate their project types.

Jedi analyzes installed library sources in the project interpreter. Contextual examples cover advanced adapters and common modern controls. Full wrapped APIs remain accessible through .sheet, .map and .view.

## Nested containers

Select a container before inserting a new control, or set the **parent** and **page** fields in its inspector. Coordinates are relative to the parent; review them when reparenting. Supported containers: Frame, LabelFrame, Canvas, TFrame, TLabelframe, CTkFrame, CTkScrollableFrame, Notebook and CTkTabview.

Use the container's **Visible page** selector for tabs. Selecting a child in the project tree reveals its page. The generator orders parents before children and rejects cycles, missing/invalid parents and invalid pages. Duplicating a container copies its subtree; deleting it removes descendants. Form duplication remaps parent names. Event code remains verbatim and may still refer to original control names. A page containing children cannot be removed/renamed until those children are reassigned.

The canvas preview is schematic. It does not instantiate external components, load network content, or faithfully reproduce styles, clipping, borders and scrolling. TPanedwindow sections are currently managed through code, not the visual nesting editor.

## Project themes

Use **View → Application theme…** or the library manager. Choose one ttk provider: none, ttkbootstrap, ttkthemes, sv-ttk, azure or forest. Theme choices follow the provider. CustomTkinter has a separate System/Light/Dark setting. Project themes do not change IDE appearance settings. ttk themes do not restyle classic Tk or CustomTkinter controls.

For Azure/Forest, download and extract the official theme, then **Import theme folder…**. Include azure.tcl or forest-light.tcl/forest-dark.tcl and their image directories. A new project themes/ folder is created and marked for deployment; existing folders are preserved. The import limit is 2000 files / 50 MB. Hidden files and symbolic links are skipped. Keep licenses with distributed resources.

Sources: [Azure](https://github.com/rdbende/Azure-ttk-theme), [Forest](https://github.com/rdbende/Forest-ttk-theme), [Sun Valley](https://github.com/rdbende/Sun-Valley-ttk-theme), [ttkthemes](https://ttkthemes.readthedocs.io/).

## Deployment

Generated code embeds the adapters/theme initializer. The build kit supplies PyInstaller collection options for active packages, including themes, fonts, Tcl and native assets. Azure/Forest require the whole theme folder in project files. External drivers, codecs, permissions and services remain separate requirements. Native builds must be tested on each target OS.

Examples: examples/Libraries/NestedLibraries.vtk.json and MapExample.vtk.json. The former combines tabs, nested frames, Sheet and Sun Valley; the latter demonstrates a map click event.
