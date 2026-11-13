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
