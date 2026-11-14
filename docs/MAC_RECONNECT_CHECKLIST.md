# Mac reconnection acceptance / Verifiche alla riconnessione

Status: **pending**. The user is travelling with the Mac disconnected. Resume these checks when the user explicitly says **ambiente collegato**. Versions 1.37–1.39 were implemented and automatically tested on remote Linux; it has not been installed or run natively on the user's Mac.

1. Confirm the connected environment and current repository/version; preserve any user changes before updating. Use a temporary test project and disposable files.
2. Run the complete Italian/English suite with a supported stable Python. Record actual counts and which graphical tests now execute; do not carry forward Linux counts as Mac results.
3. Open the IDE: single native menu, visible Project Explorer, readable properties/log, new-project chooser with 20 starters plus blank. Check create/cancel/save/discard workflow.
4. Run all twenty starters through F5 in disposable projects. Inspect event/import/startup code and designer controls. Verify stop/relaunch and absence of stale callbacks/processes.
5. Alarm/timers: stopwatch pause/resume/reset; short countdown finish/stop; invalid input; HH:MM next-occurrence logic; one alert; native system bell; closing while a Tk timer is active. Do not alter OS sound/security settings to make a test pass.
6. Notepad: create/switch/close tabs, type/paste Unicode, open/save real temporary UTF-8/BOM files, dirty markers, cancel save dialogs, save/discard/cancel on tab/app closure, failed-write preservation and 20-tab limit.
7. Habits: add/duplicate/remove names, toggle today twice, streak display, temporary JSON round trip, malformed/oversized input, cancellation and close confirmation.
8. Pixel Art: click/drag corners and outside borders, palette/custom color/white erase, clear/cancel, temporary PPM and SVG export and native image display; close confirmation. Mini-Paint also needs native EPS export/display acceptance.
9. Recheck generated Python syntax colors, breakpoint/selected-line visibility, event editing and IntelliSense typing without input stalls. Exercise global search over unsaved event and file buffers and navigate results after edits/project switches.
10. Debugger: actual event/startup breakpoints, step/continue/stop, locals/Watch/stack selection, rapid process termination and re-execution. Verify focus and stale-session guards graphically.
11. Test installer/build/uninstaller only with safe temporary fixtures first. Native `.app`/DMG, icons and macOS launch behavior require their own evidence. Do not uninstall the user's existing application or change unrelated files as a test.
12. Record each passed/failed/pending case and reproducible defects; fix and rerun relevant tests before producing the next validated package. Hardware, live cloud/LLM, printer output and Windows acceptance remain separate target-specific work.

## Italiano

Le prove native sono sospese fino al messaggio **ambiente collegato**. Alla riconnessione verificare versione e modifiche locali, eseguire i test completi in italiano/inglese e collaudare graficamente IDE e venti modelli. Priorità: salvataggi e annullamenti del blocco note, campanella e timer, JSON abitudini, disegno/esportazione pixel, editor/ricerca e debugger. Usare solo progetti e file temporanei; conservare l’installazione e i dati dell’utente. Aggiornare questa checklist con esiti osservati, senza indicare come superati controlli ancora non eseguiti.

Fourth batch: verify calculator numeric/function buttons and history; table/recipe/book selection, field edits plus Add/Update, search, delete/replace confirmations, invalid/overlapping lessons and real temporary JSON save/open. Do not assume field drafts are committed until Add/Update.

Fifth batch: test a dedicated temporary Contact Book SQLite file, existing/unrelated database refusal, photo PNG/GIF chooser/display/missing paths, Add/Update/save/reopen; exact separate currency balances; inventory +/-1/low-stock states; media loans. Use only disposable SQLite/JSON and photo fixtures, never the user’s real contact or finance data.
