#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then
  echo 'Esegui prima Install_Mac.command. Poi avvia questo script dalla cartella ~/Applications/VisualTkStudio.'
  exit 1
fi
.venv/bin/python runtime_requirements.py
# Studio runs user projects using this external interpreter, not its frozen binary.
.venv/bin/python -m PyInstaller --noconfirm --windowed --name VisualTkStudio --add-data "PROJECTS_DEPLOY.md:." --add-data "deploy_build.py:." --add-data "i18n.py:." --add-data "docs:docs" --add-data "README_IT.md:." --add-data "intellisense_worker.py:." --add-data "semantic_engine.py:." --add-data "code_assist.py:." --add-data "components.py:." --add-data "visualtk_runtime.py:." --add-data "database_runtime.py:." --add-data "DATABASE.md:." --add-data "PACCHETTI.md:." --add-data "build_project.py:." --add-data "runtime_requirements.py:." --add-data "README.md:." --add-data "INTELLISENSE.md:." --add-data "ESTENSIONI.md:." --add-data "ESEMPI.md:." --add-data "COMPATIBILITA.md:." --add-data "examples:examples" studio.py
echo 'App standalone creata in dist/VisualTkStudio.app. Configura nelle impostazioni un Python esterno con Tk per eseguire e compilare i progetti.'
hdiutil create -volname VisualTkStudio -srcfolder dist/VisualTkStudio.app -ov -format UDZO VisualTkStudio.dmg
