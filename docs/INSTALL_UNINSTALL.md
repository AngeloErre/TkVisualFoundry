# Installation and uninstallation

## TkVisualFoundry IDE — macOS

Extract the download and run **Install_Mac.command**. The IDE lives in `~/Applications/VisualTkStudio`; its launcher is `~/Applications/TkVisualFoundry.app`. The installer now records its owned files and private environment.

To remove it, close the IDE and run **Uninstall_Mac.command**, either from the download or the installation folder. Confirm at the bilingual prompt. The script removes unchanged managed application files, its private owned `.venv` and the unchanged launcher files. Modified files, unknown files/folders, projects, configuration, local history and system Python/Homebrew are preserved. Residual folders with preserved data are expected.

For a preview only, run `Uninstall_Mac.command --dry-run`. Legacy installations without ownership metadata are refused: update once with the new installer before uninstalling. The uninstaller does not recursively remove the whole installation folder.

## TkVisualFoundry IDE — Windows

Install stable **Python 3.15+ with Tkinter**, extract the download and run **Install_Windows.cmd**. By default the launcher selects `py -3.15`; set `VTS_PYTHON` to another compatible executable if needed. The installer creates `%LOCALAPPDATA%/Programs/VisualTkStudio`, a private virtual environment, a Start menu shortcut and a per-user Windows Apps uninstall entry. No administrator installation is required.

Close the IDE, then choose TkVisualFoundry in **Windows Settings → Apps → Installed apps → Uninstall**, or run **Uninstall_Windows.cmd** from the installed folder. The PowerShell uninstaller reads the ownership manifest, asks for confirmation, removes unchanged managed files and its unchanged Start menu shortcut, and removes the matching Apps entry. The private owned environment is sent to the Recycle Bin. Projects, unknown or modified files/folders, configuration, local history and system Python remain. If a locked file prevents removal, close the app and retry; do not manually delete personal project folders.

Install/uninstall commands for both platforms and PowerShell are included together in the source archive. Native Windows installation, shortcuts, registry and Recycle Bin behavior require Windows acceptance testing; they have not been exercised on this macOS session.

## Generated applications

- **macOS**: deployment kits include **Uninstall_Mac.command**. Apps installed with the kit's Install_Mac.command receive an external binary ownership hash. The uninstaller verifies it and moves the recognized app bundle to Trash after confirmation, leaving data outside the app untouched. Apps copied manually from a DMG/ZIP can be moved to Trash in Finder.
- **Windows Setup**: generated Inno Setup projects explicitly enable their native uninstaller. Remove installed applications through Windows Settings → Apps. The IDE's uninstaller never removes separately deployed applications.
- **Portable builds**: an extracted folder is not a registered installation. Remove that folder manually, preserving any data you stored inside it first.

Native installers and graphical removal on both systems still need platform acceptance. Automated checks cover confined ownership plans, preservation of personal/modified files, refusal of links/path escapes or unknown installs, an actual uninstall in temporary fixture directories, and generated shell syntax/Setup flags. No real user installation was removed during validation.

## Rename compatibility

TkVisualFoundry was previously named VisualTk Studio. The private `~/Applications/VisualTkStudio` / `%LOCALAPPDATA%/Programs/VisualTkStudio` directories, settings/cache/history locations, `.vtk.json` format, ownership product ID and Windows uninstall registry key remain stable. These identifiers are intentionally retained to update existing installations without discarding data or environments.

The new Mac launcher is `TkVisualFoundry.app`; the executable inside the script launcher retains its compatibility name. New standalone IDE builds use `TkVisualFoundry.app` and `TkVisualFoundry.dmg`. Windows installs `TkVisualFoundry.lnk` and displays TkVisualFoundry in Settings. Older launchers/shortcuts can coexist after an update and remain usable; the updated manifest retains their original ownership hashes. The uninstaller removes only matching managed files, preserving modified legacy launcher files. Old manifests without the new app/shortcut-name fields are still recognized.
