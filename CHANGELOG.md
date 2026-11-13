# 1.27

- Add persistent event/startup/import breakpoints with editor markers and Shift+F9.
- Resolve to executable generated-source lines across embedded runtime changes; report unresolved points.
- Remap edited source and preserve metadata through smart rename/save/load.
- Add real pdb event-stop and mapping regressions; update the inspector demo and bilingual docs.

# 1.26

- Add read-only Variables / Inspector for F5/F9 with globals, active/last locals, self fields and stack.
- Refresh sampled values about every 0.5 seconds; filter/expand trees and accent changes.
- Isolate temporary per-process snapshots, bound values and avoid user repr/property evaluation.
- Add live changing-value and real pdb breakpoint regressions; document sampling limits and performance.

# 1.25

- Show current pdb position and jump to a yellow line marker in immutable session source.
- Observe fragmented prompts, canonicalize macOS temporary paths and isolate old process output.
- Clear markers on resume/finish and preserve existing pdb console commands.
- Add real subprocess and session regression tests; GUI acceptance pending.

# 1.24

- Add adaptive anchors inside Notebook pages with theme-dependent client-area calibration.
- Handle pages first visited after resize, independent per-page bindings and safe queued teardown.
- Add a two-page demo, regression coverage and bilingual documentation.
- 218 tests passed per language; 11 graphical tests skipped. Interactive resizing remains pending.

# 1.23

- Add optional multi-control edge-anchor settings with minimum stretched dimensions and fixed-placement reset.
- Embed coalesced runtime placement helpers for forms and ordinary Tk/ttk frame/canvas parents; preserve existing event bindings.
- Support nested ordinary frames and preview/deploy export while retaining fixed-layout compatibility.
- Explicitly reject unsupported CustomTkinter/tab-page/scrollable internals and stale selection plans.

# 1.22

- Add minute-based project snapshots including pending event/startup/import editor text, without mutating the live model.
- Add local checkpoint/history browser, bounded JSON comparison and open-as-copy recovery with name collision protection.
- Keep 30 deduplicated versions per project identity, use atomic private writes and skip corrupt records. Preserve failed-write predecessors.
- Add startup history discovery/status count and configurable automatic snapshots; keep resources, virtual environments and external editor buffers outside this scope.

# 1.21

- Add reviewed smart rename for forms/controls from Edit and inspector Actions.
- Update static self attributes, generated event-method references, literal form show/hide and reflective self-name access, plus parent relationships.
- Preserve unrelated source formatting/text/comments and external files; warn on ambiguous/dynamic references.
- Apply one undoable model change after syntax/name/collision and stale-review validation.

# 1.20

- Add F6 real-form preview in an independent process with asynchronous interpreter validation and output.
- Build visual-only snapshots without project event/import/startup source, callbacks or Tcl focus scripts; keep the selected form/theme/tab page.
- Render approved UI libraries and substitute device/service/user-defined components with labeled placeholders.
- Prepare only preview requirements; handle refresh, close and spawn/close ownership separately from run/debug.

# 1.19.1

- Initialize the workspace splitters after Map/Configure geometry is available instead of relying on a single early idle callback.
- Give the right dock a wider initial area and clamp Project Explorer/Properties to usable dimensions after resizing. Preserve valid user splitter positions.

# 1.19

- Add canvas Shift-click/select-all, group movement, hierarchy-aware duplicate/delete and sibling alignment/equal-size/distribution commands.
- Add a navigable Problems panel with non-executing syntax/self-reference/import inventory diagnostics and stale-report protection.
- Add background project .venv creation/reuse, PIP preparation and interpreter restoration; preserve global preferences and exclude environments from deploy.
- Protect existing folders and failed environment creation, validate project environment metadata and avoid flagging IDE-only dependencies in isolated project audits.

# 1.18

- Add deployment application-icon selection, preview, removal and project-relative artwork import.
- Convert PNG/ICO/ICNS artwork into Mac ICNS, Windows ICO and runtime PNG; wire PyInstaller --icon and Inno Setup SetupIconFile.
- Apply the PNG as the default Tk window icon in the deployment source, preserve old kits without icon metadata and remap/remove icon references with project file operations.
- Add Pillow to IDE requirements and protect Save As when icon resources would lose their relative base.

# 1.17

- Replace browser-based package search with an in-app Recommended / All PyPI / Installed catalog and paginated name search.
- Stream the official Simple Index in a cancellable worker, cache names atomically and keep the previous cache on failed refresh.
- Load descriptions/licenses and Python-compatible stable version metadata internally; support direct exact-name lookup without the full index.
- Scope selections to the current interpreter, debounce metadata requests and prevent stale results from enabling installation.
- Extend recommendations with component/provider packages and replace idle PIP wizard plans when a different explicit package is selected.

# 1.16

- Recover malformed IDE settings and validate color/grid/font/flag values before building the UI; accept Tk named editor colors.
- Reset editor target, text and native undo across history/form context changes; prevent edits without an active target.
- Use unique atomic text-file replacements with failure cleanup for project and local source saves.
- Cancel queued startup audit work on destruction, track polling lifetime and key report validity to actual dependency inputs.
- Scope installed API results to the interpreter and resolve project-local component modules. Reject non-integer model geometry before rendering.
- Handle concurrent analysis-worker exits and make the full test suite independent of the selected UI language.

# 1.15

- Reorganize the IDE around a VB6-style toolbox, central designer/code workspace and right-hand Project Explorer/Properties split dock.
- Add compact icon toolbar, focus-safe in-window tooltips, F7/Shift+F7 navigation, object selectors and geometry status.
- Add searchable categorized/alphabetical property rows, read-only identifiers and compact grouped styling.
- Add eight active resize handles with grid snapping, opposite-edge preservation and cursor feedback.
- Add VB6 Classic appearance and contrast-aware editor syntax palettes while retaining saved custom colors.

# 1.14

- Add token-aware property value guidance, paired text quotes and enum/boolean suggestions across registered component defaults.
- Add an inspector Documentation tab with offline reference/examples, validated descriptor HTTPS links, official URLs and isolated installed API help through pydoc.
- Add non-blocking startup distribution/PIP checks, compatible stable PyPI candidates, pip check and documentation link verification; keep failures actionable and preserve offline help.
- Route declared requirement updates through the existing PIP wizard with extras and constraints preserved. Add opt-out settings and installer modules/CA resources.

# 1.13

- Add built-in MIDIPlayer, ExcelWorkbook, PDFDocument, PrintDocument, CloudStorage and LLMClient controls with guided setup and asynchronous events.
- Support MIDI output to synthesizers, XLSX/XLSM sheets/cells, PDF text/merge/extraction, and operating-system print submission with confirmation.
- Add Google Drive OAuth/ADC, S3/MinIO and WebDAV file operations; add official OpenAI, Claude and Gemini text APIs with model listing.
- Keep runtime credentials in memory or external storage; validate environment variable names and reject secret-valued project properties.
- Collect provider-specific dependencies, SDK resources and certificates for deployment. Add bilingual documentation and three examples.

# 1.12

- Add a 19-family library/theme catalog with interpreter-scoped import checks and isolated representative GUI probes.
- Expand ttk and CustomTkinter controls; add tksheet, map and selected Pmw integrations with contextual completion examples.
- Add validated nested frame/tab relationships, page previews, subtree duplication/deletion and parent remapping on form duplication.
- Add ttkbootstrap 1.x, ttkthemes, sv-ttk and local Azure/Forest theme configuration, preserving independent CustomTkinter appearance.
- Collect active library resources in deployment and fix CustomTkinter constructor geometry.
- Keep separate-engine frameworks informational and Tix unsupported in Python 3.15+.

# 1.11

- Add a project file/folder explorer with UTF-8 editing, imports, renaming, recoverable trash and explicit deployment inclusion.
- Add a Deploy wizard and toolbar action exporting source, resources, requirements and Mac/Windows run/build/install scripts.
- Native build driver produces macOS app/DMG, Windows portable ZIP and optional Inno Setup installer. Build on each target platform.
- Resolve local project modules during IDE execution without shifting debugger lines.

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
