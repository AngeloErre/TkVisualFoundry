# General debug and stress report — TkVisualFoundry 1.33

Date: 13 November 2026. Interpreter: Python 3.15.2, macOS. This is a completed automated/offline test session, not an overnight monitoring service or a native graphical acceptance claim.

## Reproduced defects and fixes

| Defect | Reproduction before the fix | Result after the fix |
| --- | --- | --- |
| Python identifier normalization | The mathematical Unicode name `𝚛𝚘𝚘𝚝` passed validation; Python normalized the generated attribute to `root`, overwriting the internal Tk root | Require stable NFKC identifiers before generation/loading. Ordinary canonical Unicode names such as `caffè` and Greek names remain valid. Ambiguous legacy names must be renamed in the project file before opening |
| Malformed project/event code | Loading with `code=False` accepted a list as an event body or non-text startup/import fields, allowing invalid values into the editor | Validate container shapes and text types before replacing the open project. Incomplete **text** code still loads for recovery |
| Preview comparison lost data types/content | JSON `null` → `"NULL"`, number `1` → text `"1"`, and same-length changed binary blobs could appear unchanged | Bounded row comparison keys include scalar type information and binary content digests; duplicate row counts are retained |
| Reader process shutdown race | The viewer could terminate an already-exited process or miss a worker created concurrently with closure | Synchronize process ownership, tolerate exit races, cancel read-only workers, reap them through communication and close pipes. Closure is idempotent |

Nine focused regressions cover these cases, including an actual worker created after the close request and an actual cancelled child process. Test fixtures use temporary data only.

## Completed checks

| Check | Workload | Outcome |
| --- | --- | --- |
| Full Italian suite | 286 tests | 275 passed, 11 graphical tests skipped |
| Full English suite | 286 tests; fixed hash seed | 275 passed, 11 graphical tests skipped |
| Deterministic randomized projects | 300 projects, 1–4 forms, random standard controls/events | Each generated twice identically, compiled and tokenized |
| SQLite under concurrent activity | 2,000 rows, 60 worker reads, at most 4 concurrent readers, 100 committed updates | All readers completed with bounded previews; row count remained 2,000 |
| Atomic file writes | 100 temporary project writes/readbacks | All contents matched; no temporary write artifacts remained |
| Reader cancellation | 40 freshly started child processes | All cancelled and reaped |
| Variable inspector sampling | 500 snapshots with cyclic and 10,000-item containers | Output remained bounded |
| Large generated source | 100, 1,000 and 3,000 controls | Generated, compiled and tokenized; largest source 816,833 UTF-8 bytes / 228,357 tokens |
| Existing examples | 15 project examples | Validated and generated source compiled |
| Distribution checks | Python sources, shell script syntax, README links, ZIP integrity | Checked before publication |

The measured first stress run completed 300 randomized projects in 1.779 seconds; 60 concurrent reads/100 commits in 0.692 seconds; and generation + compile + tokenization for 3,000 controls in 0.226 seconds. These are local, synthetic, non-GUI measurements, not response-time guarantees. The committed runner was executed again to verify reproducibility; timings naturally vary.

## Reproduce

From the repository root, using a compatible Python with the normal development dependencies:

```bash
VTS_LANGUAGE=it python -m unittest discover -s tests
VTS_LANGUAGE=en PYTHONHASHSEED=133 python -m unittest discover -s tests
python tools/stress_check.py
```

The runner prints JSON measurements, uses a fixed random seed and creates disposable fixtures inside a temporary directory. It does not launch user applications, access real project data or install packages. The unit suite additionally covers actual debugger subprocesses, stack/variable snapshots, environment creation, local history, dependencies, project/deployment files and component adapters. Optional service integrations are tested through their offline/mocked contracts.

## Remaining acceptance work

- The 11 graphical tests remain skipped because the available execution session cannot create Tk windows. Desktop Terminal access was unavailable in the prior attempt; this run does not claim visual clicking/typing or a full-window soak test.
- Native Windows/macOS installation, uninstall and generated app acceptance require target sessions. No existing user installation was removed or updated by these tests.
- Access ODBC and legacy XLS/DBF/Parquet native readers, camera/MIDI/printing and live cloud/LLM services require their own platform/device/service acceptance.
- The data viewer remains a bounded inspection tool, not a complete audit trail. It cannot certify that the entire database is unchanged when its sample is unchanged.
- Canonical identifier validation intentionally rejects ambiguous Unicode spellings rather than silently changing existing code references.

## Resoconto in italiano

Completata una sessione automatica di debug e stress test. Corrette quattro classi di difetti: nomi Unicode che Python trasformava in attributi interni; strutture e codice evento non testuali accettati all’apertura; confronto dati che perdeva tipi e contenuto binario; chiusure concorrenti dei processi di lettura.

Risultato: **275 test superati per lingua**, 11 grafici saltati. Eseguiti 300 progetti casuali, 60 letture SQLite con 100 commit concorrenti, 100 scritture atomiche, 40 cancellazioni di processi con raccolta completata, 500 snapshot variabili e generazione/compilazione/tokenizzazione fino a 3.000 componenti. Validati anche i 15 esempi e il pacchetto di distribuzione.

I test grafici e l’accettazione nativa delle installazioni e dei servizi opzionali restano aperti. Tutti gli stress test hanno usato dati temporanei: progetti, dati reali e installazione dell’utente non sono stati modificati. Il confronto nel visualizzatore rimane limitato al campione dichiarato.
