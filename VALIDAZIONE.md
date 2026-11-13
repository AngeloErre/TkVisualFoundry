# Validation — 1.12

118 tests passed, 11 graphical tests skipped on macOS Python 3.15.2 / Jedi 0.20.0.

New coverage includes nested parent ordering and runtime parent relationships, invalid parents/pages/cycles, page visibility, subtree/form duplication, catalog coverage, adapter generation, context assistance, Jedi inference for Sheet/CustomTkinter, theme requirements/paths/API calls, CustomTkinter constructor geometry, resource copying and PyInstaller collection options.

Actual imports passed: CustomTkinter 6.0.0, ttkbootstrap 1.20.4, ttkthemes 3.3.0, sv-ttk 2.6.1, Pmw 2.1.1, tksheet 7.6.0 and tkintermapview 1.32 in the selected Python environment. Imports do not certify GUI behavior.

A real PyInstaller 6.22.3 build of the nested-libraries example produced a macOS app and ZIP. Library resources for CustomTkinter, tksheet and sv-ttk were found in the archive; codesign --verify --deep --strict passed. hdiutil could not create a disk image in this session (device not configured), and ZIP fallback succeeded.

The built app was not graphically launched. GUI workflows, all widget interactions, external theme rendering, Windows builds/installers and clean-machine installation require manual target validation. Separate-engine frameworks are not implemented and Tix is not supported.
