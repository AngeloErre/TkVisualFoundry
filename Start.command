#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
if [ -x "$HOME/Applications/VisualTkStudio/.venv/bin/python" ]; then
  exec "$HOME/Applications/VisualTkStudio/.venv/bin/python" studio.py
elif [ -x .venv/bin/python ]; then
  exec .venv/bin/python studio.py
fi
for candidate in /Library/Frameworks/Python.framework/Versions/3.15/bin/python3 /opt/homebrew/bin/python3.15 /usr/local/bin/python3.15 python3.15 python3; do
  if "$candidate" -c 'import sys; assert sys.version_info[:2] >= (3, 15) and sys.version_info.releaselevel == "final"' >/dev/null 2>&1; then
    exec "$candidate" studio.py
  fi
done
echo 'Occorre Python 3.15 stabile. Esegui Install_Mac.command.'
exit 1
