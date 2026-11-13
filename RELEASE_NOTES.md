# TkVisualFoundry 1.33

General stress/debug release. Fix four reproduced issues: Unicode identifier aliases could shadow internal attributes, malformed non-text events could enter the editor, data comparison confused NULL/text and numeric/text values, and reader shutdown could race process exit/start. Preserve canonical Unicode names, incomplete text code recovery and bounded previews.

275 tests passed per language, 11 graphical tests skipped. Offline stress: 300 random projects; 60 concurrent SQLite readers/100 writer commits; 100 atomic writes; 40 cancelled/reaped readers; 500 bounded inspector snapshots; generation/compile/tokenization up to 3000 widgets. See docs/DEBUG_REPORT_1.33.md and tools/stress_check.py.

Interactive GUI, target-platform installation/builds and native optional reader/device/cloud validation remain pending. No user installation, project or real data was changed by the stress fixtures.
