# Follow-up debug report — TkVisualFoundry 1.33.1

Date: 14 November 2026. Python 3.15.2 on macOS. Continuation of the [1.33 stress/debug session](DEBUG_REPORT_1.33.md).

| Reproduced case | Before | Fix and verification |
| --- | --- | --- |
| Event/startup contains only comments or whitespace | Generated function has no executable statement; `IndentationError` prevents running/exporting | Append `pass` only in the generated function body. Preserve stored user text and existing line positions. Static Problems diagnostics use the same behavior |
| UTF-8 BOM project JSON | A valid project saved with a BOM fails JSON decoding | Read with `utf-8-sig`; regression verifies the source file is not rewritten |
| Deep container hierarchy | Recursive traversal raises `RecursionError` around Python's recursion limit | Iterative depth-first traversal preserves existing parent-before-child and sibling order. A 1,500-container project generates and compiles; a 1,500-node cycle is rejected as a cycle |

Six new regression tests cover these cases, true syntax errors, executable breakpoint line preservation and stable ordering. Incomplete non-comment Python code remains a real syntax error; it can still be loaded as text for repair. The IDE does not silently repair arbitrary user code.

Validation: **281 tests passed per language**, 11 graphical tests skipped, 15 existing examples validated/compiled, Python and shell syntax and README links checked. The committed offline stress runner was rerun after the hierarchy change. The full suite continues to exercise actual debugger/inspector subprocesses, project history, package preparation contracts, deployment fixtures and reader cancellation.

Graphical acceptance and native target-system builds/installations remain pending. The deep-hierarchy check covers project validation/order/generation/compilation, not a claim that native Tk can display arbitrarily nested widgets. No actual user project, installation or production data was modified by the test fixtures.

Reproduce from the repository root:

```bash
python -m unittest discover -s tests -p test_recovery_edges.py
VTS_LANGUAGE=it python -m unittest discover -s tests
VTS_LANGUAGE=en python -m unittest discover -s tests
python tools/stress_check.py
```

## Italiano

Riprodotti e corretti tre ulteriori problemi: eventi con soli commenti che impedivano di generare Python valido; progetti UTF-8 con BOM che non si aprivano; gerarchie profonde che superavano il limite di ricorsione. Il testo del progetto e le posizioni delle istruzioni restano conservati. Gli errori di sintassi effettivi continuano a essere segnalati.

Verificati 1.500 contenitori annidati, rilevamento di un ciclo della stessa profondità e ordine stabile dei fratelli. **281 test superati in italiano e inglese**, 11 grafici saltati. Restano da verificare interazione grafica e installazioni/build native: i test di profondità non certificano la visualizzazione di un numero arbitrario di contenitori Tk annidati.
