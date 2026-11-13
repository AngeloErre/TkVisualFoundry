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
