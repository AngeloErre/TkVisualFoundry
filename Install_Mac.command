#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
INSTALL_LANGUAGE="${VTS_LANGUAGE:-it}"
if [ -t 0 ] && [ -z "${VTS_LANGUAGE:-}" ]; then
  read -r -p 'Lingua / Language [it/en, default it]: ' INSTALL_LANGUAGE
fi
say() { if [ "$INSTALL_LANGUAGE" = en ]; then echo "$2"; else echo "$1"; fi; }
say 'VisualTk Studio — installazione per macOS' 'VisualTk Studio — macOS installation' 
# Prefer a modern Python with working Tk. No administrator privileges required.
PYTHON_BIN=''
for candidate in /Library/Frameworks/Python.framework/Versions/3.15/bin/python3 /opt/homebrew/bin/python3.15 /usr/local/bin/python3.15 python3.15 python3; do
  if VERSION_INFO=$("$candidate" -c 'import sys; print(sys.version.split()[0]); raise SystemExit(0 if sys.version_info[:2] >= (3, 15) and sys.version_info.releaselevel == "final" else 2)' 2>/dev/null); then
    if TK_INFO=$("$candidate" -c 'import tkinter; assert tkinter.TkVersion >= 8.6; print(tkinter.TkVersion)' 2>&1); then
      say "Python stabile rilevato: $VERSION_INFO — $candidate (Tk $TK_INFO)" "Stable Python found: $VERSION_INFO — $candidate (Tk $TK_INFO)"
      PYTHON_BIN="$candidate"; break
    else
      say "Python $VERSION_INFO trovato in $candidate, ma Tkinter non è utilizzabile: $TK_INFO" "Python $VERSION_INFO found at $candidate, but Tkinter is unavailable: $TK_INFO"
    fi
  elif [ -n "$VERSION_INFO" ]; then
    say "Rilevato $candidate: Python $VERSION_INFO. Non compatibile: occorre almeno 3.15 final; rc/alpha/beta sono escluse." "Found $candidate: Python $VERSION_INFO. Requires 3.15 final or later; prereleases are excluded."
  fi
done
if [ -z "$PYTHON_BIN" ]; then
  BREW_BIN=''
  for candidate in /opt/homebrew/bin/brew /usr/local/bin/brew; do
    if [ -x "$candidate" ]; then BREW_BIN="$candidate"; break; fi
  done
  if [ -z "$BREW_BIN" ]; then
    say 'Python può essere già installato, ma non è stata trovata una versione stabile compatibile con Tkinter.' 'No compatible stable Python with Tkinter was found.'
    say 'Installa Python 3.15.0 stabile (senza rc, alpha o beta) dal pacchetto ufficiale:' 'Install stable Python 3.15.0 or later from the official package:'
    echo 'https://www.python.org/downloads/release/python-3150/'
    open 'https://www.python.org/downloads/release/python-3150/'
    say 'Dopo aver installato Python, riesegui questo installer. Premi Invio per uscire.' 'After installing Python, run this installer again. Press Enter to exit.'
    read -r _answer
    exit 1
  fi
  "$BREW_BIN" install python@3.15 python-tk@3.15
  PYTHON_BIN="$("$BREW_BIN" --prefix python@3.15)/bin/python3.15"
fi
INSTALL_DIR="$HOME/Applications/VisualTkStudio"
mkdir -p "$INSTALL_DIR"
# Copy only distribution files, never a previous environment.
cp deploy_icons.py package_catalog.py settings_store.py vb6_ui.py editor_guidance.py component_docs.py startup_checks.py intelligence_ui.py productivity_ui.py productivity_specs.py productivity_runtime.py service_backends.py hierarchy.py library_catalog.py library_checks.py library_ui.py container_ui.py integration_runtime.py theme_runtime.py project_ui.py project_files.py deployment.py deploy_build.py studio.py i18n.py component_palette.py ux_theme.py workspace_ui.py code_assist.py assist_ui.py semantic_engine.py analysis_client.py intellisense_worker.py dependency_manager.py dependency_ui.py configuration_ui.py database_runtime.py support_ui.py runtime_requirements.py core.py components.py library_explorer.py visualtk_runtime.py build_project.py requirements.txt requirements-multimedia.txt requirements-integrations.txt Build_Mac.command Install_Optional_Legacy.command "$INSTALL_DIR/"
cp -R examples docs "$INSTALL_DIR/"
cp PRODUCTIVITY.md LIBRARIES_THEMES.md PROJECTS_DEPLOY.md README.md README_IT.md ESTENSIONI.md ESEMPI.md COMPATIBILITA.md VALIDAZIONE.md CHANGELOG.md RELEASE.json DATABASE.md PACCHETTI.md INTELLISENSE.md RELEASE_NOTES.md "$INSTALL_DIR/"
if [ -x "$INSTALL_DIR/.venv/bin/python" ]; then
  if ! "$INSTALL_DIR/.venv/bin/python" -c 'import sys,importlib.metadata; assert sys.version_info[:2] >= (3, 15) and sys.version_info.releaselevel == "final"; assert not any(d.metadata.get("Name","").lower()=="pygame" for d in importlib.metadata.distributions())' >/dev/null 2>&1; then
    ENV_BACKUP="$INSTALL_DIR/.venv.backup-$(date +%Y%m%d-%H%M%S)-$$"
    mv "$INSTALL_DIR/.venv" "$ENV_BACKUP"
    say "Ambiente precedente conservato in $ENV_BACKUP" "Previous environment preserved at $ENV_BACKUP"
  fi
fi
"$PYTHON_BIN" -m venv "$INSTALL_DIR/.venv"
"$INSTALL_DIR/.venv/bin/python" -m pip install --upgrade pip
"$INSTALL_DIR/.venv/bin/python" -m pip install -r "$INSTALL_DIR/requirements.txt"
say 'I componenti esterni si preparano dall’app: Pacchetti PIP → scegli componente → Installa.' 'Prepare external components in the app: PIP → select component → Install.'
say 'Webcam: il wizard installerà OpenCV, NumPy e Pillow. SQLite non richiede pacchetti.' 'Webcam: the wizard installs OpenCV, NumPy and Pillow. SQLite needs no packages.'
"$INSTALL_DIR/.venv/bin/python" -c 'import tkinter, jedi, PyInstaller; r=tkinter.Tk(); r.withdraw(); r.update(); r.destroy()'
APP_DIR="$HOME/Applications/VisualTk Studio.app"
mkdir -p "$APP_DIR/Contents/MacOS"
cat > "$APP_DIR/Contents/MacOS/VisualTkStudio" <<'LAUNCH'
#!/bin/bash
cd "$HOME/Applications/VisualTkStudio" || exit 1
exec .venv/bin/python studio.py
LAUNCH
chmod +x "$APP_DIR/Contents/MacOS/VisualTkStudio"
cat > "$APP_DIR/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleName</key><string>VisualTk Studio</string>
<key>CFBundleDisplayName</key><string>VisualTk Studio</string>
<key>CFBundleExecutable</key><string>VisualTkStudio</string>
<key>CFBundleIdentifier</key><string>it.visualtk.studio</string>
<key>CFBundleVersion</key><string>1.18</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>NSHighResolutionCapable</key><true/>
</dict></plist>
PLIST
say "Installato: $APP_DIR" "Installed: $APP_DIR"
open "$APP_DIR"
