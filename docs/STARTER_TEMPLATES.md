# Starter templates / Modelli iniziali — 1.39

## English

Choose **File → New project** or the toolbar **New** button. Select **Blank project** or a starter in the new chooser, read its description and dependencies, then press **Create project**. Cancel closes the chooser without replacing the current project. If the current project has unsaved edits, the normal save/discard/cancel guard runs before replacement. Each starter is a fresh copy with no project path and is marked unsaved: choose Save as to store your own project. Built-in JSON files are never overwritten by creating or editing a copy.

The twenty starters below are the first five batches from the proposed 32-project collection. Their application labels and code comments are in English; the chooser is Italian/English. Every visible control is in the project model and can be edited in the designer. Open its events, startup code and global/import code to inspect or modify behavior. No project code is executed while browsing templates.

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

All twenty use Python/Tkinter's standard library and require no additional PIP packages. Run with F5 using the selected compatible Python. They can be exported/deployed using the existing project workflow; native builds still require their target platform/toolchain. The original files are in `examples/StarterTemplates/`, included in both source installers and the Mac standalone build's example resources.

### Second-batch details

Memory uses letters rather than image assets. It blocks extra card clicks while a mismatched pair is visible, cancels the timer on reset and ignores callbacks from previous games. Sliding 15 generates a solvable arrangement through legal moves, not a uniformly random permutation. Odd One Out completes a round on each answer and guards its finished state.

Mini-Paint draws vector objects on Canvas; the eraser paints white rather than deleting underlying shapes. It exports EPS through Tk, not PNG/JPEG, and asks before clearing. It has no undo stack or automatic drawing persistence. Its motion/release bindings live in startup code because the designer's standard click event is used to begin the stroke. GUI drawing and actual platform EPS acceptance remain pending.

### Scope

The dice starter provides immediate rolls, not animated dice or a complete RPG rules engine. The text converter creates Markdown **bullet lists**, not a full Markdown parser. Counts update after keyboard edits and on focus changes. The sticky-note starter is one note window, uses explicit file saves and asks before closing without saving; it does not autosave or maintain a desktop-wide multi-note database. The quiz uses a short editable demonstration bank, not a complete assessment system.

Sixty-five automated regressions cover compilation/no extra requirements, independent copies, comment presence and no execution on load; quiz scoring/restart, dice validation/totals, Unicode conversions, real temporary note open/save/cancel and new-project state handling. All 35 example project files validate/compile. Interactive graphical acceptance remains pending.

### Next batches

The other requested projects are not yet shown in the chooser. The remaining twelve requested starters include archives, calendars, scientific tools, multimedia apps and arcade games. Arcade games, neural-network driving, databases/media archives and cloud/LLM study agents require separate logic, assets or dependency setup and will be added as complete, documented projects rather than empty placeholders.

## Italiano

Da **File → Nuovo progetto** o dal pulsante **Nuovo** scegli un progetto vuoto oppure uno dei venti modelli. Il selettore mostra descrizione e dipendenze. **Crea progetto** apre una copia indipendente ancora da salvare; Annulla lascia il progetto corrente. La normale richiesta di salvare/scartare/annullare protegge le modifiche già presenti. Modificando la copia non si cambia il modello integrato.

Primo gruppo: **Quiz**, **Simulatore di dadi**, **Convertitore di testi** e **Post-it digitali**. Con il secondo gruppo sono i primi otto della raccolta proposta di 32 progetti. I commenti del codice e i testi delle applicazioni dimostrative sono in inglese; il selettore segue la lingua dell’IDE. Tutti i controlli si modificano nel designer e la logica si trova negli eventi, nel codice di avvio e negli import/funzioni globali.

Non occorrono pacchetti PIP aggiuntivi. Avvia con F5 e salva la tua copia prima di usare il normale flusso di deploy. Per il quiz modifica la lista delle domande nel codice di avvio. I dadi permettono D6/D20/D100, quantità e bonus; non includono animazioni. Il convertitore offre maiuscolo/minuscolo, camelCase e liste Markdown, con conteggi. Il post-it è una nota singola con colori e salvataggio manuale di file: non salva automaticamente e chiede conferma prima di chiudere senza salvare.

Sessantacinque test automatici dedicati ai modelli e compilazione/validazione di tutti i 35 esempi. Resta il collaudo grafico. Gli altri 12 modelli non sono ancora nel selettore: saranno sviluppati nei gruppi successivi, senza voci vuote o funzionalità simulate.

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
