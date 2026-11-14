# TkVisualFoundry 1.33.1

Follow-up debug: handle comment-only/whitespace-only event and startup bodies by appending pass in generated code only; use the same normalization in diagnostics. Preserve original text and executable line locations. Accept UTF-8 BOM project files. Order containers iteratively so deep valid hierarchies do not hit Python recursion limits, while cycles and invalid parent/page references remain rejected.

281 tests passed per language; 11 graphical tests skipped. Six new regressions include 1500 nested containers, a 1500-node cycle, deterministic sibling order, BOM no-rewrite and breakpoint line preservation. GUI acceptance remains pending. See docs/DEBUG_REPORT_1.33.1.md.
