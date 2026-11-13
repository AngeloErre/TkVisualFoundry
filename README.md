# VisualTk Studio 1.13

A visual Python/Tkinter IDE for macOS, inspired by the Visual Basic 6 workflow. Design multiple forms, edit control properties, write event handlers and run your application from one workspace.

[Guida italiana](README_IT.md) · [Changelog](CHANGELOG.md)

## New in 1.13

Six built-in components: MIDIPlayer, ExcelWorkbook, PDFDocument, PrintDocument, CloudStorage and LLMClient. Optional dependencies follow the selected service. CloudStorage supports Google Drive, S3/MinIO and WebDAV; LLMClient supports official OpenAI, Claude and Gemini APIs. Runtime session credentials or external environment variables keep secrets out of project files. Slow operations complete asynchronously through events.

[Documents, cloud and LLM guide](docs/en/PRODUCTIVITY.md). Examples are in `examples/Productivity/`. MIDI needs a synthesizer output; API/cloud accounts, consent and printer/device setup remain external requirements. The library catalog now has 29 entries.

## New in 1.12

Library/theme manager with 19 catalog entries, isolated import/GUI checks, palette family filtering and expanded ttk/CustomTkinter controls. Adds tksheet, map and selected Pmw adapters, project theme providers and nested frame/tab containers. PySimpleGUI, FreeSimpleGUI and guizero are informational separate-engine entries, not supported project backends; Tix is unavailable in the supported Python runtime.

[Library and container guide](docs/en/LIBRARIES.md). Try `examples/Libraries/NestedLibraries.vtk.json` and `MapExample.vtk.json`. The designer preview remains schematic.

## New in 1.11

Project explorer for folders and files, UTF-8 file editors and explicit resource inclusion. The Deploy wizard exports a Mac/Windows build kit with source launchers, native build scripts, macOS app/DMG creation and optional Windows Inno Setup installer generation. Build on each target OS. [Full guide](docs/en/DEPLOYMENT.md).

## Features

- Multi-form designer with component icons, drag, resize, property editing and undo/redo.
- Event editor with syntax highlighting, Python/Tkinter completion, signatures and contextual examples.
- Jedi analysis in a separate process using the project's selected Python interpreter.
- Automatic PIP dependency setup, package inspection and external component descriptors.
- DatabaseView with SQLite, PostgreSQL and MySQL connections, tables and CRUD operations.
- Optional webcam, image, audio, video, web, USB and serial components.
- Separate execution, logs, debugging and standalone Python export.
- Persistent themes, custom colors and Italian/English interface.

## Install on macOS

1. Download and extract the source archive into a writable folder.
2. Run `Install_Mac.command` (double-click, or `bash Install_Mac.command` in Terminal).
3. The installer requires stable **Python 3.15 or later with Tkinter**, prepares the IDE environment and creates `VisualTk Studio.app` in `~/Applications`.
4. Open the app. Choose the project interpreter in **Project → Configuration**.
5. Add an optional component and follow the automatic PIP wizard, or use the **PIP** menu.

If a compatible interpreter is missing, the installer attempts Homebrew setup when Homebrew is available; otherwise it opens the Python website. Prerelease interpreters are not accepted. Tkinter is not a PIP package. Re-run the new installer to update; projects remain separate `.vtk.json` files.

## Choose your language

Open **Progetto → Configurazione → Aspetto**, select **English**, save and restart the app. In English, this is **Project → Configuration → Appearance**. Italian is the default. The setting is stored locally; `VTS_LANGUAGE=it` or `VTS_LANGUAGE=en` overrides it for a launch.

The language of generated component controls is stored separately in each project. Existing project text, identifiers, event code and data are preserved. Legacy projects default to Italian component labels.

## Code completion

Type `messagebox.` after `from tkinter import messagebox` to see available members. Type `messagebox.showinfo(` for its signature. Imported libraries and aliases are analyzed in the selected project environment. Use the engine setup action if Jedi is missing. Completion depends on available type information and packages; dynamic APIs may provide fewer suggestions. User code is analyzed statically rather than executed for completion.

## Guides

- [Packages and environment](docs/en/PACKAGES.md)
- [IntelliSense](docs/en/INTELLISENSE.md)
- [Database connections and CRUD](docs/en/DATABASE.md)
- [External components](docs/en/EXTENSIONS.md)
- [Examples](docs/en/EXAMPLES.md)
- [Compatibility](docs/en/COMPATIBILITY.md)

## Development

Run `VTS_LANGUAGE=it python3 -m unittest discover -s tests -q` from the repository directory. Graphical tests require a usable Tk display. Launch `python3 studio.py` with a supported Python/Tkinter installation. Use `Build_Mac.command` for macOS packaging.

GUI behavior and the packaged macOS application require local graphical validation. Optional drivers and native libraries must be installed in the environment used to run the application.

Try `examples/ProjectFiles/ProjectFilesDemo.vtk.json` for a local Python module and a resource included in deployment.

Validation: 118 tests passed, 11 graphical tests skipped. A native macOS example app and ZIP were built with PyInstaller 6.22.3; resource inclusion and ad hoc signature verification passed. DMG creation was unavailable in this session, and ZIP fallback succeeded. Graphical launch, Windows builds and installation on clean targets remain pending.

Version 1.12 validation: 118 tests passed, 11 graphical tests skipped. Seven optional libraries imported successfully in the selected Python 3.15.2 environment. A native macOS example build with CustomTkinter, tksheet and sv-ttk produced an app/ZIP with library resources and a valid ad hoc signature. DMG creation unavailable in this session; fallback succeeded. Graphical execution and Windows builds remain pending.

1.13 validation: 141 tests passed; 11 graphical tests skipped. Real temporary Excel/PDF operations and installed SDK imports passed. Print, MIDI and remote API contracts were tested with mocks, without live account access, paid requests or physical printing. A native Mac Office example app/ZIP build and ad hoc signature were verified; graphical launch, Windows and live services remain pending.
