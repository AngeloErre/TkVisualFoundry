# Validation — 1.11

99 tests passed; 11 graphical tests skipped. macOS Python 3.15.2, Jedi 0.20.0.

New coverage: confined paths and symlinks, file inclusion/rename/recoverable trash, exclusions, no overwrites, deployment resources and scripts, exported local imports, reserved names, output recursion prevention, failed-export cleanup, macOS and Windows native build command plans. Build-plan tests mock external tools; they do not compile native artifacts.

Existing semantic completion, locale, database and designer-model checks also pass. GUI, macOS app execution, Windows builds/installers and clean-machine installation require manual target validation.

Real native smoke build: macOS Python 3.15.2 / PyInstaller 6.22.3 produced the example .app and ZIP. Resource inclusion and ad hoc codesign verification passed. hdiutil could not create the DMG (device not configured in this session); automatic ZIP fallback succeeded. The built app was not graphically launched.
