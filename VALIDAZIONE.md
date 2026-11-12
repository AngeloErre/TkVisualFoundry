# Verifica aggiuntiva 1.3.1

32 test: 26 superati e 6 grafici saltati. Verificata sul Mac la presenza di Python 3.15.0rc3 con Tk 9.0. Eseguita solo la sezione di rilevamento dell’installer, senza installare o modificare software: il messaggio identifica correttamente rc3 e la distingue da un interprete mancante. Nessun collaudo GUI su 3.15 final.

# Verifica della versione 1.3 — 12 novembre 2026

## Requisito introdotto

IDE, interprete configurato per avvio/debug/installazione dipendenze e strumenti di build richiedono Python >=3.15 con releaselevel final. Alpha, beta e release candidate sono rifiutate. L'installer seleziona Python 3.15 stabile con Tkinter e conserva in backup eventuali ambienti precedenti incompatibili.

## Risultati effettivi

- 31 test: 25 superati, 6 test grafici saltati.
- Test eseguiti con Python 3.14.8 per validare modello, generazione e policy di versione senza avviare l'IDE. I casi 3.15 final, 3.15 prerelease e 3.16 alpha sono simulati nei test della policy.
- Provato realmente l'avvio con Python 3.14.8 e Python 3.16.0a2 installati nell'ambiente: entrambi sono rifiutati con il messaggio che richiede 3.15 stabile, senza tentare l'apertura di Tk.
- Sintassi di sorgenti Python, esempi generati e quattro script shell: verificata.
- pygame-ce>=2.5.8 sostituisce pygame nei requisiti del componente audio; resta valido import pygame. La disponibilità di un wheel CPython 3.15 macOS universal2 è stata verificata su PyPI.
- PyInstaller minimo aggiornato a 6.22.3.

## Non verificato

Python 3.15 non è installato nell'ambiente di verifica: non è stato eseguito un collaudo reale del programma o delle dipendenze su quell'interprete. Nessuna installazione Python di sistema è stata modificata. Restano da collaudare GUI, completamento, debug interattivo, audio/video, webcam, USB/seriale, browser nativo, collegamenti live e packaging sul Mac di destinazione.

## Procedura sul Mac

Eseguire Install_Mac.command. Se manca Python 3.15 e Homebrew è presente, lo script installa python@3.15 e python-tk@3.15; senza Homebrew apre il sito ufficiale Python. Dopo l'installazione verificare Help → Diagnostica dipendenze, esempi e suite di test con l'interprete 3.15. Impostare nelle preferenze un interprete stabile >=3.15 se era stato memorizzato un percorso precedente. VLC/libVLC richiede installazione separata.
