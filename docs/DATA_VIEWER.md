# Data viewer / Visualizzatore dati — 1.32

## English

Open **Project → Data viewer…** (also searchable in the command palette). Choose the data file used by your generated application. Start the application, perform a write, then click **Refresh** or enable **Refresh every 2 seconds**. Select a table/sheet and filter the displayed sample. **Show baseline** switches between the original sample and the current sample; **Reset baseline** starts a new comparison. Loading happens in a separate process using the selected project Python, with a 20-second timeout. A failed refresh stops automatic polling and keeps the last successful data; the error and last successful read time identify stale data.

The viewer does not edit data. It reads SQLite with `mode=ro` and `query_only`, opens Access with ODBC read-only mode, and never saves spreadsheets or executes SQL scripts. SQLite WAL updates are visible after the application commits. Uncommitted changes and files still buffered by the application are not visible.

| Format | Reader / requirements | Notes |
| --- | --- | --- |
| SQLite (`.sqlite`, `.sqlite3`, `.db`, or any SQLite-header file) | Python standard library | User tables; no arbitrary queries, remote SQL servers or encrypted SQLite support |
| `.sql` | Python standard library | Script text with line numbers; never imported or executed |
| Access `.mdb`, `.accdb` | `pyodbc` plus a compatible Access ODBC driver | Driver must match Python architecture; PIP cannot install the driver. Native acceptance pending. On macOS/Linux export to SQLite/CSV if no compatible driver is available |
| `.xlsx`, `.xlsm` | `openpyxl` | Select sheets; formulas are displayed, not calculated; macros are not executed |
| `.xls` | `xlrd` | Legacy Excel; date cells may appear as serial values |
| `.json`, `.jsonl`, `.ndjson` | Python standard library | JSON arrays of records, top-level lists as separate datasets, nested values in cells |
| `.csv`, `.tsv`, `.txt` | Python standard library | UTF-8/BOM; detected comma/semicolon/tab/pipe delimiter; first row is a header |
| `.dbf` | `dbfread` | Required memo sidecars must also be present |
| `.parquet` | `pyarrow` | Streamed record batches, limited columns |
| `.dbx` | SQLite-header recognition only | DBX is ambiguous; Outlook DBX and other proprietary DBX formats require export to CSV/JSON |

Use **Prepare reader with PIP…** for the selected format. The existing dependency wizard verifies and installs its reader in the selected project Python. Optional packages are not added to generated application requirements just because the IDE viewer uses them. Reader availability depends on Python/platform compatibility.

### Comparison limits

The preview shows up to **500 rows, 80 columns and 512 characters per cell**, with a 3 MiB serialized row budget. Text/JSON source files are limited to 32 MiB. Larger database/Excel files can be sampled; malformed or slow files may time out. Filtering applies only to the current sample. Excel preserves row 1 as data and uses C1/C2 column headings.

Added/removed counts compare multisets of displayed row values, including duplicates. A modified row is counted as one removed and one added row; rows are not matched by primary key. Column changes are reported separately. Changing table/file resets the baseline. The baseline lives only in this viewer session. Updates outside the sample or beyond truncated cell text are not detected: **unchanged preview does not prove an unchanged database**. This is an inspection aid, not a complete audit log. No editing, exports, database credentials or SQL execution are exposed.

Validation: real SQLite/WAL commits, quoted table names, missing-file preservation, SQL non-execution, CSV Unicode/multiline, JSON dataset selection, row/cell limits, duplicate comparisons, real XLSX formulas/no-save, and a real worker subprocess. Access read-only/driver behavior uses a mocked ODBC contract; native Access, legacy XLS/DBF/Parquet and interactive GUI acceptance remain pending.

## Italiano

Apri **Progetto → Visualizzatore dati…**, scegli il file usato dalla tua applicazione e la tabella o il foglio. Aprilo prima di eseguire l’operazione da controllare. Dopo la scrittura premi **Aggiorna**, oppure attiva l’aggiornamento ogni due secondi. **Mostra riferimento** visualizza il campione iniziale; **Nuovo riferimento** ricomincia il confronto dal campione corrente. La lettura usa il Python del progetto in un processo separato. Gli errori fermano l’aggiornamento automatico e lasciano visibile l’ultima anteprima riuscita, con relativo orario.

Il visualizzatore è in sola lettura. Le modifiche SQLite sono visibili dopo il commit; i dati non ancora salvati dall’applicazione non possono essere rilevati. Sono disponibili SQLite, script SQL come testo, Access con driver ODBC compatibile, XLS/XLSX/XLSM, JSON/JSONL/NDJSON, CSV/TSV/TXT, DBF e Parquet. **Prepara lettore PIP…** apre il wizard per installare il lettore necessario nel Python selezionato. Per Access occorre anche il driver di sistema; PIP da solo non basta. I DBX sono riconosciuti soltanto se contengono SQLite: gli altri formati DBX richiedono esportazione.

Il confronto riguarda **solo l’anteprima**: massimo 500 righe, 80 colonne, 512 caratteri per cella e 3 MiB di righe serializzate. I file testuali/JSON non possono superare 32 MiB. Il filtro cerca soltanto nel campione visualizzato. Nei CSV la prima riga è l’intestazione; in Excel viene conservata come dato, con colonne C1/C2. Le formule Excel sono mostrate senza calcolo.

Una riga modificata conta come una rimossa e una aggiunta; non viene associata per chiave primaria. I duplicati sono conteggiati. Il riferimento è temporaneo e cambia aprendo un altro file o una diversa tabella. Un campione invariato non certifica che l’intera base dati sia invariata. L’accettazione grafica e i lettori opzionali su piattaforme native restano da verificare; SQLite, Excel XLSX e i formati testuali sono coperti dai test automatici.
