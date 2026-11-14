# Global search / Ricerca globale — 1.34

## English

Open **Edit → Global search…**, **Ctrl+Shift+F** (Windows/Linux) or **Cmd+Shift+F** (macOS). The same command is available in the command palette and file editor windows. Type literal text and press Enter or **Search project**. Optional **Match case** and **Whole word** filters use Python's Unicode regular-expression case/word rules; search text is escaped, never treated as a regular expression or executable code.

The results show source/component, line number and a bounded line preview. An event label includes its form, object and event; file labels use project-relative paths. **Double-click or Enter** opens the matching source and selects the text. Navigation reuses an existing file editor so its unsaved changes are preserved. Tcl character units are used for editor indices, including non-BMP characters. A source changed since the scan must be searched again; results cannot navigate into a different project or project folder.

### Scope and unsaved changes

- All stored form/control event bodies, project startup code and imports/global code.
- The currently active event/global editor buffer overrides stored model text, including a newly edited event not yet in the model. Searching does not commit it, save the project or execute user code.
- Recursive `.py` files under the **saved project's folder**, whether or not included in deployment. Open IDE file buffers override disk text and are searched even when the backing file has been removed. Unsaved changes in external applications are not accessible.
- An unsaved project can search its events/global code; save the project to establish a folder for Python files. Hidden entries, `.git`, `.venv`, `venv`, `__pycache__`, `build`, `dist`, `.visualtk-trash` and symbolic links are excluded. Binary/non-UTF-8, inaccessible or oversized files are skipped with a status note.

Search snapshots Tk buffers on the UI thread, then scans/matches on a background thread. A new search cancels the previous request; **Stop** cancels it, and closing the window signals cancellation. Requests and project identity are checked before displaying results. Results are snapshots, not a live list; rerun after edits. Navigation can commit an event buffer to the in-memory model using the normal editor workflow, but does not save files to disk.

Limits: **1,000 results**, **200 candidate Python files**, **2 MiB per source**, **20 MiB total searched text**, **1,000 query characters**. Status notes identify truncation/skipped sources. Filtering applies to literal text, including syntactically incomplete code. Source order is imports, startup, form/control events, open file buffers, then remaining disk paths. No replace functionality is included in this release.

Validation: 14 regressions for search scope, unsaved buffers, removed backing files, Unicode positions, literal/case/word matching, symlink/path confinement, cancellation/result bounds, non-execution, source fingerprints, actual snapshot/navigation handlers and changed-project/content rejection. Tcl index handling is tested without graphical windows. Interactive graphical acceptance remains pending.

## Italiano

Apri **Modifica → Ricerca globale…** oppure premi **Ctrl/Cmd+Maiusc+F**, anche dagli editor dei file. Il comando è disponibile nella palette. Inserisci testo e premi Invio o **Cerca nel progetto**; puoi distinguere maiuscole/minuscole o cercare una parola intera. La ricerca è letterale: non esegue codice o espressioni regolari fornite dall’utente.

Ogni risultato indica componente/file, numero di riga e anteprima. **Doppio clic o Invio** apre la sorgente e seleziona il testo corrispondente. Gli eventi riportano form, componente e nome evento; i file hanno percorsi relativi al progetto. Se il codice è cambiato o hai aperto un altro progetto, occorre ripetere la ricerca per non usare posizioni obsolete.

Sono inclusi tutti gli eventi, il codice di avvio, import/funzioni globali e i file `.py` nella cartella del progetto salvato. Il buffer corrente e gli editor di file aperti hanno precedenza sui dati salvati, anche se il codice è incompleto. Le modifiche non salvate in applicazioni esterne non sono leggibili. Un progetto ancora senza percorso cerca nel proprio codice; per includere i file Python deve essere salvato. Non è necessario che i file siano inclusi nel deploy.

La ricerca usa un thread in background, può essere interrotta e non salva file. La navigazione può confermare il buffer di un evento nel modello in memoria attraverso il normale cambio di editor. Directory nascoste, ambienti virtuali, build/dist e collegamenti simbolici sono esclusi. File non UTF-8, binari, non leggibili o troppo grandi sono segnalati come esclusi.

Limiti espliciti: 1.000 risultati, 200 file Python candidati, 2 MiB per sorgente, 20 MiB totali e query fino a 1.000 caratteri. La barra di stato segnala esclusioni e limiti. I risultati sono una fotografia da aggiornare dopo le modifiche. Non è inclusa la sostituzione del testo. L’accettazione grafica resta da completare.
