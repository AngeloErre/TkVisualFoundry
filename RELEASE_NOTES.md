# VisualTk Studio 1.11

Adds project files/folders and the Deploy wizard. Manage files beside the project, edit UTF-8 text, mark resources for inclusion and prepare native build kits for macOS and Windows.

The generated scripts prepare dependencies, build with PyInstaller and create app/DMG or executable folder/ZIP and an optional Inno Setup installer. Build on each target OS; public signing/notarization is separate.

99 tests passed; 11 graphical tests skipped on macOS Python 3.15.2. Tests validate file boundaries, exclusions, resources, exported imports, collision handling and native build command plans. Windows builds, graphical launch and installation on target computers remain pending.

Real native smoke build: macOS Python 3.15.2 / PyInstaller 6.22.3 produced the example .app and ZIP. Resource inclusion and ad hoc codesign verification passed. hdiutil could not create the DMG (device not configured in this session); automatic ZIP fallback succeeded. The built app was not graphically launched.
