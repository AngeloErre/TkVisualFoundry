# Project files and deployment

Save each `.vtk.json` project in its own directory. In the Project sidebar, switch between **Forms and components** and **Files and folders**. The latter displays files next to the project, with create/import/rename/trash/refresh actions. Double-click a UTF-8 text file (up to 2 MB) to edit it. Save and close file editors before deploying. Unsaved file edits are checked when switching projects or closing the IDE.

The view is capped at 1500 entries and skips hidden directories, virtual environments, build/dist and symbolic links. Deleted files are moved into `.visualtk-trash` with a timestamp prefix, allowing manual recovery. Undo affects the designer/model; disk operations are not undone. Renames and deletions do not rewrite code references.

A **✓** means the item is included in deployment. New/imported files are included automatically. Use **Include / exclude from deploy** for existing files. Included directories contribute their visible files recursively, excluding technical folders. To exclude individual children, remove the parent directory inclusion and include the desired files individually. `main.py` is reserved for exported application code. Add local Python modules to the project and import them in the project code; declare third-party libraries as PIP requirements.

Paths are relative to the project directory. To relocate projects with files, copy the entire directory and open the copy. Save As to another directory is blocked when included resources would lose their relative base. Absolute external resource paths are not rewritten or copied automatically.

## Deployment kit

Click **Deploy…**, set a technical application name, numeric version and destination. The IDE creates a new `Name-Version` folder without overwriting existing kits. It cannot be inside an included directory. The kit contains `src/main.py`, selected files, designer project, requirements, metadata, instructions and native build scripts.

| Platform | Run source | Build | Install |
|---|---|---|---|
| macOS | Run_Mac.command | Build_Mac.command → .app and .dmg | Install_Mac.command → ~/Applications |
| Windows | Run_Windows.cmd | Build_Windows.cmd → executable folder and portable ZIP; Setup when Inno Setup is installed | Install_Windows.cmd → launch Setup |

This is a source/build kit, not a precompiled application. **Also build on this computer** uses the configured interpreter and sends output to the IDE log. Build scripts create a private `.venv`, install declared packages and PyInstaller. Initial setup needs Internet access. Use stable Python 3.15+ with Tkinter; set `VTS_PYTHON` if automatic interpreter selection needs overriding.

Build on each target OS and compatible architecture. Transfer the kit to Windows for Windows binaries. Install [Inno Setup](https://jrsoftware.org/isinfo.php) to compile the supplied `Installer_Windows.iss`; the driver detects ISCC in PATH or common install directories. Without it, the portable ZIP is still generated. Ship the whole executable directory, not just its exe.

Native builds do not require Python on the user's computer. Native libraries, drivers, VLC and camera permissions remain separate requirements. Artifacts are unsigned for public distribution; macOS uses ad hoc signing after camera metadata changes. Apple/Microsoft signing and notarization require a separate release process.

Use relative resource paths. Store writable databases and persistent data in a user directory, outside the app bundle. Review included files and licenses before shipping. Dynamic imports and unusual integrations may need custom PyInstaller hooks in `deploy_build.py`. Test builds on clean target computers.

If disk image creation is unavailable, the driver preserves the app and creates a macOS ZIP using `ditto`.
