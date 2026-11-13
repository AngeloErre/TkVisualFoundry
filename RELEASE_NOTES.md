# TkVisualFoundry 1.32

Add Project → Data viewer: read-only SQLite, SQL script text, Excel, JSON/JSONL, CSV/TSV and optional Access/DBF/Parquet readers. Browse tables/sheets, filter samples, refresh manually/every two seconds and compare with a session baseline. Use the existing PIP wizard to prepare the reader in the project Python. Access needs a compatible system ODBC driver; DBX support is SQLite-header only.

Comparisons cover a bounded preview (500 rows, 80 columns, 512 characters per cell), not a full audit. A modified row counts as one added/one removed; formulas are not recalculated and SQL is never executed.

266 tests passed per language; 11 graphical tests skipped. Access uses mocked driver contracts; native Access, legacy XLS/DBF/Parquet and graphical acceptance remain pending. See docs/DATA_VIEWER.md.
