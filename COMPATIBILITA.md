# Compatibilità e dipendenze — VisualTk Studio 1.3

Python minimo richiesto: 3.15 stabile, con Tcl/Tk. Il software è destinato principalmente a macOS. I componenti opzionali richiedono collaudo sul sistema effettivo; la presenza nel catalogo non certifica compatibilità di ogni versione di un pacchetto.

| Funzione | Integrazione | Requisiti / limiti |
|---|---|---|
| Widget Tk, Treeview, Notebook, ScrolledText | Palette | Solo libreria standard, con Tcl/Tk installato |
| filedialog, messagebox, simpledialog, colorchooser | Componenti FileBrowserButton e MessageButton; servizi dell'IDE | Mode determina il dialogo; risultato in paths/result |
| tkinter.font | Selettore carattere, peso, corsivo e anteprima | Solo componenti con proprietà font |
| tkinter.dnd | Modulo standard disponibile al codice utente | Designer usa eventi mouse; FileDropZone usa tkinterdnd2 per Finder |
| Galleria / MP3 / webcam / USB / seriale | Componenti della versione 1.1 mantenuti | Pillow, pygame-ce, OpenCV + NumPy, PyUSB + libusb, pySerial |
| Drag & drop Finder | FileDropZone | tkinterdnd2 e binari tkdnd compatibili con Tk/architettura |
| Dialoghi file avanzati | AdvancedFileBrowser | tkfilebrowser; non è una promessa di anteprima di ogni formato |
| HTML semplice | HtmlView | tkhtmlview; non esegue applicazioni web complete |
| HTML/CSS e pagine locali | WebView | tkinterweb; JavaScript disabilitato nel controllo integrato |
| Browser moderno nativo | NativeWebButton | pywebview; apre una finestra in processo separato, non un Frame incorporato |
| Video locale / streaming | VideoPlayer | python-vlc + VLC/libVLC. Su macOS video in finestra separata; su Windows/Linux embedding dove supportato |
| YouTube | YouTubePlayer | yt-dlp + VLC. Stream audio/video combinato; URL soggetti a scadenza e cambiamenti del servizio |
| Backend YouTube alternativi | backend=pytubefix o pytube | pytubefix incluso nelle dipendenze moderne; pytube è opzionale/legacy |
| tkVideoPlayer | LegacyVideoPlayer | Adapter opzionale: PyAV e compatibilità Python da verificare; fuori dall'installazione standard |
| CustomTkinter | CTkButton, CTkEntry, CTkSwitch | customtkinter |
| Temi ttkbootstrap | Menu Librerie → Tema del progetto | Applicati all'app generata; il designer mantiene il suo tema |
| Calendario / campo data | Calendar, DateEntry | tkcalendar |
| CEF/Chromium cefpython3 | Solo voce catalogo con avvertenza | Non integrato nel runtime Python 3.15; supporto pubblicato per Python precedenti |

## Installazione

Install_Mac.command installa gli strumenti dell’IDE in un ambiente isolato. Multimedia e integrazioni si preparano dal wizard Pacchetti PIP; libusb si installa separatamente tramite il gestore di sistema. VLC va installato separatamente da https://www.videolan.org/vlc/ per la stessa architettura di Python. Non viene scaricato silenziosamente da fonti non verificate.

Install_Optional_Legacy.command, dalla cartella installata, prova a installare tkVideoPlayer e pytube solo dopo una scelta esplicita; può fallire con interpreti moderni. Non installa cefpython3.

Help → Diagnostica dipendenze mostra l'interprete usato, i moduli trovati e i backend nativi rilevati. Un modulo trovato non garantisce che tutti i suoi binari funzionino. Usa Librerie → Wizard PIP / dipendenze progetto per installare ciò che serve ai controlli effettivamente usati.

## Esportazione e macOS

Il generatore incorpora il runtime dei componenti nel sorgente esportato e produce requirements-visualtk.txt. Non copia automaticamente foto/audio/video o altri file riferiti da percorso. Il packaging tenta di raccogliere le dipendenze importate, ma i pacchetti con binari o dati nativi possono richiedere hook PyInstaller dedicati: non è garantita una build universale senza ulteriori interventi. La build dell'app usa una firma locale ad hoc e la descrizione della fotocamera; non è una release notarizzata Apple.

La fotocamera richiede il consenso in Privacy e sicurezza. L'accesso USB dipende dai driver, dai permessi e dal protocollo del dispositivo. Il codice utente e i pacchetti installati eseguono codice con i permessi dell'utente.

## DatabaseView 1.7
SQLite usa sqlite3 standard; PostgreSQL richiede SQLAlchemy e psycopg[binary]; MySQL richiede SQLAlchemy e PyMySQL. Requisiti condizionali al backend. Connessioni remote, GUI e packaging devono essere verificati sul sistema di destinazione.
