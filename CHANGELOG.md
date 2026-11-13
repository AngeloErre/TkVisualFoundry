# 1.10.1

- Keep completion suggestions inside the main window, preventing native popup focus changes from interrupting typing on macOS.
- Add panel focus regression coverage and a graphical typing check.

# 1.10

- Italian/English interface with a persistent language selector and restart notice.
- Project-specific language for exported component controls; existing content preserved.
- English README and in-app documentation with a separate Italian guide.

# 1.9 — IntelliSense Python e librerie

Motore semantico Jedi collegato automaticamente al punto, analisi nel Python dei progetti, import/alias/variabili, metodi dei componenti e firme con argomento attivo. Worker persistente con timeout e scarto delle risposte obsolete; documentazione selezionata su richiesta. Fallback stdlib, comando Motore per preparare Jedi e riavvio dell’analisi dopo installazioni PIP.

77 test superati, 11 grafici saltati nel runtime Linux Python 3.12.14 / Jedi 0.20.0. GUI e build macOS da verificare.

# 1.8 — UI compatta e preparazione PIP automatica

- Icone native per la palette, ricerca e inserimento da tastiera.
- Menu a tendina dentro la finestra; comandi File/Modifica/PIP raccolti per funzione.
- Pulsanti di inserimento e applicazione proprietà sopra le aree espandibili.
- Log richiudibile e limitato in altezza; ripristino pannelli.
- Verifica/installazione/prosecuzione automatiche per i componenti con dipendenze.
- Footer PIP riservato con layout a griglia, scheda log e stato breve.
- Preferenza wheel con fallback sorgenti; solo-wheel facoltativo; import nativi isolati per pacchetto.
- Prova PIP reale in ambiente temporaneo offline. 58 test superati, 10 grafici saltati.

# 1.7 — Configurazione, wizard PIP e database

Centro configurazione, dipendenze prima dell’uso, installazioni in background con esito verificato, NumPy esplicito per webcam, DatabaseView SQLite/PostgreSQL/MySQL con griglia e CRUD, guide/esempio database, ispettore scorrevole e toolbar riorganizzata. Installer base con pacchetti opzionali su richiesta.

50 test superati, 8 grafici saltati; database remoto e installazioni live da collaudare.

# 1.6 — Assistente codice

Completamento contestuale per nomi progetto, metodi Tkinter e opzioni configure. Pannello esempi per componente/evento, firme e descrizioni italiane, popup al cursore e inserimento da tastiera. Installer aggiornato.
33 test superati, 6 grafici saltati.

# 1.5

Procedura guidata componenti esterni, accesso da PyPI, gestione form e duplicazione, preferenze colori persistenti con tre preset.
28 test superati; 6 grafici saltati.

# 1.4 — UX

- Tema chiaro coordinato, editor scuri e pulsante Avvia in evidenza.
- Ricerca componenti e miglioramento spaziature, schede e albero progetto.
- Designer con sfondo chiaro e ombra della finestra.
- Installer aggiornato per includere il modulo del tema.
- 26 test superati, 6 grafici saltati; verifica grafica manuale ancora necessaria.

# Cronologia

## v1.3.1

Diagnostica installer: mostra versione completa, motivo di esclusione delle prerelease e problemi Tk separatamente. Link diretto alla release stabile Python 3.15.0.

## v1.3

- Python minimo 3.15 stabile per IDE, avvio progetti e build.
- Rifiuto di alpha/beta/RC, inclusa 3.16 alpha.
- Installer Python 3.15/Tk e backup degli ambienti incompatibili.
- Backend audio pygame-ce>=2.5.8; PyInstaller>=6.22.3.
- Documentazione e messaggi aggiornati. 25 test superati; 6 grafici saltati; collaudo reale su 3.15 ancora da eseguire.

## v1.2

36 controlli e descrittori, Help, HTML/web/video/YouTube, drag & drop, calendari, font e temi.

## v1.1

Componenti esterni, immagini, MP3, webcam, USB/seriale ed esploratore PyPI.

## v1.0

Designer Tkinter, proprietà, editor eventi, generazione Python, avvio/debug e script macOS.
