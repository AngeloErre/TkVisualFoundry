#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
echo 'Componenti legacy: tkVideoPlayer / pytube. Possono non funzionare con Python 3.15.'
echo 'Per video e YouTube sono preferiti VideoPlayer (VLC) e YouTubePlayer (yt-dlp).'
read -r -p 'Installare comunque le dipendenze opzionali? [s/N] ' legacy_answer
if [ "$legacy_answer" != s ] && [ "$legacy_answer" != S ]; then exit 0; fi
.venv/bin/python runtime_requirements.py
.venv/bin/python -m pip install tkVideoPlayer pytube
