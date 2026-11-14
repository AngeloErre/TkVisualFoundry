# Starter templates / Modelli iniziali — 1.36

## English

Choose **File → New project** or the toolbar **New** button. Select **Blank project** or a starter in the new chooser, read its description and dependencies, then press **Create project**. Cancel closes the chooser without replacing the current project. If the current project has unsaved edits, the normal save/discard/cancel guard runs before replacement. Each starter is a fresh copy with no project path and is marked unsaved: choose Save as to store your own project. Built-in JSON files are never overwritten by creating or editing a copy.

The eight starters below are the first two batches from the proposed 32-project collection. Their application labels and code comments are in English; the chooser is Italian/English. Every visible control is in the project model and can be edited in the designer. Open its events, startup code and global/import code to inspect or modify behavior. No project code is executed while browsing templates.

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

All eight use Python/Tkinter's standard library and require no additional PIP packages. Run with F5 using the selected compatible Python. They can be exported/deployed using the existing project workflow; native builds still require their target platform/toolchain. The original files are in `examples/StarterTemplates/`, included in both source installers and the Mac standalone build's example resources.

### Second-batch details

Memory uses letters rather than image assets. It blocks extra card clicks while a mismatched pair is visible, cancels the timer on reset and ignores callbacks from previous games. Sliding 15 generates a solvable arrangement through legal moves, not a uniformly random permutation. Odd One Out completes a round on each answer and guards its finished state.

Mini-Paint draws vector objects on Canvas; the eraser paints white rather than deleting underlying shapes. It exports EPS through Tk, not PNG/JPEG, and asks before clearing. It has no undo stack or automatic drawing persistence. Its motion/release bindings live in startup code because the designer's standard click event is used to begin the stroke. GUI drawing and actual platform EPS acceptance remain pending.

### Scope

The dice starter provides immediate rolls, not animated dice or a complete RPG rules engine. The text converter creates Markdown **bullet lists**, not a full Markdown parser. Counts update after keyboard edits and on focus changes. The sticky-note starter is one note window, uses explicit file saves and asks before closing without saving; it does not autosave or maintain a desktop-wide multi-note database. The quiz uses a short editable demonstration bank, not a complete assessment system.

Twenty-one automated regressions cover compilation/no extra requirements, independent copies, comment presence and no execution on load; quiz scoring/restart, dice validation/totals, Unicode conversions, real temporary note open/save/cancel and new-project state handling. All 23 example project files validate/compile. Interactive graphical acceptance remains pending.

### Next batches

The other requested projects are not yet shown in the chooser. Fast candidates for the next batch are Stopwatch/Countdown, a tabbed notepad, a habit tracker and Pixel Art. Arcade games, neural-network driving, databases/media archives and cloud/LLM study agents require separate logic, assets or dependency setup and will be added as complete, documented projects rather than empty placeholders.

## Italiano

Da **File → Nuovo progetto** o dal pulsante **Nuovo** scegli un progetto vuoto oppure uno degli otto modelli. Il selettore mostra descrizione e dipendenze. **Crea progetto** apre una copia indipendente ancora da salvare; Annulla lascia il progetto corrente. La normale richiesta di salvare/scartare/annullare protegge le modifiche già presenti. Modificando la copia non si cambia il modello integrato.

Primo gruppo: **Quiz**, **Simulatore di dadi**, **Convertitore di testi** e **Post-it digitali**. Con il secondo gruppo sono i primi otto della raccolta proposta di 32 progetti. I commenti del codice e i testi delle applicazioni dimostrative sono in inglese; il selettore segue la lingua dell’IDE. Tutti i controlli si modificano nel designer e la logica si trova negli eventi, nel codice di avvio e negli import/funzioni globali.

Non occorrono pacchetti PIP aggiuntivi. Avvia con F5 e salva la tua copia prima di usare il normale flusso di deploy. Per il quiz modifica la lista delle domande nel codice di avvio. I dadi permettono D6/D20/D100, quantità e bonus; non includono animazioni. Il convertitore offre maiuscolo/minuscolo, camelCase e liste Markdown, con conteggi. Il post-it è una nota singola con colori e salvataggio manuale di file: non salva automaticamente e chiede conferma prima di chiudere senza salvare.

Ventuno test automatici dedicati ai modelli e compilazione/validazione di tutti i 23 esempi. Resta il collaudo grafico. Gli altri 24 modelli non sono ancora nel selettore: saranno sviluppati nei gruppi successivi, senza voci vuote o funzionalità simulate.

### Secondo gruppo (1.36)

Aggiunti **Trova l’intruso**, **Memory**, **Gioco del 15** e **Mini-Paint**: ora otto modelli più il progetto vuoto. Tutti hanno commenti in inglese e non richiedono PIP aggiuntivi. Memory usa coppie di lettere e protegge il riavvio dai vecchi timer. Il Gioco del 15 resta risolvibile perché viene mescolato tramite mosse legali. Mini-Paint offre pennello, gomma bianca, linee, rettangoli, ovali, colori e spessore: esporta EPS, non PNG/JPEG, e chiede prima di cancellare. Non include undo o salvataggio automatico. Gli undici nuovi test coprono la logica; il collaudo grafico e l’output EPS nativo restano da completare.
