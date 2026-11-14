"""Italian/English UI catalog. Python identifiers and project data are never rewritten."""
import json
import os
from pathlib import Path

LANGUAGES = {'it': 'Italiano', 'en': 'English'}

def configured_language(settings_path=None):
    override = os.environ.get('VTS_LANGUAGE')
    if override in LANGUAGES:
        return override
    try:
        data = json.loads(Path(settings_path or Path.home()/'.visualtkstudio.json').read_text(encoding='utf-8'))
        return data.get('language') if data.get('language') in LANGUAGES else 'it'
    except (OSError, ValueError, TypeError, AttributeError):
        return 'it'

_LANGUAGE = configured_language()

def get_language():
    return _LANGUAGE

def set_language(language):
    if language not in LANGUAGES:
        raise ValueError('Unsupported language: '+str(language))
    global _LANGUAGE
    _LANGUAGE = language

def tr(message, *, language=None, context=None, **values):
    locale = language or _LANGUAGE
    if locale not in LANGUAGES:
        raise ValueError('Unsupported language: '+str(locale))
    text = EN_MESSAGES.get(message, message) if locale == 'en' else message
    if locale == 'en' and context == 'cancel' and message == 'Annulla':
        text = 'Cancel'
    return text.format(**values) if values else text

EN_MESSAGES = {
  "Aggiorna": "Refresh",
  "Aggiunge testo.": "Appends text.",
  "Aggiunge un elemento.": "Adds an item.",
  "Aggiunge un nodo.": "Adds a node.",
  "Aggiunge un record alla tabella selezionata (esempio contatti).": "Adds a record to the selected table (contacts example).",
  "Aggiungi alla palette": "Add to palette",
  "Aggiungi componente visuale": "Add visual component",
  "Aggiungi dipendenza al progetto": "Add project dependency",
  "Aggiungi finestra": "Add window",
  "Aggiungi record": "Add record",
  "Aggiunta al progetto: ": "Added to project: ",
  "Albero/tabella ttk; heading, insert e column nel codice Load.": "ttk tree/table; use heading, insert and column in Load code.",
  "Allinea X": "Align X",
  "Allinea Y": "Align Y",
  "Altre opzioni ▾": "More options ▾",
  "Analisi non disponibile o troppo lenta: ": "Analysis unavailable or timed out: ",
  "Analisi semantica: ": "Semantic analysis: ",
  "Annulla": "Undo",
  "Apertura": "Open",
  "Apertura webcam…": "Opening webcam…",
  "Applica": "Apply",
  "Applica codice": "Apply code",
  "Applica proprietà": "Apply properties",
  "Applicazione": "Application",
  "Apre la connessione in background; attendi DatabaseConnected.": "Opens the connection in the background; wait for DatabaseConnected.",
  "Apre una finestra del progetto.": "Shows a project window.",
  "Apri": "Open",
  "Apri YouTube": "Open YouTube",
  "Apri browser nativo": "Open native browser",
  "Apri cartella immagini": "Open image folder",
  "Apri progetto…": "Open project…",
  "Apri video (tkVideoPlayer)": "Open video (tkVideoPlayer)",
  "Apri web nativo": "Open native web window",
  "Apri wizard PIP…": "Open PIP wizard…",
  "Arresta il processo corrente prima di avviarne un altro.": "Stop the current process before starting another one.",
  "Arresta prima il processo corrente.": "Stop the current process first.",
  "Aspetto": "Appearance",
  "Aspetto ambiente di sviluppo": "IDE appearance",
  "Assistente codice • seleziona un componente e apri un evento": "Code assistant • select a component and open an event",
  "Attendi il completamento dell’operazione corrente.": "Wait for the current operation to finish.",
  "Attiva Jedi dal pulsante Motore… per analizzare le librerie esterne. I suggerimenti standard restano disponibili.": "Use Engine… to enable Jedi for external libraries. Standard suggestions remain available.",
  "Attiva i campi da scrivere. NULL è distinto dal testo vuoto. Le chiavi esistenti non si modificano.": "Enable the fields to write. NULL is different from empty text. Existing keys cannot be edited.",
  "Attiva opzione": "Enable option",
  "Audio MP3 — Python 3.15": "MP3 audio — Python 3.15",
  "Avvia l’animazione.": "Starts the animation.",
  "Avvia webcam": "Start webcam",
  "Avvia — F5": "Run — F5",
  "Avvio": "Run",
  "Azioni ▾": "Actions ▾",
  "Backend database non supportato": "Unsupported database backend",
  "Backend non supportato": "Unsupported backend",
  "Backend supportati: sqlite, postgresql, mysql.": "Supported backends: sqlite, postgresql, mysql.",
  "Booleano: usa true, false, 1 o 0.": "Boolean: use true, false, 1 or 0.",
  "Build completata:": "Build completed:",
  "Calcolo numerico": "Numerical computing",
  "Calendario": "Calendar",
  "Calendario con selezione data.": "Calendar with date selection.",
  "Cambia dimensioni.": "Changes the window size.",
  "Cambia il titolo.": "Changes the title.",
  "Campo data con calendario a comparsa.": "Date field with a popup calendar.",
  "Campo testo CustomTkinter.": "CustomTkinter text entry.",
  "Cancella gli elementi.": "Deletes all items.",
  "Cancella il contenuto.": "Clears the content.",
  "Cancella il testo.": "Clears the text.",
  "Carattere e stile": "Font and style",
  "Carattere editor (8–32)": "Editor font size (8–32)",
  "Cartella di destinazione build": "Build output folder",
  "Catalogo consigliato + ricerca per nome esatto su PyPI. La ricerca libera apre PyPI nel browser.": "Recommended catalog and exact-name PyPI lookup. Free-text search opens PyPI in your browser.",
  "Categoria": "Category",
  "Cerca": "Find",
  "Chiaro": "Light",
  "Chiudi": "Close",
  "Chiudi log": "Close log",
  "Chromium legacy — non supportato su Python 3.13": "Legacy Chromium — not supported on Python 3.13",
  "Classe widget": "Widget class",
  "Codice avvio": "Startup code",
  "Codice da correggere: ": "Code needs attention: ",
  "Codice eventi": "Event code",
  "Codice evento": "Event code",
  "Colonne non valide.": "Invalid columns.",
  "Colore accento": "Accent color",
  "Colore sfondo…": "Background color…",
  "Colore testo…": "Text color…",
  "Colori ambiente…": "IDE colors…",
  "Compatibilità": "Compatibility",
  "Componente": "Component",
  "Componente aggiunto": "Component added",
  "Componente aggiunto: ": "Component added: ",
  "Componente del designer…": "Designer component…",
  "Componente del progetto": "Project component",
  "Componente della palette…": "Palette component…",
  "Componente già disponibile nella palette.": "This component is already available in the palette.",
  "Componente legacy: la disponibilità di pacchetti per questo Python va verificata.": "Legacy component: package availability for this Python must be checked.",
  "Componente sconosciuto": "Unknown component",
  "Componenti": "Components",
  "Componenti del progetto…": "Project components…",
  "Componenti visuali": "Visual components",
  "Configura componente database": "Configure database component",
  "Configura componente…": "Configure component…",
  "Configura il tuo ambiente di lavoro": "Configure your workspace",
  "Configura selezionato…": "Configure selected component…",
  "Configurazione database": "Database configuration",
  "Configurazione • TkVisualFoundry": "Settings • TkVisualFoundry",
  "Conflitti di dipendenze dopo l’installazione.\n": "Dependency conflicts after installation.\n",
  "Connessione database": "Database connection",
  "Connessione e tabella dati": "Connection and data table",
  "Connessione remota non riuscita: verifica server, database, credenziali, rete e driver.": "Remote connection failed: check the server, database, credentials, network and driver.",
  "Connesso • scegli una tabella.": "Connected • select a table.",
  "Connetti": "Connect",
  "Connetti e scegli la tabella durante l’esecuzione": "Connect and select a table at runtime",
  "Connetti prima il database.": "Connect to the database first.",
  "Consulta il Manuale": "See the manual",
  "Consultare il progetto": "See the project documentation",
  "Continua": "Continue",
  "Controlli rinominati. Il codice evento è conservato: aggiorna gli eventuali riferimenti ai controlli originali.": "Controls have been renamed. Event code was preserved: update any references to the original controls.",
  "Controllo Tkinter standard.": "Standard Tkinter control.",
  "Corsivo": "Italic",
  "Crea applicazione": "Build application",
  "Crea componente esterno…": "Create external component…",
  "Crea componente visuale da una libreria…": "Create visual component from a library…",
  "Crea la tabella contatti su SQLite dopo la connessione.": "Creates the contacts example table in SQLite after connecting.",
  "Crea tabella esempio": "Create example table",
  "Crea un controllo riutilizzabile da una classe Tkinter.": "Create a reusable control from a Tkinter class.",
  "Da installare: ": "To install: ",
  "Da verificare": "Not checked",
  "Database SQLite/PostgreSQL/MySQL con tabella dati e comandi CRUD. SQLite non richiede PIP.": "SQLite/PostgreSQL/MySQL database with a data grid and CRUD actions. SQLite needs no PIP packages.",
  "Database remoti": "Remote databases",
  "Database vuoto. Puoi creare la tabella esempio.": "Empty database. You can create the example table.",
  "Descrittore componente visuale": "Visual component descriptor",
  "Dettagli": "Details",
  "Dettagli PyPI": "PyPI details",
  "Diagnostica": "Diagnostics",
  "Dialoghi file avanzati": "Advanced file dialogs",
  "Dialoghi info, warning, error, confirm, text, integer, float, color.": "Information, warning, error, confirmation, text, integer, float and color dialogs.",
  "Dialoghi standard: open, multiple, directory, save. advanced=true richiede tkfilebrowser.": "Standard dialogs: open, multiple, directory and save. advanced=true requires tkfilebrowser.",
  "Dialoghi tkfilebrowser, con selezione multipla.": "tkfilebrowser dialogs with multiple selection.",
  "Dimensioni tra 1 e 10000": "Dimensions must be between 1 and 10000",
  "Dipendenza": "Dependency",
  "Dipendenze del progetto": "Project dependencies",
  "Disconnesso • SQLite non richiede PIP. Premi Connetti per iniziare.": "Disconnected • SQLite needs no PIP packages. Click Connect to start.",
  "Disegna testo.": "Draws text.",
  "Disegna un rettangolo.": "Draws a rectangle.",
  "Dizionario della riga selezionata o None.": "Selected row as a dictionary, or None.",
  "Dizionario selezionato o None": "Selected dictionary or None",
  "Documentazione Tkinter": "Tkinter documentation",
  "Documento non disponibile.": "Document unavailable.",
  "Drag & drop Finder": "Finder drag and drop",
  "Drag & drop nativo di file. Evento FilesDropped; proprietà paths.": "Native file drag and drop. FilesDropped event; paths property.",
  "Drag & drop non disponibile: ": "Drag and drop unavailable: ",
  "Duplica": "Duplicate",
  "Duplica componente": "Duplicate component",
  "ERRORE: ": "ERROR: ",
  "Elenco USB, VID/PID e selezione dispositivo. Richiede libusb.": "USB list, VID/PID and device selection. Requires libusb.",
  "Elimina": "Delete",
  "Elimina finestra": "Delete window",
  "Elimina form": "Delete form",
  "Elimina record": "Delete record",
  "Elimina selezionato": "Delete selected",
  "Elimina selezione": "Delete selection",
  "Elimina un record tramite chiave primaria; chiedi conferma all’utente prima di chiamarlo.": "Deletes a record by primary key; ask the user for confirmation before calling it.",
  "Eliminare definitivamente la riga selezionata?\n": "Permanently delete the selected row?\n",
  "Eliminare il form e i suoi controlli? Aggiorna gli eventuali riferimenti nel codice.": "Delete this form and its controls? Update any code references.",
  "Eliminare la finestra e tutti i suoi componenti?": "Delete the window and all of its components?",
  "Entra": "Step into",
  "Esci": "Exit",
  "Escludi sorgenti e usa soltanto wheel (avanzato)": "Exclude source packages and use wheels only (advanced)",
  "Esegue il comando associato a command, se presente; non genera il Click del designer.": "Invokes the assigned command, if any; does not trigger the designer Click event.",
  "Esegui": "Run",
  "Esempi": "Examples",
  "Esplora PyPI…": "Browse PyPI…",
  "Esplora librerie • PyPI": "Library browser • PyPI",
  "Esplora pacchetti online — PyPI": "Browse packages online — PyPI",
  "Esplora progetto": "Project explorer",
  "Esporta Python…": "Export Python…",
  "Esportato: ": "Exported: ",
  "Esportazione": "Export",
  "Estensioni": "Extensions",
  "Estrazione stream in corso…": "Resolving stream…",
  "Evento sconosciuto": "Unknown event",
  "Ferma l’animazione.": "Stops the animation.",
  "Ferma — Shift+F5": "Stop — Shift+F5",
  "File SQLite / database remoto": "SQLite file / remote database",
  "File SQLite / nome database": "SQLite file / database name",
  "File browser avanzato": "Advanced file browser",
  "Filtra catalogo": "Filter catalog",
  "Fine": "Done",
  "Finestra": "Window",
  "Finestra corrente": "Current window",
  "Finestra radice Tk": "Tk root window",
  "Finestra web nativa in processo separato, compatibile con il mainloop Tk.": "Native web window in a separate process, compatible with the Tk main loop.",
  "Form duplicato": "Form duplicated",
  "Form principale": "Main form",
  "Formato progetto non supportato": "Unsupported project format",
  "Galleria": "Gallery",
  "Galleria miniature con selezione e apertura cartella.": "Thumbnail gallery with image selection and folder browsing.",
  "Gestione form": "Form manager",
  "Gestione form…": "Manage forms…",
  "Grafici": "Charts",
  "Grassetto": "Bold",
  "Griglia designer (1–100 px)": "Designer grid (1–100 px)",
  "Griglia o carattere fuori intervallo.": "Grid or font size is out of range.",
  "Guida rapida": "Quick start",
  "Guida rapida — F1": "Quick start — F1",
  "HTML leggero": "Lightweight HTML",
  "HTML/CSS e pagine web/locali con TkinterWeb. Premi Apri per caricare.": "HTML/CSS and web/local pages with TkinterWeb. Click Open to load.",
  "HTML/CSS web": "Web HTML/CSS",
  "Host (remoto)": "Host (remote)",
  "Host remoto": "Remote host",
  "I campi binari vanno gestiti da codice.": "Binary fields must be handled in code.",
  "Il componente selezionato non espone la proprietà font.": "The selected component does not expose a font property.",
  "Il componente è nella palette. Installa le sue dipendenze prima di avviarlo. Il modulo non viene importato durante il design.": "The component is in the palette. Prepare its dependencies before running. Its module is not imported during design.",
  "Il form principale non può essere eliminato.": "The main form cannot be deleted.",
  "Il nome si assegna alla creazione; rinominare richiede aggiornare il codice utente.": "Names are assigned at creation; renaming requires updating user code.",
  "Il pacchetto python-vlc richiede VLC/libVLC della stessa architettura di Python, installato separatamente.": "python-vlc requires a separate VLC/libVLC installation matching your Python architecture.",
  "Immagini / gallerie": "Images / galleries",
  "Import bloccato: tempo massimo superato": "Import timed out",
  "Import e funzioni globali": "Imports and global functions",
  "Import fallito": "Import failed",
  "Import terminato con codice ": "Import exited with code ",
  "Import verificato": "Import verified",
  "Importa descrittore JSON…": "Import JSON descriptor…",
  "Importa descrittore…": "Import descriptor…",
  "Importazione componente": "Component import",
  "Impossibile leggere dalla webcam": "Unable to read from the webcam",
  "Imposta il valore.": "Sets the value.",
  "Impostazioni pacchetti…": "Package settings…",
  "Incompatibile": "Incompatible",
  "Incrementa il valore.": "Increments the value.",
  "Indica un file SQLite o un nome database.": "Enter a SQLite file or database name.",
  "Informazione": "Information",
  "Informazioni": "About",
  "Inserisce testo.": "Inserts text.",
  "Inserisci URL video": "Enter video URL",
  "Inserisci e seleziona DatabaseView dalla palette.": "Insert and select DatabaseView from the palette.",
  "Inserisci esempio": "Insert example",
  "Inserisci il nome esatto del pacchetto PyPI": "Enter the exact PyPI package name",
  "Inserisci selezionato": "Insert selected",
  "Inserisci un URL YouTube valido": "Enter a valid YouTube URL",
  "Inserisci una porta tra 0 e 65535.": "Enter a port between 0 and 65535.",
  "Installa / ripara": "Install / repair",
  "Installa automaticamente i requisiti mancanti": "Automatically install missing requirements",
  "Installa un pacchetto…": "Install a package…",
  "Installa versione selezionata": "Install selected version",
  "Installazione": "Installation",
  "Installazione in corso": "Installation in progress",
  "Installazione interrotta. Ripeti la verifica prima di usare il componente.": "Installation cancelled. Check the requirements again before using the component.",
  "Installazione nel Python indicato. PIP sceglie versioni compatibili e prepara anche le dipendenze indirette.": "Installation targets the selected Python. PIP resolves compatible versions and indirect dependencies.",
  "IntelliSense e completamento": "IntelliSense and completion",
  "Intero progetto": "Entire project",
  "Interprete Python dei progetti": "Project Python interpreter",
  "Interprete cambiato: riapri la preparazione dei pacchetti.": "The interpreter changed: reopen package preparation.",
  "Interprete inesistente.": "Interpreter does not exist.",
  "Interprete non utilizzabile: ": "Interpreter unavailable: ",
  "Interprete: ": "Interpreter: ",
  "Interrompi": "Cancel operation",
  "Interrompi o attendi il wizard PIP prima di chiudere l’IDE.": "Cancel or finish the PIP wizard before closing the IDE.",
  "Interruttore CustomTkinter.": "CustomTkinter switch.",
  "Interruzione richiesta. Attendi il termine prima di chiudere.": "Cancellation requested. Wait for the operation to stop before closing.",
  "Invia": "Send",
  "La classe deve accettare master e supportare place/bind.\nInstallare un pacchetto non genera automaticamente un widget.\nIl codice esterno viene caricato quando avvii il progetto.": "The class must accept master and support place/bind.\nInstalling a package does not automatically create a widget.\nExternal code is loaded when the project runs.",
  "La tabella non ha una chiave primaria: modifica ed eliminazione sono disabilitate.": "The table has no primary key: update and delete are disabled.",
  "Le chiavi primarie non si modificano dall’editor.": "Primary keys cannot be changed in this editor.",
  "Legge gli indici selezionati.": "Reads the selected indices.",
  "Legge i nodi selezionati.": "Reads the selected nodes.",
  "Legge il contenuto.": "Reads the content.",
  "Legge il testo.": "Reads the text.",
  "Legge il valore.": "Reads the value.",
  "Legge la larghezza effettiva in pixel.": "Reads the actual width in pixels.",
  "Legge la selezione.": "Reads the selection.",
  "Legge l’altezza effettiva in pixel.": "Reads the actual height in pixels.",
  "Legge posizione e dimensioni.": "Reads the position and dimensions.",
  "Legge una proprietà.": "Reads a property.",
  "Leggi dati caricati": "Read loaded data",
  "Leggi riga selezionata": "Read selected row",
  "Lista dei record caricati": "List of loaded records",
  "Locale": "Local",
  "Locali": "Locals",
  "Log installazione": "Installation log",
  "L’esempio è disponibile solo con SQLite.": "The example is available for SQLite only.",
  "L’interprete non ha restituito una verifica leggibile.": "The interpreter did not return a readable check result.",
  "L’operazione continuerà in background. Chiudere la finestra?": "The operation will continue in the background. Close the window?",
  "Mancante": "Missing",
  "Manuale": "Manual",
  "Messaggio": "Message",
  "Messaggio informativo": "Information message",
  "Metadati ricevuti da pypi.org. Nessun pacchetto eseguito.": "Metadata received from pypi.org. No package code was executed.",
  "Modifica": "Edit",
  "Modifica le proprietà del componente.": "Changes the component properties.",
  "Modifica proprietà della finestra.": "Changes window properties.",
  "Modifica record": "Edit record",
  "Modifica selezionato": "Edit selected",
  "Modifica un record tramite chiave primaria (esempio contatti).": "Updates a record by primary key (contacts example).",
  "Modifiche non salvate": "Unsaved changes",
  "Modulo Python": "Python module",
  "Modulo/classe Python non validi": "Invalid Python module/class",
  "Monitor seriale USB: connessione, lettura e invio testo.": "USB serial monitor: connect, read and send text.",
  "Mostra ": "Show ",
  "Mostra / nascondi log": "Show / hide log",
  "Mostra i requisiti prima di aggiungere un componente esterno": "Show requirements before adding an external component",
  "Mostra la finestra.": "Shows the window.",
  "Mostra log": "Show log",
  "Mostra messaggio": "Show message",
  "Mostra un messaggio.": "Shows a message.",
  "Motore Jedi non disponibile: ": "Jedi engine unavailable: ",
  "Motore di analisi terminato.": "Analysis engine stopped.",
  "Motore ricaricato: digita un punto oppure premi Ctrl+Spazio.": "Engine reloaded: type a dot or press Ctrl+Space.",
  "Nasconde la finestra.": "Hides the window.",
  "Nascondi log": "Hide log",
  "Nessun dispositivo USB rilevato": "No USB devices found",
  "Nessun file audio": "No audio file",
  "Nessun pacchetto PIP richiesto. È sufficiente Python con Tkinter.": "No PIP packages required. Python with Tkinter is sufficient.",
  "Nessun pacchetto necessario: SQLite è incluso in Python.": "No packages required: SQLite is included in Python.",
  "Nessuna dipendenza da installare": "No dependencies to install",
  "Nessuna modifica da salvare.": "No changes to save.",
  "Nessuno stream diretto disponibile": "No direct stream available",
  "Nome": "Name",
  "Nome Python del componente:": "Component Python name:",
  "Nome Python non valido o già utilizzato.": "Invalid or duplicate Python name.",
  "Nome Python:": "Python name:",
  "Nome componente": "Component name",
  "Nome componente non valido": "Invalid component name",
  "Nome componente riservato o non valido": "Reserved or invalid component name",
  "Nome del pacchetto (anche con versione, es. Pillow>=10):": "Package name (optionally with a version, e.g. Pillow>=10):",
  "Nome della variabile ambiente non valido.": "Invalid environment variable name.",
  "Nome non valido o duplicato": "Invalid or duplicate name",
  "Nome non valido o già presente": "Invalid or existing name",
  "Nome palette": "Palette name",
  "Nuova finestra": "New window",
  "Nuovo": "New",
  "Nuovo progetto": "New project",
  "Nuovo record": "New record",
  "Nuovo testo": "New text",
  "OpenCV acquisisce il video e richiede NumPy; Pillow converte e visualizza i fotogrammi. Dopo l’installazione macOS deve autorizzare la Fotocamera per Python o l’app avviata.": "OpenCV captures video and requires NumPy; Pillow converts and displays frames. macOS must grant Camera access to Python or the app.",
  "Operazione in corso": "Operation in progress",
  "Operazione in corso…": "Working…",
  "Operazione interrotta prima della verifica finale.": "Operation cancelled before the final check.",
  "Operazione interrotta. I pacchetti già installati vengono conservati.": "Operation cancelled. Packages already installed are kept.",
  "Operazione interrotta. Premi Verifica per controllare lo stato dei pacchetti.": "Operation cancelled. Click Check to inspect package status.",
  "Operazione terminata": "Operation completed",
  "PIP non disponibile: scegli un ambiente Python con PIP.\n": "PIP unavailable: choose a Python environment with PIP.\n",
  "PIP non ha completato l’installazione. Leggi il log per il dettaglio. Nessun requisito viene dichiarato pronto.\n": "PIP could not complete installation. Read the log for details. No requirement is marked ready.\n",
  "Pacchetti PIP": "PIP packages",
  "Pacchetti PIP • preparazione automatica": "PIP packages • automatic preparation",
  "Pacchetti PyPI (separati da virgola)": "PyPI packages (comma separated)",
  "Pacchetti e componenti": "Packages and components",
  "Pacchetti installati": "Installed packages",
  "Pacchetti selezionati": "Selected packages",
  "Pacchetto": "Package",
  "Pacchetto PIP": "PIP package",
  "Pacchetto non valido": "Invalid package",
  "Pagina 1": "Page 1",
  "Pagina 2": "Page 2",
  "Pagina PyPI": "PyPI page",
  "Passo": "Step over",
  "Password (non salvata)": "Password (not saved)",
  "Per aggiungere un widget di una libreria esterna importa un descrittore JSON. Esempio in examples/CTkButton.vtk-component.json. La classe deve accettare master e le proprietà defaults, e supportare place e bind. Le dipendenze sono installate solo su richiesta.": "Import a JSON descriptor to add a widget from an external library. See examples/CTkButton.vtk-component.json. The class must accept master/default properties and support place and bind. Dependencies are installed on request.",
  "Player MP3: apri, riproduci, pausa, riprendi e stop.": "MP3 player: open, play, pause, resume and stop.",
  "Porta": "Port",
  "Porta (0 = predefinita)": "Port (0 = default)",
  "Porta o limite database non validi": "Invalid database port or row limit",
  "Porta o limite righe non validi.": "Invalid port or row limit.",
  "Porte": "Ports",
  "Prepara automaticamente i pacchetti quando inserisci o avvii un componente": "Automatically prepare packages when inserting or running a component",
  "Prepara automaticamente il progetto…": "Automatically prepare project…",
  "Prepara il componente": "Prepare component",
  "Prepara pacchetti del componente…": "Prepare component packages…",
  "Preparo PIP e i requisiti, poi ripeto la verifica…": "Preparing PIP and requirements, then checking again…",
  "Prima": "First",
  "Prima consulta Dettagli PyPI per selezionare una versione": "Open PyPI details first to select a version",
  "Processo attivo": "Active process",
  "Progetto": "Project",
  "Progetto senza nome": "Untitled project",
  "Progetto → ": "Project → ",
  "Pronto": "Ready",
  "Pronto con Python/Tkinter • nessun pacchetto PIP.": "Ready with Python/Tkinter • no PIP packages.",
  "Pronto • ": "Ready • ",
  "Proprietà": "Properties",
  "Proprietà iniziali (JSON)": "Default properties (JSON)",
  "Proprietà non valide": "Invalid properties",
  "Pulisci": "Clear",
  "Pulsante moderno": "Modern button",
  "Pulsante moderno CustomTkinter.": "Modern CustomTkinter button.",
  "PyUSB richiede anche la libreria nativa libusb (su Mac: brew install libusb). Il wizard PIP non installa driver di sistema.": "PyUSB also requires native libusb (on Mac: brew install libusb). The PIP wizard does not install system drivers.",
  "Python e designer": "Python and designer",
  "Python generato / breakpoint": "Generated Python / breakpoints",
  "Python stabile compatibile:": "Compatible stable Python:",
  "Questa applicazione usa la webcam quando viene avviato il componente WebcamView.": "This application uses the camera when WebcamView is started.",
  "Rendering HTML leggero con tkhtmlview.": "Lightweight HTML rendering with tkhtmlview.",
  "Requisiti da preparare: premi Installa / ripara. Gli errori dettagliati sono nella scheda Log.": "Requirements need preparation: click Install / repair. Detailed errors are in the Log tab.",
  "Requisiti e opzioni": "Requirements and options",
  "Ricerca web": "Web search",
  "Riga non trovata o chiave non univoca; transazione annullata.": "Row not found or key not unique; transaction rolled back.",
  "Righe visualizzate (1–5000)": "Visible rows (1–5000)",
  "Rilegge e visualizza i dati; attendi DataLoaded.": "Reloads and displays data; wait for DataLoaded.",
  "Ripeti": "Redo",
  "Riprendi": "Resume",
  "Ripristina pannelli": "Reset panels",
  "Riproduzione locale/streaming tramite VLC. Su Mac finestra video separata; richiede VLC/libVLC.": "Local/streaming playback via VLC. Separate video window on Mac; requires VLC/libVLC.",
  "Risoluzione stream YouTube e riproduzione VLC. Backend alternativi pytubefix/pytube.": "YouTube stream resolution and VLC playback. Alternative pytubefix/pytube backends.",
  "SQLite è incluso in Python. PostgreSQL richiede SQLAlchemy e psycopg; MySQL richiede SQLAlchemy e PyMySQL. Nessuna password viene salvata nel progetto.": "SQLite is included in Python. PostgreSQL requires SQLAlchemy and psycopg; MySQL requires SQLAlchemy and PyMySQL. Passwords are not stored in the project.",
  "SQLite: nessuna installazione. Remoto: SQLAlchemy + psycopg o PyMySQL.\nLa connessione usa l’ambiente Python dell’app. Password vuota: variabile ": "SQLite: no installation. Remote: SQLAlchemy + psycopg or PyMySQL.\nThe connection uses the app Python environment. Empty password: variable ",
  "Salva": "Save",
  "Salva con nome…": "Save as…",
  "Salva configurazione": "Save settings",
  "Salva e applica": "Save and apply",
  "Salva e prepara dipendenze…": "Save and prepare dependencies…",
  "Salva modifiche": "Save changes",
  "Salva tema": "Save theme",
  "Salvare le modifiche prima di proseguire?": "Save changes before continuing?",
  "Salvataggio": "Save",
  "Scansiona USB": "Scan USB",
  "Scegli file SQLite…": "Choose SQLite file…",
  "Scegli il percorso del database SQLite.": "Choose a SQLite database path.",
  "Scegli un componente per vedere funzioni e requisiti.": "Select a component to see its features and requirements.",
  "Scegli un preset oppure personalizza i colori dell’IDE.\nI colori delle finestre create si modificano nel designer.": "Choose a preset or customize IDE colors.\nApplication window colors are edited in the designer.",
  "Schede ttk. add_page(titolo) restituisce un Frame per i widget creati da codice.": "ttk tabs. add_page(title) returns a Frame for widgets created in code.",
  "Scrivi qui…": "Type here…",
  "Scuro": "Dark",
  "Seconda": "Second",
  "Seleziona Python con Tkinter": "Select Python with Tkinter",
  "Seleziona per indice.": "Selects by index.",
  "Seleziona un componente e un evento": "Select a component and an event",
  "Seleziona un componente nella palette.": "Select a component in the palette.",
  "Seleziona un componente. Doppio clic o Invio per inserirlo.": "Select a component. Double-click or press Enter to insert it.",
  "Seleziona una tabella.": "Select a table.",
  "Selezione file": "File selection",
  "Selezione ▾": "Selection ▾",
  "Seppia": "Sepia",
  "Seriale": "Serial",
  "Seriale / Arduino": "Serial / Arduino",
  "Servono anche VLC/libVLC. La disponibilità dei flussi dipende dal servizio video.": "VLC/libVLC is also required. Stream availability depends on the video service.",
  "Sfoglia file…": "Browse files…",
  "Sfondo designer": "Designer background",
  "Sfondo editor": "Editor background",
  "Sfondo pannelli": "Panel background",
  "Solo designer": "Designer only",
  "Solo wheel (opzione avanzata: escludi pacchetti sorgenti)": "Wheels only (advanced: exclude source packages)",
  "Sposta il focus sul componente.": "Moves focus to the component.",
  "Stato": "Status",
  "Stream audio/video combinato non disponibile": "Combined audio/video stream unavailable",
  "Stream risolto: avvio VLC": "Stream resolved: starting VLC",
  "Superficie controlli": "Control surface",
  "Tabella iniziale (facoltativa)": "Initial table (optional)",
  "Tabella non presente nel database.": "Table not found in the database.",
  "Tabelle": "Tables",
  "Tema applicazione…": "Application theme…",
  "Tema del progetto": "Project theme",
  "Tema ttkbootstrap dell’app generata. Vuoto = standard Tk.": "ttkbootstrap theme for the generated app. Empty = standard Tk.",
  "Temi e colori…": "Themes and colors…",
  "Temi e componenti ttk": "ttk themes and components",
  "Testo editor": "Editor text",
  "Testo multiriga con scrollbar integrata.": "Multiline text with a built-in scrollbar.",
  "Testo pannelli": "Panel text",
  "Tipo": "Type",
  "Tipo database": "Database type",
  "Tkinter non disponibile": "Tkinter unavailable",
  "Trascina qui file dal Finder": "Drop Finder files here",
  "Tutti": "All",
  "Tutti i pacchetti del wizard saranno installati in questo Python.\nPuoi scegliere il Python di un ambiente virtuale.": "All wizard packages are installed into this Python.\nYou may select a virtual environment interpreter.",
  "USB generico": "Generic USB",
  "Ultimo errore database": "Last database error",
  "Usa nell’evento DataLoaded: lista di dizionari.": "Use in DataLoaded: a list of dictionaries.",
  "Utente (remoto)": "Username (remote)",
  "Utente remoto": "Remote username",
  "Valore non valido": "Invalid value",
  "Variabile ambiente password": "Password environment variable",
  "Verifica": "Check",
  "Verifica automatica in corso…": "Automatic check in progress…",
  "Verifica finale delle versioni e degli import…\n": "Final version and import checks…\n",
  "Verifica i pacchetti prima di Avvia / Debug": "Check packages before Run / Debug",
  "Verifica non riuscita: ": "Check failed: ",
  "Verifica requisiti senza installare…": "Check requirements without installing…",
  "Verifica sintassi": "Check syntax",
  "Versione": "Version",
  "Video / streaming": "Video / streaming",
  "Video legacy / verificare Python": "Legacy video / check Python compatibility",
  "Vista": "View",
  "Web nativo": "Native web",
  "Webcam inattiva": "Webcam inactive",
  "Webcam live, avvio esplicito e snapshot.": "Live webcam with explicit start and snapshots.",
  "Webcam non disponibile. Controlla i permessi Fotocamera di macOS.": "Webcam unavailable. Check macOS Camera permissions.",
  "Widget moderni": "Modern widgets",
  "YouTube alternativo": "Alternative YouTube backend",
  "class deve essere un singolo identificatore": "class must be a single identifier",
  "defaults deve essere un oggetto JSON": "defaults must be a JSON object",
  "requirements ammette solo nomi/versioni PyPI, senza URL o opzioni": "requirements only accepts PyPI names/versions, not URLs or options",
  "È necessaria la chiave primaria completa e non NULL.": "A complete, non-NULL primary key is required.",
  "È richiesto Python 3.15 o successivo in versione stabile (final), con Tkinter. Le versioni alpha, beta e release candidate non sono accettate.": "Python 3.15 or newer stable (final), with Tkinter, is required. Alpha, beta and release candidates are not accepted.",
  "✓ Sintassi e modello validi.\n": "✓ Syntax and project model are valid.\n",
  "＋ Inserisci nel form": "＋ Insert into form",
  "1/3 • Verifica dei requisiti…": "1/3 • Checking requirements…",
  "2/3 • Installazione in corso. Puoi seguirla nella scheda Log.": "2/3 • Installing. Follow progress in the Log tab.",
  "3/3 • Componente pronto. Requisiti verificati.": "3/3 • Component ready. Requirements verified.",
  " (copia)": " (copy)",
  "  [principale]": "  [main]",
  " • anteprima": " • preview",
  " • Senza chiave primaria: modifica/eliminazione disabilitate.": " • No primary key: update/delete disabled.",
  "* modificato • ": "* modified • ",
  " — cosa puoi fare": " — available actions",
  " Firma: ": " Signature: ",
  "   • argomento: ": "   • argument: ",
  " (stato: ": " (status: ",
  "\nVersione rilevata: ": "\nDetected version: ",
  "\nDipendenze: ": "\nDependencies: ",
  "\nInstalla VLC/libVLC per la stessa architettura di Python.": "\nInstall VLC/libVLC matching your Python architecture.",
  "\nLa password verrà chiesta alla connessione oppuretta dalla variabile ambiente indicata; non viene salvata nel progetto.": "\nThe password is requested at connection time or read from the environment variable; it is not saved in the project.",
  "Motore…": "Engine…",
  "Ctrl+Spazio": "Ctrl+Space",
  "Lingua interfaccia": "Interface language",
  "Lingua dei componenti generati": "Generated component language",
  "Lingua aggiornata": "Language updated",
  "La lingua è stata salvata. Riavvia TkVisualFoundry per applicarla a tutte le finestre.": "The language has been saved. Restart TkVisualFoundry to apply it to all windows.",
  "Italiano": "Italiano",
  "English": "English",
  "Scelta lingua non valida.": "Invalid language selection.",
  "\nLa password verrà chiesta alla connessione oppure letta dalla variabile ambiente indicata; non viene salvata nel progetto.": "\nThe password is requested at connection time or read from the environment variable; it is not saved in the project.",
  "\n[Processo terminato: {v0}]\n": "\n[Process exited: {v0}]\n",
  "Modifica {v0}": "Change {v0}",
  "Imposta {v0}. Valore nel designer: {v1}.": "Set {v0}. Designer value: {v1}.",
  "{v0} righe visualizzate • limite {v1}": "{v0} rows displayed • limit {v1}",
  "Nome non valido o duplicato: {v0}": "Invalid or duplicate name: {v0}",
  "Versione fuori dal requisito ": "Version outside requirement ",
  "Non installato": "Not installed",
  "Versione verificata; modulo esterno non importato": "Version checked; external module not imported",
  "AVVISO: conflitti già presenti nell’ambiente prima dell’installazione; controlla il log.\n": "WARNING: these conflicts were already present before installation; check the log.\n",
  "Debug pdb: continue, next, step, pp espressione, where, break N, quit.\nLa GUI si blocca intenzionalmente ai breakpoint.\n": "pdb debugging: continue, next, step, pp expression, where, break N, quit.\nThe GUI intentionally pauses at breakpoints.\n",
  "Sfoglia…": "Browse…",
  "Scegli…": "Choose…",
  "Carattere…": "Font…",
  "Connetti…": "Connect…",
  "Nome componente già utilizzato.": "Component name already in use.",
  "Ciao!": "Hello!",
  "TkVisualFoundry 1.40\nDesigner visuale Python / Tkinter": "TkVisualFoundry 1.40\nVisual Python / Tkinter designer",
  " • Librerie → Installa dipendenze progetto dopo averlo inserito nel form": " • PIP → Prepare component packages after inserting it into the form",
  "Ctrl+Spazio: completamento.": "Ctrl+Space: completion.",
  "Errore applicazione": "Application error",
  "Seleziona la lingua dell’interfaccia. Il cambio viene applicato al riavvio.": "Choose the interface language. Changes apply after restarting.",
  "TKVISUALFOUNDRY — Guida rapida\n\n1. Inserisci un controllo dalla palette, con doppio clic o Invio.\n2. Modifica le proprietà e premi Applica proprietà.\n3. Doppio clic sul controllo per aprire il codice evento.\n4. Digita messagebox., tk. o self. per i suggerimenti.\n5. Salva il progetto e premi F5.\n\nPIP prepara automaticamente i pacchetti necessari.\nProgetto → Configurazione consente di scegliere lingua, Python e preferenze.\nVista gestisce log e colori. Help contiene le guide dettagliate.\n\nLa lingua dell’interfaccia cambia dopo il riavvio. Il codice e i testi dei progetti restano invariati.": "TKVISUALFOUNDRY — Quick start\n\n1. Insert a control from the palette by double-clicking or pressing Enter.\n2. Edit its properties and click Apply properties.\n3. Double-click the control to open its event code.\n4. Type messagebox., tk. or self. for suggestions.\n5. Save the project and press F5.\n\nPIP automatically prepares the required packages.\nProject → Settings lets you select the language, Python and preferences.\nView manages the log and colors. Help provides detailed guides.\n\nInterface language changes after restarting. Project code and text are preserved."
}

EN_MESSAGES["Database"] = "Database"

EN_MESSAGES['Nel codice evento: self.show("Form2") / self.hide("Form2").\nIl primo form è quello principale; chiuderlo termina l’app.'] = 'In event code: self.show("Form2") / self.hide("Form2").\nThe first form is the main window; closing it ends the app.'

EN_MESSAGES.update({'Errore: ': 'Error: ', '+ Nuovo record': '+ New record'})

EN_MESSAGES.update({'Licenza':'License','Repository/documentazione':'Repository/documentation'})

EN_MESSAGES['Configurazione…'] = 'Configuration…'

EN_MESSAGES.update({'Form e componenti': 'Forms and components', 'File e cartelle': 'Files and folders', 'File e cartelle ▾': 'Files and folders ▾', 'Nuovo file…': 'New file…', 'Nuova cartella…': 'New folder…', 'Importa file…': 'Import file…', 'Rinomina…': 'Rename…', 'Sposta nel cestino': 'Move to trash', 'Includi / escludi dal deploy': 'Include / exclude from deploy', 'Salva il progetto per gestire file e cartelle.': 'Save the project to manage files and folders.', '✓ = incluso nel deploy. File sul disco; cestino in .visualtk-trash. Limite vista: 1500 elementi.': '✓ = included in deploy. Files on disk; trash in .visualtk-trash. View limit: 1500 entries.', 'Nome relativo alla cartella selezionata:': 'Name relative to the selected folder:', 'File di progetto': 'Project files', 'Usa Salva con nome per il file del progetto.': 'Use Save As for the project file.', 'Nuovo nome. I riferimenti nel codice non vengono modificati:': 'New name. Code references are not updated:', 'Puoi recuperarlo dalla cartella .visualtk-trash. I riferimenti nel codice non vengono modificati.': 'Recover it from .visualtk-trash. Code references are not updated.', 'Escludi prima la cartella contenitore.': 'Exclude the containing folder first.', 'Il progetto si modifica nel designer.': 'Edit the project in the designer.', 'Editor limitato a file UTF-8 fino a 2 MB.': 'The editor supports UTF-8 files up to 2 MB.', 'File modificato o spostato sul disco: riaprilo prima di salvare.': 'File changed or moved on disk: reopen it before saving.', 'Salva e chiudi gli editor dei file prima del deploy.': 'Save and close file editors before deploying.', 'Nome applicazione': 'Application name', 'Versione': 'Version', 'Destinazione': 'Destination', 'Genera un kit Mac + Windows. La compilazione va eseguita sul sistema di destinazione. Include soltanto i file contrassegnati ✓.': 'Generate a Mac + Windows kit. Build on the target OS. Only files marked ✓ are included.', 'Compila anche su questo computer (installa le dipendenze nel kit)': 'Also build on this computer (install dependencies in the kit)', 'Scegli una cartella di destinazione.': 'Choose an output folder.', 'Kit pronto. Leggi README_DEPLOY.md e usa gli script del sistema di destinazione.': 'Kit ready. Read README_DEPLOY.md and use the scripts for the target OS.', 'Genera deploy': 'Generate deployment'})

EN_MESSAGES['Per mantenere i percorsi relativi, copia prima la cartella del progetto nella nuova destinazione e aprila da lì.']='To preserve relative paths, copy the project folder to the new destination first, then open it there.'

EN_MESSAGES['File e deploy']='Files and deployment'

EN_MESSAGES['Chiudi gli editor di questi file prima di rinominare o spostare.']='Close the editors for these files before renaming or moving them.'

EN_MESSAGES.update({'Librerie e temi': 'Libraries and themes', 'Librerie e temi…': 'Libraries and themes…', 'Installazione, prova grafica e deploy sono verifiche distinte.': 'Installation, GUI checks and deployment are separate checks.', 'Libreria': 'Library', 'Tipo': 'Type', 'Integrazione': 'Integration', 'Ultima verifica': 'Last check', 'Controlli: ': 'Controls: ', 'Verifica in un processo separato…': 'Checking in a separate process…', 'Prepara con PIP…': 'Prepare with PIP…', 'Verifica installazione': 'Check installation', 'Prova grafica isolata': 'Isolated GUI test', 'Tema del progetto…': 'Project theme…', 'Motore tema ttk': 'ttk theme engine', 'Nome tema': 'Theme name', 'Modalità tema': 'Theme mode', 'Aspetto CustomTkinter': 'CustomTkinter appearance', 'File Tcl relativo': 'Relative Tcl file', 'Il tema ttk non modifica i controlli Tk classici o CustomTkinter. Anteprima del designer schematica; usa la prova grafica isolata.': 'ttk themes do not restyle classic Tk or CustomTkinter controls. The designer preview is schematic; use the isolated GUI test.', 'Seleziona Azure o Forest prima di importare.': 'Select Azure or Forest before importing.', 'Cartella del tema con Tcl e immagini': 'Theme folder containing Tcl files and images', 'Importa cartella tema…': 'Import theme folder…', 'Pagina visibile': 'Visible page', 'Legge i dati della tabella.': 'Reads table data.', 'Sostituisce i dati della tabella.': 'Replaces table data.', 'Legge una cella.': 'Reads a cell.', 'Modifica una cella.': 'Changes a cell.', 'Centra la mappa sulle coordinate.': 'Centers the map on coordinates.', 'Imposta lo zoom della mappa.': 'Sets map zoom.', 'Cerca un indirizzo online.': 'Looks up an address online.', 'Aggiunge un marcatore.': 'Adds a marker.', 'Rimuove i marcatori.': 'Removes markers.', 'Legge la pagina attiva.': 'Reads the active page.', 'Seleziona una pagina.': 'Selects a page.', 'Aggiunge una pagina e restituisce il contenitore.': 'Adds a page and returns its container.', 'Legge o seleziona la scheda.': 'Reads or selects the tab.', 'Imposta la selezione.': 'Sets the selection.', 'Tutte le famiglie': 'All families', 'Installata': 'Installed', 'Da verificare': 'Unchecked', 'Prova grafica superata': 'GUI test passed', 'Da preparare': 'Setup required', 'Non supportata': 'Unsupported', 'Motore separato': 'Separate engine', 'Risorse locali': 'Local resources', 'Adattatore': 'Adapter', 'Sperimentale': 'Experimental'})

EN_MESSAGES['Errore']='Error'

EN_MESSAGES['Deploy della libreria: non verificato automaticamente.']='Library deployment: not automatically verified.'

EN_MESSAGES.update({'Controlli Tk standard': 'Standard Tk controls', 'Controlli standard con temi ttk': 'Themed standard controls', 'Controlli moderni e contenitori annidati': 'Modern controls and nested containers', 'Temi della serie 1.x; versione vincolata per compatibilità': 'Legacy 1.x theme names; version constrained for compatibility', 'Raccolta di temi ttk; controlla le licenze prima della distribuzione': 'ttk theme collection; review theme licenses before distribution', 'Tema ttk Sun Valley chiaro/scuro': 'Sun Valley light/dark ttk theme', 'Importa la cartella contenente azure.tcl e le sue risorse': 'Import a theme folder containing azure.tcl and its assets', 'Importa la cartella con forest-light.tcl e forest-dark.tcl': 'Import a theme folder containing forest-light.tcl and forest-dark.tcl', 'tkinter.tix è stato rimosso da Python 3.13; non disponibile in questo ambiente': 'tkinter.tix was removed in Python 3.13; unavailable in this IDE runtime', 'Megawidget selezionati con inizializzazione in esecuzione': 'Selected megawidgets with runtime initialization', 'Calendario e campo data': 'Calendar and DateEntry', 'Tabella modificabile con eventi per celle e selezioni': 'Editable table with cell and selection events', 'Adattatore HTML/web': 'HTML/web adapter', 'Mappe, coordinate e marcatori; possono servire servizi cartografici online': 'Maps, coordinates, markers; online tile services may be required', 'Video opzionale; verifica la compatibilità di PyAV': 'Optional video adapter; PyAV compatibility must be checked', 'Drag and drop nativo; binari Tcl/Tk specifici per piattaforma': 'Native drag and drop; platform-specific Tcl/Tk binaries', 'Motore di layout/eventi separato; non disponibile come widget nella palette': 'Separate layout/event engine; not available as palette widgets', 'Modello App/contenitori separato; non disponibile come widget nella palette': 'Separate App/container model; not available as palette widgets'})

EN_MESSAGES.update({'Controlli':'Controls','Temi':'Themes'})

EN_MESSAGES.update({' • anteprima del testo della prima pagina': ' • first-page text preview', 'API OpenAI, Claude e Gemini: scelta modello, invio testo e risposta asincrona. Chiavi esterne.': 'OpenAI, Claude and Gemini APIs: model selection, text requests and asynchronous responses. External credentials.', 'API ufficiali: chiave nella variabile ambiente configurata. Puoi anche usare Chiave API per la sola sessione. Il testo viene inviato soltanto con Invia.': 'Official APIs: use the configured environment variable or an API key for this session. Text is sent only when you click Send.', 'Accesso Drive: app o tutti i file': 'Drive access: app files or all files', 'Anteprima con l’app associata e invio al sistema di stampa. Richiede stampante e driver.': 'Preview in the associated app and submit print jobs. Requires a printer and drivers.', 'Anteprima e dialogo tramite l’app associata. Invio diretto con conferma; su Windows solo stampante predefinita e una copia.': 'Preview/dialog through the associated app. Direct submission with confirmation; Windows supports the default printer and one copy.', 'Apri MIDI…': 'Open MIDI…', 'Apri Excel…': 'Open Excel…', 'Apri PDF…': 'Open PDF…', 'Modifica cella…': 'Edit cell…', 'Estrai testo': 'Extract text', 'Unisci PDF…': 'Merge PDFs…', 'Estrai pagine…': 'Extract pages…', 'Salva testo…': 'Save text…', 'Apri anteprima / dialogo di stampa': 'Open preview / print dialog', 'Apri un documento e attendi la fine dell’operazione.': 'Open a document and wait for the operation to finish.', 'Autenticazione Drive': 'Drive authentication', 'Bucket S3': 'S3 bucket', 'Carica file…': 'Upload file…', 'Cella Excel': 'Excel cell', 'Chiave API solo per questa sessione (non viene salvata):': 'API key for this session only (not saved):', 'Chiave API…': 'API key…', 'Client OAuth Desktop di Google (JSON)': 'Google Desktop OAuth client (JSON)', 'Colonna (da 1):': 'Column (starting at 1):', 'Configura servizio': 'Configure service', 'Connetti prima il servizio.': 'Connect to the service first.', 'Copie:': 'Copies:', 'Credenziali solo per questa sessione.': 'Credentials for this session only.', 'Credenziali…': 'Credentials…', 'Drive: abilita Drive API e crea un client OAuth Desktop. app limita l’accesso ai file dell’app; all richiede consenso più ampio. S3/WebDAV richiedono il proprio account. Credenziali inseribili anche solo in esecuzione.': 'Drive: enable Drive API and create a Desktop OAuth client. app limits access to app files; all needs broader consent. S3/WebDAV need their own account. Credentials can be entered at runtime only.', 'Elenca file': 'List files', 'File iniziale (facoltativo)': 'Initial file (optional)', 'Foglio iniziale': 'Initial sheet', 'Funzioni PDF testuali e pagine; niente OCR o rendering grafico. I PDF cifrati richiedono la password in esecuzione.': 'PDF text and page operations; no OCR or graphical rendering. Encrypted PDFs require a password at runtime.', 'Google Drive, S3/MinIO e WebDAV: elenco, caricamento e download. Credenziali esterne.': 'Google Drive, S3/MinIO and WebDAV: list, upload and download. External credentials.', 'ID cartella Drive / prefisso S3-WebDAV': 'Drive folder ID / S3-WebDAV prefix', 'ID modello (o selezionalo nell’app)': 'Model ID (or choose it in the app)', 'Invia alla stampa…': 'Submit print job…', 'Inviare questo documento alla stampa?': 'Submit this document for printing?', 'Legge, crea e modifica file XLSX/XLSM, fogli e celle. Non calcola formule.': 'Read, create and edit XLSX/XLSM files, sheets and cells. Does not calculate formulas.', 'Limite token di output': 'Output token limit', 'MIDI richiede una porta e un sintetizzatore esterno o virtuale. Il componente non include strumenti audio.': 'MIDI requires an output and an external or virtual synthesizer. Audio instruments are not included.', 'Modelli': 'Models', 'Nome uscita MIDI': 'MIDI output name', 'Non inserire segreti nei campi: usa nomi di variabili ambiente. Le credenziali di sessione si inseriscono solo nell’app in esecuzione.': 'Enter environment variable names, not secrets. Session credentials are entered only in the running app.', 'Pagine da estrarre, separate da virgola (da 1):': 'Pages to extract, comma-separated (starting at 1):', 'Pagine: ': 'Pages: ', 'Password facoltativa (lascia vuoto se non cifrato):': 'Optional password (leave blank if unencrypted):', 'Pausa / riprendi': 'Pause / resume', 'Per il dialogo nativo apri il documento e usa Stampa nell’app associata. Su Windows invio diretto solo alla stampante predefinita, una copia.': 'For the native dialog, open the document and use Print in its app. Windows direct printing uses the default printer and one copy.', 'Richiesta affidata al sistema di stampa: ': 'Request handed to the print system: ', 'Riga (da 1):': 'Row (starting at 1):', 'Righe in anteprima': 'Preview rows', 'Riproduce file MIDI su un’uscita collegata a un sintetizzatore; pausa e stop.': 'Play MIDI files through an output connected to a synthesizer; pause and stop.', 'Riproduci': 'Play', 'Scarica file…': 'Download file…', 'Scegli prima un file.': 'Choose a file first.', 'Seleziona un’uscita MIDI collegata a un sintetizzatore. Nessun sintetizzatore audio è incluso.': 'Select a MIDI output connected to a synthesizer. No audio synthesizer is included.', 'Serve un account API del fornitore, con accesso e fatturazione propri. L’abbonamento ChatGPT/Claude/Gemini non imposta le API. In esecuzione usa Chiave API oppure la variabile ambiente. Nessuna richiesta a pagamento durante il design.': 'A provider API account with its own access and billing is required. Chat subscriptions do not configure API access. Use API key at runtime or an environment variable. No paid requests occur during design.', 'Servizio': 'Service', 'Stampa': 'Print', 'Stampante (vuoto = predefinita):': 'Printer (blank = default):', 'Testo PDF, unione ed estrazione pagine; anteprima testuale, senza OCR.': 'PDF text, merge and page extraction; text preview without OCR.', 'Usa per questa sessione': 'Use for this session', 'Uscite MIDI': 'MIDI outputs', 'Uscite trovate: ': 'Outputs found: ', 'Valore (JSON per numeri, booleani o null; altrimenti testo):': 'Value (JSON for numbers, booleans or null; otherwise text):', 'Variabile ambiente della chiave API': 'API key environment variable', 'Variabile con URL WebDAV': 'Variable containing WebDAV URL', 'Variabile con endpoint S3/MinIO': 'Variable containing S3/MinIO endpoint', 'Variabile con password WebDAV': 'Variable containing WebDAV password', 'Variabile con percorso JSON OAuth': 'Variable containing OAuth JSON path', 'Variabile con percorso token esterno': 'Variable containing external token path', 'Variabile con utente WebDAV': 'Variable containing WebDAV username', 'XLSX e XLSM: formule conservate, non calcolate. Salva una copia; elementi Excel particolari possono non essere preservati.': 'XLSX/XLSM formulas are preserved, not calculated. Save a copy; some Excel features may not be preserved.'})

EN_MESSAGES['Documenti, cloud e LLM']='Documents, cloud and LLMs'

EN_MESSAGES.update({'Documentazione': 'Documentation', 'Sito ufficiale': 'Official website', 'API installata (pydoc)': 'Installed API (pydoc)', 'Controlli librerie e documentazione…': 'Library and documentation checks…', 'Caricamento API…': 'Loading API…', 'Controllo in background… Puoi continuare a lavorare.': 'Checking in the background… You can continue working.', 'Controllo non completato: ': 'Check incomplete: ', 'Controllo versioni stabili (compatibilità Python e vincoli dichiarati).': 'Stable version check (Python compatibility and declared constraints).', 'PIP verificherà anche dipendenze e disponibilità di wheel prima di installare.': 'PIP will also check dependencies and wheel availability before installation.', 'Documentazione:': 'Documentation:', 'Controlli iniziali': 'Startup checks', 'Ricontrolla': 'Check again', 'Aggiorna con wizard PIP…': 'Update with PIP wizard…', 'Nessun controllo eseguito.': 'No checks performed.', 'Completa automaticamente le virgolette dei valori testuali': 'Automatically complete quotation marks for text values', 'Controlla librerie, PIP e documentazione all’avvio': 'Check libraries, PIP and documentation at startup', 'Proprietà modificabili da codice': 'Properties editable in code', 'Metodi ed esempi': 'Methods and examples', 'Configurazione nel designer': 'Designer configuration', 'Pacchetti richiesti': 'Required packages', 'Libreria standard': 'Standard library', 'Controllo in corso…': 'Checking…', 'Risultati controlli iniziali…': 'Startup check results…'})

EN_MESSAGES.update({'Alfabetico': 'Alphabetical', 'Aspetto e comportamento': 'Appearance and behavior', 'Casella degli strumenti': 'Toolbox', 'Classico VB6': 'VB6 Classic', 'Codice': 'Code', 'Codice progetto': 'Project code', 'Designer': 'Designer', 'Disposizione': 'Layout', 'Identità': 'Identity', 'Per categoria': 'Categorized', 'Seleziona una proprietà per vedere il valore.': 'Select a property to see its value.'})

EN_MESSAGES.update({'Cerca componente':'Find component','Filtra le proprietà per nome':'Filter properties by name'})

EN_MESSAGES['Le coordinate devono essere numeri interi.']='Coordinates must be integers.'

EN_MESSAGES.update({'Aggiorna indice': 'Refresh index', 'Cache oltre 24 ore: usa Aggiorna indice per aggiornarla.': 'Cache is over 24 hours old: use Refresh index to update it.', 'Caricamento catalogo… Il primo accesso a Tutto PyPI scarica l’indice dei nomi.': 'Loading catalog… First access to All PyPI downloads the project-name index.', 'Catalogo pacchetti…': 'Package catalog…', 'Cerca e installa pacchetti senza uscire dall’app. Tutto PyPI cerca nei nomi; seleziona un risultato per i dettagli.': 'Find and install packages inside the app. All PyPI searches names; select a result for details.', 'Consigliati': 'Recommended', 'Indice aggiornato da PyPI': 'Index refreshed from PyPI', 'Indice locale': 'Local index', 'Installati': 'Installed', 'Interprete cambiato: seleziona nuovamente il pacchetto.': 'Interpreter changed: select the package again.', 'Lettura dettagli: ': 'Loading details: ', 'Nessuna versione stabile compatibile': 'No compatible stable release', 'Precedenti': 'Previous', 'Seleziona un pacchetto e attendi i dettagli.': 'Select a package and wait for its details.', 'Successivi': 'Next', 'Tutto PyPI': 'All PyPI', 'Versione installata': 'Installed version', 'Nome esatto…': 'Exact name…'})

EN_MESSAGES.update({'Icona applicazione': 'Application icon', 'Icona non disponibile: selezionala nuovamente.': 'Icon unavailable: select it again.', 'Scegli icona applicazione': 'Choose application icon', 'Rimuovi': 'Remove', 'PNG, ICO o ICNS quadrata, almeno 256 px. Consigliata: PNG trasparente 1024 × 1024. Conversione automatica per Mac e Windows.': 'Square PNG, ICO or ICNS, at least 256 px. Recommended: transparent 1024 × 1024 PNG. Automatic conversion for Mac and Windows.'})

EN_MESSAGES.update({' selezionati': ' selected', 'Allinea a sinistra': 'Align left', 'Allinea in alto': 'Align top', 'Allinea a destra': 'Align right', 'Allinea in basso': 'Align bottom', 'Stessa larghezza': 'Same width', 'Stessa altezza': 'Same height', 'Distribuisci orizzontalmente': 'Distribute horizontally', 'Distribuisci verticalmente': 'Distribute vertically'})

EN_MESSAGES.update({'Problemi': 'Problems', 'Analizza progetto': 'Analyze project', 'Analisi statica: nessun codice del progetto viene eseguito.': 'Static analysis: project code is never executed.', 'Tipo': 'Type', 'Oggetto': 'Object', 'Evento': 'Event', 'Riga': 'Line', 'Descrizione': 'Description', 'Analisi in corso…': 'Analyzing…', 'Progetto o interprete cambiato: ripeti l’analisi.': 'Project or interpreter changed: analyze again.', 'Errore': 'Error', 'Avviso': 'Warning', 'Problemi rilevati: ': 'Problems found: ', 'Verifica import non disponibile: ': 'Import check unavailable: ', 'Riferimento self non riconosciuto: ': 'Unrecognized self reference: ', 'Modulo non rilevato nell’ambiente: ': 'Module not detected in environment: '})

EN_MESSAGES.update({'Ambiente Python del progetto': 'Project Python environment', 'Ogni progetto può usare una propria .venv: i pacchetti restano separati dagli altri progetti.': 'Each project can use its own .venv, keeping packages separate from other projects.', 'Creazione ambiente in corso…': 'Creating environment…', 'Crea / usa .venv e prepara pacchetti': 'Create / use .venv and prepare packages', 'Usa interprete globale': 'Use global interpreter', 'Progetto cambiato: riapri la gestione ambiente.': 'Project changed: reopen environment management.'})

EN_MESSAGES.update({'Anteprima': 'Preview', 'segnaposto': 'placeholder', 'Anteprima — F6': 'Preview — F6', 'Chiudi anteprima': 'Close preview', 'Anteprima reale: eventi e codice di avvio del progetto esclusi.\n': 'Live form preview: project events and startup code excluded.\n', 'Componenti mostrati come segnaposto: ': 'Components shown as placeholders: ', '\n[Anteprima terminata: {code}]\n': '\n[Preview ended: {code}]\n', 'Errore anteprima: ': 'Preview error: '})

EN_MESSAGES.update({'Correggi gli errori di sintassi prima della rinomina.': 'Fix syntax errors before renaming.', 'Riferimento ambiguo da controllare: ': 'Ambiguous reference to review: ', 'Accesso dinamico da controllare manualmente.': 'Dynamic access needs manual review.', 'Nome Python non valido o riservato.': 'Invalid or reserved Python name.', 'Oggetto non trovato.': 'Object not found.', 'Nome già usato nel progetto.': 'Name already used in the project.', 'Rinomina intelligente': 'Smart rename', 'Nuovo nome Python:': 'New Python name:', 'Anteprima della rinomina': 'Rename preview', 'Controlla le modifiche. Testi, commenti e file Python esterni non vengono riscritti.': 'Review the changes. Text, comments and external Python files are not rewritten.', 'Riferimenti costruiti dinamicamente o contenuti in stringhe generiche richiedono verifica manuale.': 'Dynamically built references and generic strings need manual review.', 'Il progetto è cambiato: ripeti la rinomina.': 'The project changed: repeat the rename.', 'Applica rinomina': 'Apply rename', 'Rinomina intelligente…': 'Smart rename…'})

EN_MESSAGES['Nome non normalizzato: verifica i riferimenti manualmente.']='Non-normalized name: review references manually.'

EN_MESSAGES['Per rinominare usa Azioni → Rinomina intelligente…']='To rename, use Actions → Smart rename…'

EN_MESSAGES.update({'Apri come copia recuperata': 'Open as recovered copy', 'Confronto troncato per dimensione.': 'Comparison truncated because of size.', 'Copie locali: ': 'Local snapshots: ', 'Copie ogni 60 secondi delle modifiche al progetto. Recupera apre una copia: il file originale non viene sovrascritto.': 'Snapshots of project changes every 60 seconds. Recovery opens a copy: the original file is not overwritten.', 'Crea copie locali automatiche del progetto ogni 60 secondi': 'Create automatic local project snapshots every 60 seconds', 'Cronologia e recupero locale': 'Local history and recovery', 'Cronologia locale': 'Local history', 'Data': 'Date', 'Errore cronologia locale': 'Local history error', 'Nessuna differenza.': 'No differences.', 'Recupero': 'Recovery', 'Salva punto locale': 'Save local checkpoint'})

EN_MESSAGES.update({'Ancoraggi adattivi': 'Adaptive anchors', 'Seleziona almeno un componente.': 'Select at least one control.', 'Scegli i bordi da mantenere. Due bordi opposti allargano il controllo; nessun bordo lo mantiene centrato rispetto alla variazione del contenitore.': 'Choose edges to preserve. Opposite edges stretch the control; no edges center it relative to the container size change.', 'Sinistra': 'Left', 'Alto': 'Top', 'Destra': 'Right', 'Basso': 'Bottom', 'Larghezza minima': 'Minimum width', 'Altezza minima': 'Minimum height', 'Prima fase: controlli con geometria Tk/ttk su form e frame/canvas ordinari. CustomTkinter, pagine di schede e contenitori scorrevoli interni richiedono ancora layout da codice.': 'First stage: Tk/ttk geometry on forms and ordinary frames/canvases. CustomTkinter, tab-page contents and scrollable internals still need code-managed layout.', 'La selezione è cambiata: riapri gli ancoraggi.': 'Selection changed: reopen anchor settings.', 'Ripristina posizione fissa': 'Restore fixed position', 'Ancoraggi adattivi…': 'Adaptive anchors…'})

EN_MESSAGES.update({'Controlli Tk/ttk su form, frame/canvas e pagine Notebook. CustomTkinter e contenitori scorrevoli interni richiedono ancora layout da codice.':'Tk/ttk controls on forms, frames/canvases and Notebook pages. CustomTkinter and scrollable internals still need code-managed layout.'})

EN_MESSAGES.update({'Debug: in attesa del programma':'Debug: waiting for program','Debug terminato':'Debug finished','Debug fermo alla riga {v0}':'Debug paused at line {v0}','Debug fermo fuori dal sorgente generato':'Debug paused outside generated source','Debug: esecuzione in corso':'Debug: running','Debug non avviato':'Debug not started','Mostra riga':'Show line','Arresta il debug prima di cambiare i breakpoint.':'Stop debugging before changing breakpoints.'})

EN_MESSAGES.update({'Variabili / Ispettore':'Variables / Inspector','Monitoraggio per il prossimo avvio':'Monitor next launch','Filtra':'Filter','Avvia con F5 o F9 per osservare le variabili.':'Launch with F5 or F9 to inspect variables.','Variabile / ambito':'Variable / scope','Valore':'Value','Campioni ogni 0,5 s. Locali attive o ultima funzione osservata; valori e contenitori limitati. Nessuna espressione o proprietà viene eseguita.':'Samples every 0.5 s. Active locals or last observed function; bounded values and containers. No expressions or properties are executed.','In attesa del primo campione…':'Waiting for the first sample…','Locali':'Locals','Ultime locali':'Last locals','Globali':'Globals','Attributi self':'self attributes','Stack delle chiamate':'Call stack','In pausa: valori del punto di arresto':'Paused: values at the stopping point','In esecuzione: valori campionati':'Running: sampled values','Terminato: ultimi valori disponibili':'Finished: last available values','Valori campionati':'Sampled values','Ispettore':'Inspector','Monitoraggio disattivato per questo avvio.':'Monitoring disabled for this launch.'})

EN_MESSAGES.update({'Monitoraggio non avviato':'Monitoring not started','Terminato prima del primo campione':'Finished before the first sample'})

EN_MESSAGES.update({'Breakpoint · ⇧F9':'Breakpoint · ⇧F9','Scegli una riga di codice, non vuota o di solo commento.':'Choose a code line, not an empty or comment-only line.','Breakpoint non eseguibile: ':'Non-executable breakpoint: '})

EN_MESSAGES.update({'Breakpoint rimossi da righe eliminate: ':'Breakpoints removed from deleted lines: '})
EN_MESSAGES.update({'Breakpoint':'Breakpoint'})

EN_MESSAGES.update({'Attiva/disattiva riga · ⇧F9':'Toggle line · ⇧F9','Rimuovi breakpoint di questo codice':'Clear breakpoints in this code'})

EN_MESSAGES.update({'Watch / Osserva':'Watch','Aggiungi Watch':'Add watch','Rimuovi selezionata':'Remove selected',"Percorsi: self.contatore, self.samples[0], config['porta'], globals.nome, locals.nome. Nessuna chiamata o espressione aritmetica.":"Paths: self.counter, self.samples[0], config['port'], globals.name, locals.name. No calls or arithmetic.",'Percorso':'Path','Ambito':'Scope','Sono consentite al massimo 100 Watch.':'Up to 100 watches are allowed.','Watch':'Watch','Non disponibile nel campione':'Unavailable in sample','Nessun campione della sessione corrente':'No sample from the current session'})

EN_MESSAGES.update({'Usa un percorso di variabile con al massimo 256 caratteri.':'Use a variable path of at most 256 characters.','Percorso Watch non valido.':'Invalid watch path.','Le Watch accettano nomi, attributi, indici interi non negativi e chiavi stringa; chiamate e calcoli non sono supportati.':'Watches accept names, attributes and literal non-negative indices/string keys; calls and arithmetic are not supported.','Percorso Watch troppo profondo.':'Watch path is too deep.','Usa al massimo 100 percorsi Watch distinti.':'Use up to 100 unique watch paths.'})

EN_MESSAGES.update({'Seleziona frame':'Select frame','Seleziona un frame durante una pausa del debug corrente.':'Select a frame while the current debug session is paused.'})

EN_MESSAGES.update({'Palette dei comandi':'Command palette','Cerca una funzione, poi premi Invio. Puoi usare termini italiani o inglesi.':'Find a function, then press Enter. You can search in Italian or English.','↑↓ seleziona · Invio esegue · Esc chiude. Senza ricerca, i comandi recenti sono in cima.':'↑↓ select · Enter runs · Esc closes. With no query, recent commands appear first.','Comandi trovati: {v0}':'Commands found: {v0}','Nessun comando trovato.':'No commands found.','Cerca un comando…':'Find a command…'})

EN_MESSAGES.update({'Visualizzatore dati': 'Data viewer', 'Visualizzatore dati…': 'Data viewer…', 'Apri un file dati per controllarne il contenuto.': 'Open a data file to inspect its contents.', 'Apri file dati…': 'Open data file…', 'Aggiorna ogni 2 secondi': 'Refresh every 2 seconds', 'Nuovo riferimento': 'Reset baseline', 'Tabella / foglio': 'Table / sheet', 'Filtra anteprima': 'Filter preview', 'Prepara lettore PIP…': 'Prepare reader with PIP…', 'Sola lettura • confronto sulla sola anteprima: massimo 500 righe, 80 colonne, 512 caratteri per cella. CSV: prima riga come intestazione. Excel: formule visibili, non calcolate.': 'Read only • comparison covers the preview only: up to 500 rows, 80 columns, 512 characters per cell. CSV: first row is the header. Excel: formulas shown, not calculated.', 'File dati': 'Data files', 'Tutti i file': 'All files', 'Lettura in corso…': 'Reading…', 'Lettura non riuscita: {v0}': 'Read failed: {v0}', 'Letto: {v0} • Righe nel campione: {v1} • Aggiunte: {v2}, rimosse: {v3} • Colonne cambiate: {v4}': 'Read: {v0} • Sample rows: {v1} • Added: {v2}, removed: {v3} • Columns changed: {v4}', 'Riferimento aggiornato al campione visualizzato.': 'Baseline reset to the displayed sample.', 'Questo formato non richiede pacchetti PIP oppure non è supportato.': 'This format requires no PIP packages or is unsupported.'})

EN_MESSAGES.update({'Sì':'Yes','No':'No','Mostra riferimento':'Show baseline'})

EN_MESSAGES.update({' • Ultima lettura riuscita: {v0}':' • Last successful read: {v0}'})

EN_MESSAGES.update({'Il codice del progetto e degli eventi deve essere testo.':'Project and event code must be text.','Struttura del form non valida.':'Invalid form structure.'})

EN_MESSAGES.update({'Ricerca globale': 'Global search', 'Ricerca globale…': 'Global search…', 'Cerca negli eventi e nei file Python, inclusi gli editor non salvati.': 'Search events and Python files, including unsaved editors.', 'Cerca nel progetto': 'Search project', 'Interrompi': 'Stop', 'Maiuscole/minuscole': 'Match case', 'Parola intera': 'Whole word', 'Componente / file': 'Component / file', 'Doppio clic o Invio apre la riga. Ricerca letterale; nessun file viene salvato. Limiti: 1.000 risultati, 200 file Python, 2 MiB per sorgente, 20 MiB totali.': 'Double-click or Enter opens the line. Literal search; no files are saved. Limits: 1,000 results, 200 Python files, 2 MiB per source, 20 MiB total.', 'Ricerca in corso…': 'Searching…', 'Ricerca interrotta.': 'Search stopped.', 'Progetto cambiato: ripeti la ricerca.': 'Project changed: search again.', 'Ricerca non riuscita: {v0}': 'Search failed: {v0}', ' • Risultati limitati': ' • Results limited', ' • Sorgenti escluse o limiti: {v0}': ' • Skipped sources or limits: {v0}', ' • Salva il progetto per cercare anche nei file Python.': ' • Save the project to search Python files too.', 'Risultati: {v0}': 'Results: {v0}', 'Sorgente modificata: ripeti la ricerca prima di navigare.': 'Source changed: search again before navigating.', 'Risultato non più disponibile: {v0}': 'Result no longer available: {v0}'})

EN_MESSAGES.update({'Progetto vuoto': 'Blank project', 'Base': 'Basic', 'Un form vuoto: costruisci liberamente la tua applicazione.': 'An empty form: build your own application freely.', 'Gioco a quiz': 'Quiz game', 'Giochi': 'Games', 'Cinque domande, quattro risposte, punteggio e riavvio. Modifica il questionario nel codice di avvio.': 'Five questions, four answers, scoring and restart. Edit the question bank in startup code.', 'Simulatore di dadi': 'Dice roller', 'D6, D20 e D100, da 1 a 100 dadi e bonus. Controlli degli input e totale.': 'D6, D20 and D100, 1–100 dice and a bonus. Input checks and total.', 'Convertitore di testi': 'Text converter', 'Utilità': 'Utilities', 'Maiuscolo, minuscolo, camelCase, liste Markdown e conteggio parole/caratteri.': 'Uppercase, lowercase, camelCase, Markdown lists and word/character counts.', 'Post-it digitali': 'Sticky notes', 'Una nota colorata con apertura e salvataggio manuale UTF-8. Nessun salvataggio automatico.': 'A colorful note with manual UTF-8 open/save. No automatic saving.', 'Nuovo progetto • scegli un modello': 'New project • choose a template', 'Da quale progetto vuoi partire?': 'Which project would you like to start from?', 'I quattro modelli pronti hanno codice commentato in inglese e controlli modificabili nel designer. Non vengono eseguiti durante la scelta.': 'The four starters have English code comments and controls editable in the designer. They do not run during selection.', 'Pacchetti richiesti: ': 'Required packages: ', 'Nessun PIP aggiuntivo: solo libreria standard.': 'No extra PIP packages: standard library only.', 'Crea progetto': 'Create project'})

EN_MESSAGES.update({'Trova l’intruso': 'Odd One Out', 'Cinque turni su una griglia di nove tessere: trova il simbolo diverso e accumula punti.': 'Five rounds on a nine-tile grid: find the different symbol and score points.', 'Memory • coppie': 'Memory pairs', 'Otto coppie di lettere, contatore mosse e riavvio. Le coppie sbagliate si richiudono dopo una breve pausa.': 'Eight pairs of letters, move counter and restart. Mismatched cards hide after a short pause.', 'Gioco del 15': 'Sliding 15 puzzle', 'Griglia 4×4, mosse legali e mescolamento sempre risolvibile. Riordina le tessere da 1 a 15.': 'A 4×4 grid with legal moves and solvable shuffles. Arrange tiles from 1 to 15.', 'Mini-Paint': 'Mini-Paint', 'Creatività': 'Creativity', 'Pennello, gomma bianca, linee, rettangoli e ovali. Colori, spessore, pulizia ed esportazione EPS.': 'Brush, white eraser, lines, rectangles and ovals. Colors, stroke width, clear and EPS export.', 'I modelli pronti hanno codice commentato in inglese e controlli modificabili nel designer. Non vengono eseguiti durante la scelta.': 'The starters have English code comments and designer-editable controls. They do not run during selection.'})

EN_MESSAGES.update({'Sveglia e timer': 'Alarm and timers', 'Cronometro con pausa, conto alla rovescia e sveglia HH:MM. Segnale tramite campanella di sistema.': 'Stopwatch with pause, countdown and HH:MM alarm. Alerts use the system bell.', 'Blocco note a schede': 'Tabbed notepad', 'Note multiple con apertura e salvataggio UTF-8, schede dinamiche e protezione delle modifiche non salvate.': 'Multiple notes with UTF-8 open/save, dynamic tabs and unsaved-change protection.', 'Tracker di abitudini': 'Habit tracker', 'Organizzazione': 'Organization', 'Abitudini giornaliere, serie consecutive e cronologia. Apertura e salvataggio manuale JSON.': 'Daily habits, current streaks and history. Manual JSON open/save.', 'Editor Pixel Art': 'Pixel Art editor', 'Griglia 16×16, colori e gomma bianca. Esporta immagini PPM o SVG senza librerie esterne.': 'A 16×16 grid, colors and white eraser. Export PPM or SVG images without external libraries.'})

EN_MESSAGES.update({'Calcolatrice scientifica': 'Scientific calculator', 'Espressioni aritmetiche, funzioni scientifiche in radianti e cronologia. Valutazione AST senza eval.': 'Arithmetic expressions, scientific functions in radians and history. AST evaluation without eval.', 'Orario settimanale': 'Weekly timetable', 'Lezioni, giorni, orari, aula e docente. Verifica sovrapposizioni e salva un archivio JSON.': 'Lessons, days, times, room and teacher. Check overlaps and save a JSON archive.', 'Ricettario': 'Recipe manager', 'Ricette, ingredienti, preparazione, categorie e tempi. Ricerca e gestione di un archivio JSON.': 'Recipes, ingredients, preparation, categories and times. Search and manage a JSON archive.', 'Catalogo libri': 'Book catalog', 'Titoli, autori, stato di lettura, prestiti e valutazioni. Ricerca e gestione di un archivio JSON.': 'Titles, authors, reading status, loans and ratings. Search and manage a JSON archive.'})

EN_MESSAGES.update({'Rubrica contatti': 'Contact book', 'Nomi, telefoni, email, note e foto PNG/GIF. Salvataggio esplicito in un database SQLite dedicato.': 'Names, phone numbers, email, notes and PNG/GIF photos. Explicit saving to a dedicated SQLite database.', 'Gestionale spese': 'Expense manager', 'Entrate e uscite, date e categorie. Totali decimali separati per valuta e salvataggio JSON.': 'Income and expenses, dates and categories. Decimal totals by currency and JSON saving.', 'Inventario casa/magazzino': 'Home/stock inventory', 'Codici univoci, quantità, costi EUR e soglie scorte basse. Modifica stock e salva JSON.': 'Unique codes, quantities, EUR costs and low-stock thresholds. Adjust stock and save JSON.', 'Archivio CD/DVD/giochi': 'CD/DVD/game archive', 'Titoli, tipo, artista/piattaforma, anno e prestiti. Ricerca e salvataggio JSON.': 'Titles, type, artist/platform, year and loans. Search and JSON saving.'})

EN_MESSAGES.update({'Campo Minato': 'Minesweeper', 'Griglia 9×9, dieci mine, primo clic sicuro e bandierine con clic destro o Control-clic.': 'A 9×9 grid, ten mines, safe first click and right-click/Control-click flags.', 'Labirinto': 'Maze', 'Labirinto generato con percorso verso l’uscita. Movimento con frecce, WASD o pulsanti.': 'Generated maze with a path to the exit. Move with arrows, WASD or buttons.', 'Agenda e calendario': 'Agenda and calendar', 'Calendario mensile navigabile e appuntamenti con date/orari. Ricerca e salvataggio JSON.': 'Navigable month calendar and dated/timed appointments. Search and JSON saving.', 'Slideshow PNG/GIF': 'PNG/GIF slideshow', 'Cartella immagini PNG/GIF, precedente/successiva e riproduzione automatica. Nessun PIP aggiuntivo.': 'PNG/GIF folder, previous/next and automatic playback. No extra PIP packages.'})
