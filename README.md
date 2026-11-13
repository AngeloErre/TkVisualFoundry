# VisualTk Studio 1.10

A visual Python/Tkinter IDE for macOS, inspired by the Visual Basic 6 workflow. Design multiple forms, edit control properties, write event handlers and run your application from one workspace.

[Guida italiana](README_IT.md) · [Changelog](CHANGELOG.md)

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
