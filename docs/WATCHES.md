# Watch paths

Open **Watch** (also available from **Output/Debug → Debug → Watch**) and add a path such as `self.counter`, `self.samples[0]` or `config['port']`. Launch with F5 or F9 while inspector monitoring is enabled. Watches are saved in the project; adding/removing a watch is undoable. Remove a watch by selecting its row (or an expanded child) and clicking **Remove selected**.

## Supported paths

- Names: `counter`, `settings`.
- Application fields: `self.counter`, `self.samples`.
- Standard-container access: `self.samples[0]`, `settings['port']`, `settings['nested'][2]`.
- Explicit scope prefixes: `globals.counter`, `locals.counter`, `last.counter`.

A bare name looks first in sampled active local scopes, then globals, then historical returning-function locals. In a paused debug session, frame selection updates active locals and puts that frame’s module globals first. Explicit `locals` excludes historical locals; `last` selects those historical values. If more than one matching group exists, the first group shown by the inspector wins; the Scope column identifies that source. `globals`, `locals`, `last` and `self` are reserved scope prefixes in watch paths.

Only identifiers, attributes, non-negative integer indices and literal string keys are accepted. Calls, arithmetic, comprehensions, slices, negative indices and assignment are rejected. Watches do not evaluate Python expressions, invoke properties or query widgets. Custom object attributes are available only when already represented by inspector data; arbitrary objects are summarized, not traversed.

## Values and lifetime

Watches read existing inspector samples. Refresh is approximately every 0.5 seconds during execution and at pdb stops. Expand a container to view the sampled children; changed displayed data uses an accent color. Lists/dictionaries can be excerpts: a path outside the captured items displays **Unavailable in sample**, rather than fetching or fabricating a value.

The inspector's limits apply (three container levels, at most 30 captured children per container, bounded namespaces/overall values). Up to 100 unique watch strings are supported, each at most 256 characters and 16 path steps. Rendering also has a shared child-node budget. Watch trees update only while their tab is visible to avoid unnecessary UI work.

Short-lived locals may be absent. Historical locals are identified by the Scope column and the `last` prefix. Finished processes retain their last sample; opening another project starts a different ownership session and does not reuse those values. Disabling monitoring for a new launch clears live watch data. Code edits affect the next launched source, while watch-path changes can be made during the current session.

Smart rename updates direct `self.ComponentName` references in watch paths, preserving unrelated dictionary keys and bare local names. Existing exported/preview/deployment source remains uninstrumented.

## Example

Open `examples/Debugging/VariableInspectorDemo.vtk.json` and select Watch. The example includes `self.counter`, `self.samples` and `self.samples[0]`. F5 runs normally; click Increment to see changes. With F9, continue from the initial pdb stop, then click Increment to stop at the included event breakpoint and inspect values.

## Validation

Tests cover scoped lookup, nested standard containers, unavailable/truncated values, rejection of executable expressions, persistence/rename and project-session ownership. A real isolated runner test verifies a watched global changes across successive snapshots. Interactive graphical acceptance is still pending.
