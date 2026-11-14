# TkVisualFoundry 1.34

Add Edit → Global search and Ctrl/Cmd+Shift+F, also available in the command palette and file editors. Search events, startup/import code and confined Python files, using unsaved IDE buffers first. Results show component/file, line and preview; Enter/double-click opens the editor and selects the match. Literal search with match-case/whole-word options, cancellable worker, content/project freshness checks and bounded scanning. No replacement or automatic saving.

295 tests passed per language, 11 graphical tests skipped. Fourteen new regressions cover model search and actual snapshot/navigation handlers, including stale-source rejection and Tcl Unicode index units. Interactive GUI acceptance remains pending. See docs/GLOBAL_SEARCH.md.
