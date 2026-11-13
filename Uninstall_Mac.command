#!/bin/bash
set -euo pipefail
root="$HOME/Applications/VisualTkStudio"
if [ ! -f "$root/.visualtk-install.json" ]; then
  echo 'Installazione non riconosciuta. Aggiorna prima con Install_Mac.command. / Unrecognized installation: update with Install_Mac.command first.'
  exit 1
fi
candidate="$root/.venv/bin/python"
if [ ! -x "$candidate" ]; then candidate=python3; fi
"$candidate" "$root/installation.py" uninstall-mac "$@"
echo 'Premi Invio per chiudere / Press Enter to close'
read -r _answer
