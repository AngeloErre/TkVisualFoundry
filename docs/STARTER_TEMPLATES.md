# Starter templates / Modelli iniziali — 1.37

## English

Choose **File → New project** or the toolbar **New** button. Select **Blank project** or a starter in the new chooser, read its description and dependencies, then press **Create project**. Cancel closes the chooser without replacing the current project. If the current project has unsaved edits, the normal save/discard/cancel guard runs before replacement. Each starter is a fresh copy with no project path and is marked unsaved: choose Save as to store your own project. Built-in JSON files are never overwritten by creating or editing a copy.

The twelve starters below are the first three batches from the proposed 32-project collection. Their application labels and code comments are in English; the chooser is Italian/English. Every visible control is in the project model and can be edited in the designer. Open its events, startup code and global/import code to inspect or modify behavior. No project code is executed while browsing templates.

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

All twelve use Python/Tkinter's standard library and require no additional PIP packages. Run with F5 using the selected compatible Python. They can be exported/deployed using the existing project workflow; native builds still require their target platform/toolchain. The original files are in `examples/StarterTemplates/`, included in both source installers and the Mac standalone build's example resources.

### Second-batch details

Memory uses letters rather than image assets. It blocks extra card clicks while a mismatched pair is visible, cancels the timer on reset and ignores callbacks from previous games. Sliding 15 generates a solvable arrangement through legal moves, not a uniformly random permutation. Odd One Out completes a round on each answer and guards its finished state.

Mini-Paint draws vector objects on Canvas; the eraser paints white rather than deleting underlying shapes. It exports EPS through Tk, not PNG/JPEG, and asks before clearing. It has no undo stack or automatic drawing persistence. Its motion/release bindings live in startup code because the designer's standard click event is used to begin the stroke. GUI drawing and actual platform EPS acceptance remain pending.

### Scope

The dice starter provides immediate rolls, not animated dice or a complete RPG rules engine. The text converter creates Markdown **bullet lists**, not a full Markdown parser. Counts update after keyboard edits and on focus changes. The sticky-note starter is one note window, uses explicit file saves and asks before closing without saving; it does not autosave or maintain a desktop-wide multi-note database. The quiz uses a short editable demonstration bank, not a complete assessment system.

Thirty-eight automated regressions cover compilation/no extra requirements, independent copies, comment presence and no execution on load; quiz scoring/restart, dice validation/totals, Unicode conversions, real temporary note open/save/cancel and new-project state handling. All 27 example project files validate/compile. Interactive graphical acceptance remains pending.

### Next batches

The other requested projects are not yet shown in the chooser. The remaining twenty requested starters include archives, calendars, scientific tools, multimedia apps and arcade games. Arcade games, neural-network driving, databases/media archives and cloud/LLM study agents require separate logic, assets or dependency setup and will be added as complete, documented projects rather than empty placeholders.

## Italiano

Da **File → Nuovo progetto** o dal pulsante **Nuovo** scegli un progetto vuoto oppure uno dei dodici modelli. Il selettore mostra descrizione e dipendenze. **Crea progetto** apre una copia indipendente ancora da salvare; Annulla lascia il progetto corrente. La normale richiesta di salvare/scartare/annullare protegge le modifiche già presenti. Modificando la copia non si cambia il modello integrato.

Primo gruppo: **Quiz**, **Simulatore di dadi**, **Convertitore di testi** e **Post-it digitali**. Con il secondo gruppo sono i primi otto della raccolta proposta di 32 progetti. I commenti del codice e i testi delle applicazioni dimostrative sono in inglese; il selettore segue la lingua dell’IDE. Tutti i controlli si modificano nel designer e la logica si trova negli eventi, nel codice di avvio e negli import/funzioni globali.

Non occorrono pacchetti PIP aggiuntivi. Avvia con F5 e salva la tua copia prima di usare il normale flusso di deploy. Per il quiz modifica la lista delle domande nel codice di avvio. I dadi permettono D6/D20/D100, quantità e bonus; non includono animazioni. Il convertitore offre maiuscolo/minuscolo, camelCase e liste Markdown, con conteggi. Il post-it è una nota singola con colori e salvataggio manuale di file: non salva automaticamente e chiede conferma prima di chiudere senza salvare.

Trentotto test automatici dedicati ai modelli e compilazione/validazione di tutti i 27 esempi. Resta il collaudo grafico. Gli altri 20 modelli non sono ancora nel selettore: saranno sviluppati nei gruppi successivi, senza voci vuote o funzionalità simulate.

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
