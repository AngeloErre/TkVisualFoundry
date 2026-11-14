# Starter templates / Modelli iniziali — 1.35

## English

Choose **File → New project** or the toolbar **New** button. Select **Blank project** or a starter in the new chooser, read its description and dependencies, then press **Create project**. Cancel closes the chooser without replacing the current project. If the current project has unsaved edits, the normal save/discard/cancel guard runs before replacement. Each starter is a fresh copy with no project path and is marked unsaved: choose Save as to store your own project. Built-in JSON files are never overwritten by creating or editing a copy.

The four starters below are the first batch from the proposed 32-project collection. Their application labels and code comments are in English; the chooser is Italian/English. Every visible control is in the project model and can be edited in the designer. Open its events, startup code and global/import code to inspect or modify behavior. No project code is executed while browsing templates.

| Starter | Included behavior | Where to customize |
| --- | --- | --- |
| Quiz | Five questions, four answers, score, finished-state guard and restart | Question bank in startup; helpers in imports; answer button events |
| Dice Roller | D6/D20/D100, 1–100 dice, signed bonus, input validation, last-roll breakdown and total | Dice options/entries in designer; `roll_dice` in imports |
| Text Converter | Upper/lower case, simple Unicode-word camelCase, Markdown bullet lists, word/character counts | `convert_text_value`, input events and conversion buttons |
| Sticky Note | Three colors, manual UTF-8 file open/save, replace and close confirmation | Note Text control, color/open/save button events and helpers |

All four use Python/Tkinter's standard library and require no additional PIP packages. Run with F5 using the selected compatible Python. They can be exported/deployed using the existing project workflow; native builds still require their target platform/toolchain. The original files are in `examples/StarterTemplates/`, included in both source installers and the Mac standalone build's example resources.

### Scope

The dice starter provides immediate rolls, not animated dice or a complete RPG rules engine. The text converter creates Markdown **bullet lists**, not a full Markdown parser. Counts update after keyboard edits and on focus changes. The sticky-note starter is one note window, uses explicit file saves and asks before closing without saving; it does not autosave or maintain a desktop-wide multi-note database. The quiz uses a short editable demonstration bank, not a complete assessment system.

Ten automated regressions cover compilation/no extra requirements, independent copies, comment presence and no execution on load; quiz scoring/restart, dice validation/totals, Unicode conversions, real temporary note open/save/cancel and new-project state handling. All 19 example project files validate/compile. Interactive graphical acceptance remains pending.

### Next batches

The other requested projects are not yet shown in the chooser. Fast candidates for the next batch are Odd One Out, Memory, Sliding 15 Puzzle, Stopwatch/Countdown and Mini-Paint. Arcade games, neural-network driving, databases/media archives and cloud/LLM study agents require separate logic, assets or dependency setup and will be added as complete, documented projects rather than empty placeholders.

## Italiano

Da **File → Nuovo progetto** o dal pulsante **Nuovo** scegli un progetto vuoto oppure uno dei quattro modelli. Il selettore mostra descrizione e dipendenze. **Crea progetto** apre una copia indipendente ancora da salvare; Annulla lascia il progetto corrente. La normale richiesta di salvare/scartare/annullare protegge le modifiche già presenti. Modificando la copia non si cambia il modello integrato.

Primo gruppo: **Quiz**, **Simulatore di dadi**, **Convertitore di testi** e **Post-it digitali**. Sono i primi quattro della raccolta proposta di 32 progetti. I commenti del codice e i testi delle applicazioni dimostrative sono in inglese; il selettore segue la lingua dell’IDE. Tutti i controlli si modificano nel designer e la logica si trova negli eventi, nel codice di avvio e negli import/funzioni globali.

Non occorrono pacchetti PIP aggiuntivi. Avvia con F5 e salva la tua copia prima di usare il normale flusso di deploy. Per il quiz modifica la lista delle domande nel codice di avvio. I dadi permettono D6/D20/D100, quantità e bonus; non includono animazioni. Il convertitore offre maiuscolo/minuscolo, camelCase e liste Markdown, con conteggi. Il post-it è una nota singola con colori e salvataggio manuale di file: non salva automaticamente e chiede conferma prima di chiudere senza salvare.

Dieci nuovi test automatici e compilazione/validazione di tutti i 19 esempi. Resta il collaudo grafico. Gli altri 28 modelli non sono ancora nel selettore: saranno sviluppati nei gruppi successivi, senza voci vuote o funzionalità simulate.
