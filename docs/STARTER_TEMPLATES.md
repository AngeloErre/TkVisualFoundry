# Starter templates / Modelli iniziali — 1.41

## English

Choose **File → New project** or the toolbar **New** button. Select **Blank project** or a starter in the new chooser, read its description and dependencies, then press **Create project**. Cancel closes the chooser without replacing the current project. If the current project has unsaved edits, the normal save/discard/cancel guard runs before replacement. Each starter is a fresh copy with no project path and is marked unsaved: choose Save as to store your own project. Built-in JSON files are never overwritten by creating or editing a copy.

The collection now includes all 32 requested starters. Their application labels and code comments are in English; the chooser is Italian/English. Application controls are editable in the designer; game sprites, grid cells and dynamic content are drawn or created by their commented helpers. Open its events, startup code and global/import code to inspect or modify behavior. No project code is executed while browsing templates.

| Starter | Included behavior | Where to customize |
| --- | --- | --- |
| Quiz | Five questions, four answers, score, finished-state guard and restart | Question bank in startup; helpers in imports; answer button events |
| Dice Roller | D6/D20/D100, 1–100 dice, signed bonus, input validation, last-roll breakdown and total | Dice options/entries in designer; `roll_dice` in imports |
| Text Converter | Upper/lower case, simple Unicode-word camelCase, Markdown bullet lists, word/character counts | `convert_text_value`, input events and conversion buttons |
| Sticky Note | Three colors, manual UTF-8 file open/save, replace and close confirmation | Note Text control, color/open/save button events and helpers |
| Odd One Out | Five rounds, nine tokens, score and restart | Token pairs in `odd_render`, card events |
| Memory Pairs | Eight letter pairs, moves, mismatch delay and restart | `memory_reset`, `memory_choose`, card events |
| Sliding 15 | 4×4 numbered tiles, move count, win detection, solvable shuffle | `puzzle_new_board`, `puzzle_choose`, tile events |
| Mini-Paint | Brush, white eraser, line/rectangle/oval, colors, width, clear, EPS export | Canvas click event and startup motion/release bindings |
| Alarm and Timers | Stopwatch pause/reset, countdown up to 24 hours, local HH:MM alarm, system bell | `clock_refresh`, `clock_tick` and button events |
| Tabbed Notepad | Up to 20 UTF-8 notes, new/open/save/close, dirty markers and close guards | Designer first page; dynamic `tabs_add` pages |
| Habit Tracker | Add/remove habits, daily toggle, current streak and total, validated JSON open/save | `habit_streak`, history schema and buttons |
| Pixel Art | 16×16 RGB cells, brush/white eraser, palette/custom color, PPM and SVG export | Canvas click/motion, `pixel_ppm`, `pixel_svg` |
| Scientific Calculator | Arithmetic/functions in radians, allowlisted AST, bounded 100-item history | `calc_expression`, button tokens and history events |
| Weekly Timetable | Recurring week, days/times/room/teacher, overlap validation, JSON | Field schema, timetable validators and archive helpers |
| Recipe Manager | Ingredients/steps/categories/preparation time, search/CRUD, JSON | Field schema, recipe validator and archive helpers |
| Book Catalog | Authors/status/borrower/rating, search/CRUD, JSON | Field schema, choices and archive helpers |
| Contact Book | Names/phone/email/notes, referenced PNG/GIF preview, dedicated SQLite | Schema validation, `contacts_preview`, SQLite adapters |
| Expense Manager | Income/expenses, ISO dates/categories, Decimal balances per currency, JSON | `expense_amount`, `expense_totals`, archive helpers |
| Home/Stock Inventory | Unique codes, whole quantities, EUR cost, low-stock thresholds, +/-1, JSON | `inventory_adjust`, `inventory_summary` |
| CD/DVD/Game Archive | Type, artist/platform, year, ownership/borrower, JSON | Media schema and loan/year validator |
| Minesweeper | 9×9 cells, 10 mines, safe first click, flags, flood fill, win/loss/restart | `mines_place`, `mines_reveal`, designer cell events |
| Maze Explorer | Connected 21×21 maze, arrows/WASD/buttons, move count, exit | `maze_generate`, `maze_move`, Canvas bindings |
| Agenda and Calendar | Monday-first month navigation, dates/times/events, search/CRUD, JSON | Calendar helpers, field schema and archive functions |
| PNG/GIF Slideshow | Folder scan, previous/next, play/pause, interval, bounded preview | `slide_show`, callback generation and scan limits |

All twenty-four use Python/Tkinter's standard library and require no additional PIP packages. Run with F5 using the selected compatible Python. They can be exported/deployed using the existing project workflow; native builds still require their target platform/toolchain. The original files are in `examples/StarterTemplates/`, included in both source installers and the Mac standalone build's example resources.

### Second-batch details

Memory uses letters rather than image assets. It blocks extra card clicks while a mismatched pair is visible, cancels the timer on reset and ignores callbacks from previous games. Sliding 15 generates a solvable arrangement through legal moves, not a uniformly random permutation. Odd One Out completes a round on each answer and guards its finished state.

Mini-Paint draws vector objects on Canvas; the eraser paints white rather than deleting underlying shapes. It exports EPS through Tk, not PNG/JPEG, and asks before clearing. It has no undo stack or automatic drawing persistence. Its motion/release bindings live in startup code because the designer's standard click event is used to begin the stroke. GUI drawing and actual platform EPS acceptance remain pending.

### Scope

The dice starter provides immediate rolls, not animated dice or a complete RPG rules engine. The text converter creates Markdown **bullet lists**, not a full Markdown parser. Counts update after keyboard edits and on focus changes. The sticky-note starter is one note window, uses explicit file saves and asks before closing without saving; it does not autosave or maintain a desktop-wide multi-note database. The quiz uses a short editable demonstration bank, not a complete assessment system.

Eighty automated regressions cover compilation/no extra requirements, independent copies, comment presence and no execution on load; quiz scoring/restart, dice validation/totals, Unicode conversions, real temporary note open/save/cancel and new-project state handling. All 39 example project files validate/compile. Interactive graphical acceptance remains pending.

### Next batches

The other requested projects are not yet shown in the chooser. The remaining eight requested starters are neural-network driving, Space Invaders, Pacman, Super Mario, Tetris, an LLM study agent, QR/barcode tools and a multimedia soundboard. Arcade games, neural-network driving, databases/media archives and cloud/LLM study agents require separate logic, assets or dependency setup and will be added as complete, documented projects rather than empty placeholders.

## Italiano

Da **File → Nuovo progetto** o dal pulsante **Nuovo** scegli un progetto vuoto oppure uno dei ventiquattro modelli. Il selettore mostra descrizione e dipendenze. **Crea progetto** apre una copia indipendente ancora da salvare; Annulla lascia il progetto corrente. La normale richiesta di salvare/scartare/annullare protegge le modifiche già presenti. Modificando la copia non si cambia il modello integrato.

Primo gruppo: **Quiz**, **Simulatore di dadi**, **Convertitore di testi** e **Post-it digitali**. Con il secondo gruppo sono i primi otto della raccolta proposta di 32 progetti. I commenti del codice e i testi delle applicazioni dimostrative sono in inglese; il selettore segue la lingua dell’IDE. Tutti i controlli si modificano nel designer e la logica si trova negli eventi, nel codice di avvio e negli import/funzioni globali.

Non occorrono pacchetti PIP aggiuntivi. Avvia con F5 e salva la tua copia prima di usare il normale flusso di deploy. Per il quiz modifica la lista delle domande nel codice di avvio. I dadi permettono D6/D20/D100, quantità e bonus; non includono animazioni. Il convertitore offre maiuscolo/minuscolo, camelCase e liste Markdown, con conteggi. Il post-it è una nota singola con colori e salvataggio manuale di file: non salva automaticamente e chiede conferma prima di chiudere senza salvare.

Ottanta test automatici dedicati ai modelli e compilazione/validazione di tutti i 39 esempi. Resta il collaudo grafico. Gli altri 8 modelli non sono ancora nel selettore: saranno sviluppati nei gruppi successivi, senza voci vuote o funzionalità simulate.

### Secondo gruppo (1.36)

Aggiunti **Trova l’intruso**, **Memory**, **Gioco del 15** e **Mini-Paint**: ora otto modelli più il progetto vuoto. Tutti hanno commenti in inglese e non richiedono PIP aggiuntivi. Memory usa coppie di lettere e protegge il riavvio dai vecchi timer. Il Gioco del 15 resta risolvibile perché viene mescolato tramite mosse legali. Mini-Paint offre pennello, gomma bianca, linee, rettangoli, ovali, colori e spessore: esporta EPS, non PNG/JPEG, e chiede prima di cancellare. Non include undo o salvataggio automatico. Gli undici nuovi test coprono la logica; il collaudo grafico e l’output EPS nativo restano da completare.

## Third batch — remote development (1.37)

The Mac was disconnected during development. Logic/file tests run on remote Linux; native Mac GUI checks remain deferred until the user reports **ambiente collegato**, using [the reconnection checklist](MAC_RECONNECT_CHECKLIST.md).

- Alarm and Timers is a session-only app. It does not wake a sleeping/off computer or notify after closure. Alerts use Tk's system bell; audibility depends on native sound settings. HH:MM alarms use the local date/time. Stopwatch/countdown elapsed time uses monotonic time.
- Tabbed Notepad handles up to 20 notes and opens UTF-8/BOM files up to 2 MiB. The first Notebook page/Text control is designer-editable; additional pages are created by English-commented startup/helpers. Saves use atomic replacement. Closing a modified tab/window offers save/discard/cancel. No autosave, external-change detection or full Notepad++ feature set is claimed.
- Habit Tracker stores only user-entered names and ISO dates, up to 200 habits and 3,660 dates per habit. Today can be toggled. The current streak includes yesterday when today is still incomplete. Save/open is manual JSON; replacement and closure are confirmed. No background tracking or health advice is provided.
- Pixel Art has a fixed 16×16 canvas. White acts as the eraser; there is no transparency, image import, undo or autosave. Export PPM for a 16×16 raster image or SVG for scalable crisp rectangles. PNG/JPEG is not included. Clear/close are confirmed.

Seventeen third-batch regressions cover timing, malformed inputs, midnight rollover, atomic save failures, unsaved cancellation, tab lifecycle, habit streaks and valid PPM/SVG payloads. These are automated logic/file tests, not native clicking/typing or audible alarm acceptance.

### Terzo gruppo — Mac scollegato

Aggiunti **Sveglia e timer**, **Blocco note a schede**, **Tracker di abitudini** ed **Editor Pixel Art**: ora 12 modelli più il progetto vuoto. Codice commentato in inglese e nessun PIP aggiuntivo. Il timer richiede l’app aperta e non riattiva il computer; la campanella va verificata sul Mac. Il blocco note protegge le modifiche, gestisce fino a 20 schede e salva esplicitamente in UTF-8. Il tracker salva manualmente una cronologia JSON. Pixel Art esporta PPM/SVG, non PNG, e non salva automaticamente. I test automatici sono eseguiti da remoto; collaudo nativo e debugging saranno ripresi al messaggio **ambiente collegato**.

## Fourth batch (1.38)

All four starters run without extra PIP packages. The calculator supports +, -, *, /, //, %, **; sin/cos/tan/inverse functions, sqrt, log/log10, exp, abs, factorial and pi/e/tau. Trigonometry uses radians. Expressions are limited to 256 characters/100 AST nodes, numeric literals to 1e12, exponents to -12…12, factorial to whole values 0…50 and finite real intermediate results to 1e100. Attributes, imports, strings, containers, arbitrary names and keyword arguments are rejected. Floating-point arithmetic is used; this is not symbolic algebra or arbitrary precision.

The three archives keep up to 500 records in memory. Use **New → edit fields → Add**, or select a record, edit and press **Update**. Then **Save JSON** writes the collection. Unapplied field drafts are not part of the saved collection. Search covers all fields and keeps stable record IDs; a hidden selection cannot be updated accidentally. Delete, collection replacement and app closure require confirmation. There is no autosave or merge of external edits.

JSON files carry version and archive-kind markers, so opening a recipe file in the book catalog is rejected. Reads and writes are capped at 2 MiB; field lengths and unique IDs are validated. Saves use temporary files and atomic replacement to preserve previous files on write failure. These templates use local JSON archives, **not SQLite or a remote database**.

Timetables represent a recurring week in a sorted list, not a visual calendar grid. Times must be HH:MM on the same day; adjacent lessons are valid, overlaps on the same day are rejected. Recipes allow preparation times from 0 to 1440 whole minutes and require ingredients/steps. Books track one optional borrower string, reading status and a 0–5 numeric rating (0 means unrated); no ISBN lookup, cover-image service or automatic lending reminders are included.

Thirteen fourth-batch regressions cover the calculator allowlist/limits/history, archive data/CRUD/filter selection, invalid records, timetable overlaps/ordering, recipe constraints, real temporary JSON round trips, atomic failure preservation, file-kind and size rejection and cancellation. Native Mac graphical acceptance remains pending.

### Quarto gruppo (1.38)

Aggiunti **Calcolatrice scientifica**, **Orario settimanale**, **Ricettario** e **Catalogo libri**: sedici modelli più il progetto vuoto. Commenti in inglese, nessun PIP aggiuntivo. La calcolatrice valuta solo espressioni matematiche limitate e usa radianti. I tre archivi permettono ricerca, aggiunta, modifica ed eliminazione: premi **Add/Update prima di Save JSON**, perché i campi non applicati non vengono salvati. Dati in JSON locale, non SQLite; massimo 500 record e file da 2 MiB. L’orario è una lista settimanale ordinata e rifiuta sovrapposizioni; il ricettario include ingredienti/passaggi/tempi; il catalogo gestisce stato di lettura, prestito e voto. Sono inclusi salvataggi atomici e conferme, non autosave o servizi esterni. Le verifiche native attendono il messaggio **ambiente collegato**.

## Fifth batch (1.39)

Twenty standard-library starters are now available. These four have English-commented code and designer-editable controls. As with the preceding archives, press **Add/Update** to apply field drafts before saving. Creating a starter never creates a user database or calls a service.

- **Contact Book:** manual open/save of a dedicated SQLite database with schema/version markers, names, phone, basic optional email validation, notes and a photo path. Save replaces the stored contact collection in one transaction; it is not an incremental merge or a generic editor for arbitrary contact databases. Unrelated schemas, extra views/triggers and invalid rows are rejected before replacement; read opens use read-only/query-only mode. Up to 500 validated records. A failed first save can leave a newly created empty file; existing records are protected by rollback. No passwords, remote servers, email sending or phone calls are included.
- Photo previews use Tk PhotoImage and are limited to PNG/GIF, 2 MiB, dimensions up to 4096 per side and at most 8 million pixels. Files are **referenced**, not embedded or copied: keep their paths accessible when reopening or deploying. JPEG/WebP and contact photo import into the project are not included. Header/loader contracts are tested; actual native rendering remains pending.
- **Expense Manager:** manual income/expense records with ISO dates/categories and positive amounts up to 999999999.99, accepting comma or dot decimal input. Decimal balances are calculated independently for EUR/USD/GBP over the **entire collection**, not just filtered rows. There is no exchange conversion, bank connection, tax reporting, budgets or recurring transaction engine.
- **Inventory:** unique item codes ignoring case, quantities and thresholds from 0 to 1000000, nonnegative EUR unit costs, location and +/-1 stock buttons. `[LOW]` means quantity is at or below its threshold. Totals cover all records. Stock changes are in memory until Save JSON; no movement audit ledger, fractional units, barcode scanning or costing method is included.
- **CD/DVD/Game Archive:** titles, media type, artist/platform, optional four-digit year, ownership/wishlist/loan state and one borrower string. Loaned items require a borrower. No cover downloads, media playback, lending reminders or external metadata lookup are included.

The last three use versioned JSON archives, capped at 500 records / 2 MiB, with atomic saves and confirmation dialogs. Contacts use SQLite instead. Fourteen new regressions exercise exact currency totals, stock bounds/low thresholds, media validation, real JSON/SQLite persistence, unrelated database rejection, parameterized values, transaction rollback after an insert failure, cancellation and bounded mocked photo loading. Mac graphical/photo acceptance remains pending until **ambiente collegato**.

### Quinto gruppo (1.39)

Aggiunti **Rubrica contatti**, **Gestionale spese**, **Inventario casa/magazzino** e **Archivio CD/DVD/giochi**: venti modelli più il progetto vuoto. Tutti con commenti in inglese, senza PIP aggiuntivi. La rubrica salva esplicitamente in un database SQLite dedicato e può mostrare foto PNG/GIF referenziate sul disco; non modifica database con schemi estranei. Gli altri tre salvano JSON. Le spese usano importi decimali e totali separati per valuta; l’inventario segnala scorte basse e rifiuta stock negativi/codici duplicati; l’archivio multimediale controlla anno e nominativo del prestito. I totali riguardano l’intera raccolta, anche quando la lista è filtrata. **Add/Update applica i campi, Save conserva la raccolta**: niente autosave o servizi esterni. Le foto non sono incorporate; JPEG/WebP non sono previsti. Collaudo nativo Mac ancora sospeso.

## Sixth batch (1.40)

- **Minesweeper:** fixed 9×9 board with ten mines. The first unflagged reveal and its neighbors are excluded from mine placement. Left click reveals; right click, middle click or Control-click toggles a flag, up to ten. Empty areas reveal iteratively. Opening all 71 safe cells wins; flags alone do not win. Restart clears all state. Native platform mouse/Control-click interaction remains to be checked.
- **Maze Explorer:** iterative depth-first carving connects 100 rooms on a 21×21 wall/passage grid. Move the blue player to the green exit with arrows, WASD or buttons. Click the Canvas to focus keyboard input. Walls, diagonal moves and moves after completion are blocked. New maze resets position and move count. No enemies, scoring timer or externally loaded maps are included.
- **Agenda and Calendar:** Monday-first monthly calendar with a stable 42-cell view. Previous/next navigate across years; a day click starts a new draft and fills its date/09:00–10:00 defaults while filtering the event list by date. Add/Update applies fields; Save JSON persists the collection. Generic Add/Update clears the list search to show all records. Event dates are ISO YYYY-MM-DD, with same-day HH:MM end after start; overlaps are allowed. Up to 500 records / 2 MiB; atomic versioned JSON saves and replacement/close confirmations. No recurring/multi-day events, reminders, notifications or calendar service sync.
- **PNG/GIF Slideshow:** nonrecursive local folder browsing, sorted selected files, previous/next and 1–10-second automatic playback. Manual stepping pauses playback. Pause/folder replacement/close cancel the owned callback and invalidate stale generations. Supported input is PNG or GIF **first frame only**, not JPEG/WebP or animated playback. Preview limits: 500 images from at most 5,000 directory entries, 2 MiB per file, at most 4096 per side and 8 million pixels. Symlinks are excluded; bad/missing files show a message instead of a stale image. Thumbnails use integer subsampling, not animated transitions or arbitrary resampling. Files are not copied into the project or modified.

Fifteen new regressions verify 80 safe first-mine placements, flags/flood fill/win/loss, 25 connected maze generations with reachable exits and an actual logical path to completion, calendar leap/year transitions and JSON round trips, slideshow file scanning/bounds and mocked Tk image lifetime/timer lifecycle/cancel paths. All 39 examples validate/compile on remote Linux. Native Mac rendering and pointer/keyboard acceptance remain deferred until **ambiente collegato**.

### Sesto gruppo (1.40)

Aggiunti **Campo Minato**, **Labirinto**, **Agenda/Calendario** e **Slideshow PNG/GIF**: ventiquattro modelli più il progetto vuoto, tutti commentati in inglese e senza PIP aggiuntivi. Campo Minato protegge il primo clic e usa bandierine; il labirinto ha un’uscita raggiungibile e controlli da tastiera/pulsanti. L’agenda naviga i mesi e salva appuntamenti JSON applicati con Add/Update; non invia promemoria. Lo slideshow gestisce cartella, precedente/successiva e timer, ma supporta soltanto PNG/GIF statici entro i limiti indicati, non JPEG/WebP. File immagine non copiati né modificati. Restano otto modelli della lista iniziale. Le prove native sul Mac attendono **ambiente collegato**.

## Final batch / Ultimo gruppo — 1.41

| Starter | Behavior / Funzioni | Customization / Personalizzazione |
| --- | --- | --- |
| Micro Invaders | Formation movement, limited shots, score, win/loss / Formazione, spari, punteggio, vittoria/sconfitta | `game_step`, `invader_shoot`, Canvas colors |
| Dot Maze Chase | Connected original maze, dots, breadth-first pursuer / Labirinto originale, punti, inseguitore | `MAZE`, `chase_next`, movement cadence |
| Mini Platformer | Gravity, jumping, top landing and goal / Gravità, salto, atterraggio e traguardo | `PLATFORMS`, physics, goal position |
| Falling Blocks | Seven pieces, rotation, hard drop, line clearing / Sette pezzi, rotazione, caduta rapida, righe | `PIECES`, `blocks_valid`, `blocks_clear`, gravity |
| Neural Driving Lab | Actual 3-6-1 tanh network with supervised training / Rete tanh 3-6-1 con addestramento supervisionato | `neural_target`, `neural_train`, road function |
| Study Agent | Topic to explanation/example/three questions; async response / Argomento, spiegazione, esempio e tre domande; risposta asincrona | `study_send`, Tutor properties/model/token limit |
| QR and Barcode Studio | QR/Code128 PNG generation; local image decoding / Generazione QR/Code128 PNG e lettura da immagini locali | `code_generate`, `code_read`, input and image limits |
| Soundboard | Eight local-file pads, single-stream playback, volume/pause/stop / Otto pad locali, un suono alla volta, volume/pausa/stop | Pad Click events, `sound_assign`, AudioPlayer properties |

### Dependencies and first run / Dipendenze e primo avvio

The first 29 starters (including the five new games/simulations) need no additional PIP packages. The other three declare dependencies that the chooser displays and the existing project PIP workflow can install into the selected Python environment. The templates do not silently install packages. Build on each target operating system and verify package/wheel support there.

I primi 29 modelli (inclusi i cinque nuovi giochi/simulazioni) non richiedono PIP aggiuntivi. Gli altri tre dichiarano le dipendenze, visibili nel selettore e installabili con il flusso PIP del progetto nell’interprete scelto. I modelli non installano pacchetti silenziosamente. La disponibilità dei pacchetti e delle wheel va verificata su ogni sistema di destinazione.

- **Study Agent:** `openai>=2,<4` via LLMClient. Choose a model in the client and provide `OPENAI_API_KEY` or its session-only Key dialog. Model listing and sending are explicit network actions; API usage follows the user's account. No keys are stored in the template. Responses are study aids and are not externally verified. / Scegliere modello e chiave personale; nessuna chiamata all’avvio, credenziali non salvate nel progetto.
- **QR/barcode:** `qrcode>=8,<9`, `python-barcode>=0.16,<1`, `zxing-cpp>=2.3,<4`, `Pillow>=11,<14`. Generation and reading stay local. QR accepts up to 1000 characters; Code128 accepts printable ASCII. Reading is bounded to 20 MB / 20 million pixels. Decoding success depends on image quality. / Generazione e lettura locali, limiti di input e immagini; qualità dell’immagine determinante.
- **Soundboard:** `pygame-ce>=2.5.8` via AudioPlayer. Select a slot, Assign an existing WAV/MP3/OGG file, then click its pad. Assignments last for the session; audio files are not bundled. The built-in player offers volume/pause/resume/stop. / Assegnare file ai pad; associazioni di sessione, file audio non inclusi.

### Gameplay / Uso dei giochi

Use Start/Pause/Reset. Keyboard focus belongs to the Canvas; click it after using other controls. Invaders uses Left/Right/Space; maze chase uses arrows; platformer uses Left/Right/Space (side Stop button halts motion); blocks uses arrows, Up to rotate and Space to drop. All five have owned timers with generation guards, canceled on pause, reset or close. Neural Driving: press Train network, then Start; training can be repeated. This is a supervised synthetic teaching example with a handcrafted steering target, not reinforcement learning. Reset preserves learned weights. Artwork consists of original geometric shapes and maps.

Usare Start/Pause/Reset; cliccare il Canvas per restituire il focus alla tastiera. Nei blocchi, Su ruota e Spazio fa cadere il pezzo. La simulazione neurale si usa con Train network e poi Start: apprendimento supervisionato su una strada sintetica, pesi conservati dopo Reset. I cinque modelli annullano i timer su pausa, riavvio e chiusura. Grafica e mappe originali.

### Validation / Verifica

Nineteen new offline regressions cover collisions, victories/losses, connected maps, every piece's four-rotation cycle, line clearing, hard drop, stale callbacks, neural error reduction, explicit tutor sends, sound assignments and real PNG generation/decoding for QR and Code128. Service and audio calls are mocked; no paid API or physical audio test was performed. Native Mac GUI/keyboard/audio/PIP and generated-app deployment acceptance remains pending **ambiente collegato**.
