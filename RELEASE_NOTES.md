# TkVisualFoundry 1.42

Four additional editable starter applications bring the chooser to **36 starters plus Blank project**:

- **Kanban and Pomodoro:** three drag-and-drop stages, task CRUD, ISO due dates, overdue marks, bounded/scrollable board, atomic versioned JSON saves, unsaved guards and monotonic focus timer with pause/resume/reset.
- **Interactive Data Explorer:** read-only UTF-8 CSV/TSV, active XLSX sheet and SQLite tables, filtering/sorting/pagination/scrollbars, finite numeric min/max/mean, zero-baseline chart and separate filtered CSV export. Source overwrite aliases are rejected and formula-like text escaped on export. Limits prevent unrestricted row/text/workbook loading. `openpyxl>=3.1,<4` is declared for XLSX.
- **Memory and Attention Lab:** adaptive 2–9 digit sequences, fixed 6×6 visual search, response times, latest 200 anonymous session results, chart and CSV export. Educational demo, without diagnostic norms or clinical interpretation.
- **The Clockwork Observatory:** original three-room investigation, clues/keys/inventory, two puzzles, solo/rescue endings and validated atomic JSON progress. Story content is editable JSON data in global code.

Each has English-commented global/startup/event code; chooser metadata is Italian/English. Thirty-two starters require no extra PIP; four declare optional packages. Creating a template loads a fresh unsaved project copy without executing its code.

Remote Python 3.15.2/Linux: **418 tests passed per language, 11 graphical tests skipped; 51 example projects validate and compile**. Twenty-four new regressions include real CSV/SQLite/XLSX round trips, timer phases/deadlines, persistence failure cleanup, drag/drop logic and both complete adventure paths. No native Mac GUI, mouse/keyboard, PIP or target-build validation was performed. These checks await **ambiente collegato**.

See [starter guide](docs/STARTER_TEMPLATES.md) and [Mac reconnection checklist](docs/MAC_RECONNECT_CHECKLIST.md).
