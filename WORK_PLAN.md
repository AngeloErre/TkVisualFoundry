# Development work plan — 1.19

Each step is implemented, checked and reported before the next step.

- [x] 1. Multiple selection: Shift-click, select all, group movement, duplicate/delete and sibling alignment/equal sizes/distribution. Preserve nested container relationships and undo.
- [x] 2. Problems panel: static event/startup/import syntax diagnostics, unknown self references and navigable source locations. No execution of project code; runtime dependency checks stay in the PIP wizard.
- [x] 3. Project Python environment: create/reuse a private .venv with the selected stable Python, switch interpreter for run/completion/PIP and restore it when reopening the project. Creation runs outside Tk; install dependencies through the existing wizard.
- [x] Final: bilingual tests, docs, GitHub and downloadable installer archive. Interactive desktop/target-platform validation is reported separately.

## Validation checkpoints

- Steps 1–2: 186 tests passed, 11 graphical tests skipped.
- Steps 1–3: 191 tests passed per language, 11 graphical tests skipped; a real isolated virtual environment was created/reused without network installation.
- Layout, problem navigation and onboarding still need interactive graphical validation.

## Phase 4 — real form preview (1.20)

- [x] Isolated visual-only form snapshot and selected tab page.
- [x] Independent process, F6/refresh/close controls, asynchronous validation/output.
- [x] Service/external placeholders, callback removal and project preservation.
- [x] Automated validation and bilingual documentation; graphical acceptance remains pending.

Next candidates: adaptive layouts, rename refactoring, local recovery/history and visual debugging.

## Phase 5 — reviewed smart rename (1.21)

- [x] Source-preserving AST plans for static form/control references and parents.
- [x] Review window, stale-plan checks, one undoable application and manual-review warnings.
- [x] Bilingual docs and backend regressions; interactive GUI acceptance remains pending.

Next: adaptive layouts, local recovery/history and visual debugging.

## Phase 6 — local history and recovery (1.22)

- [x] Periodic project/pending-editor snapshots outside deploy resources.
- [x] Atomic bounded history, comparison and explicit recovery as a new copy.
- [x] Configuration opt-out, startup discovery and regression coverage; graphical/crash acceptance pending.

Next: adaptive layouts and visual debugging.

## Phase 7 — adaptive anchors, first stage (1.23)

- [x] Optional edge anchoring/minimums and multi-control editor.
- [x] Embedded runtime helpers, ordinary nested frames, additive/coalesced events and fixed-layout compatibility.
- [x] Geometry/validation tests and bilingual scope documentation; graphical resize acceptance pending.
- [ ] Later: CustomTkinter scaling, tab/scrollable client areas and visual grid/pack layouts.

Next: visual debugging and expansion of adaptive layouts.

## Phase 8 — adaptive Notebook pages (1.24)

- [x] Independent anchors per page with measured client area and first-map calibration after resize.
- [x] Regression tests, demo and bilingual documentation; graphical/theme acceptance pending.
- [ ] CustomTkinter scaling, scrollable client areas and visual grid/pack remain future work.

## Phase 9 — visual debug position (1.25)

- [x] Current pdb line/function and explicit jump to generated-source highlight.
- [x] Immutable session source, resume/finish cleanup and old process isolation.
- [x] Real subprocess/parser tests and bilingual documentation; GUI acceptance pending.
- [ ] Later: graphical stack/variables/watch editor and event-relative breakpoints.

## Phase 10 — sampled variable inspector (1.26)

- [x] F5/F9 live globals, active/last locals, Application fields and stack snapshots.
- [x] Read-only expandable/filterable tree, changed values and bounded non-evaluating serialization.
- [x] Private per-session files, lifecycle isolation, real subprocess regressions and limits documentation.
- [ ] Interactive graphical acceptance, frame switching, explicit watch expressions and event-relative breakpoints.

## Phase 11 — event-relative breakpoints (1.27)

- [x] Persisted event/startup/import markers and editor Shift+F9 control.
- [x] Executable generated-source mapping, edit remapping and rename/save/load preservation.
- [x] Real pdb event-stop regression and bilingual docs; graphical acceptance pending.
- [ ] Next: explicit watches, graphical stack frame selection and broader UI acceptance.

## Phase 12 — persistent snapshot watches (1.28)

- [x] Saved read-only watch paths, explicit scopes and captured container expansion.
- [x] Non-executing resolution, bounded visible-tab rendering, changed values and rename preservation.
- [x] Cross-project ownership and unmonitored-launch reset; real changing-watch and model regressions.
- [ ] Graphical acceptance and stack-frame selection; arbitrary expression watches remain outside this first stage.

## Phase 13 — selected stack context and uninstall lifecycle (1.29)

- [x] Paused stack frame selection with selected locals/globals/Watches and stale-token protection.
- [x] Owned IDE uninstallers and Windows per-user install; generated Mac/Windows uninstall support.
- [x] Real pdb and temporary uninstall preservation regressions; bilingual documentation.
- [ ] Graphical acceptance: desktop control unavailable. Native Windows registry/shortcut/Recycle Bin and target OS installer acceptance pending.

## Phase 14 — TkVisualFoundry identity (1.30)

- [x] Rename visible product branding, docs, generator headers, repository links and build names.
- [x] Preserve project/storage identities and recognize owned legacy launcher manifests.
- [x] Migration and bilingual regression checks; native/graphical acceptance pending.

## Phase 15 — command palette (1.31)

- [x] Discover existing menu actions from Ctrl/Cmd+Shift+P and Edit menu.
- [x] Bilingual search, keyboard selection and session-recent ranking.
- [x] Model regressions and bilingual documentation.
- [ ] Interactive focus, keyboard and modal acceptance (desktop access unavailable).

## Phase 16 — read-only data viewer (1.32)

- [x] Selected-Python worker, bounded SQLite/Excel/JSON/CSV/SQL and optional reader adapters.
- [x] Dataset selection, sample filter, refresh and session baseline comparison.
- [x] Reader PIP wizard, format matrix, DBX/Access prerequisites and regression tests.
- [ ] Native optional-reader and interactive GUI acceptance.

## Phase 17 — general stress and debug (1.33)

- [x] Reproduce and fix Unicode namespace, malformed load, typed comparison and reader lifecycle defects.
- [x] Nine regressions, bilingual full suite and reproducible offline stress fixtures.
- [x] Report evidence and remaining native/graphical acceptance limits.

## Follow-up 1.33.1 — recovery edge cases

- [x] Comment-only function bodies and matching static diagnostics; preserve stored source and line offsets.
- [x] BOM project load and iterative deep hierarchy/cycle validation.
- [x] Six regressions, full bilingual suite and follow-up report.

## Phase 18 — global search and navigation (1.34)

- [x] All model scopes and live unsaved editor buffer snapshots.
- [x] Confined Python file scan, literal matching, limits and cancellation.
- [x] Navigable previews with content/project guards and Unicode indices.
- [x] Fourteen regressions and bilingual docs.
- [ ] Interactive graphical acceptance.
