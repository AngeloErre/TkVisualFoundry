# Variable inspector

Open **Variables / Inspector**, or click **Inspector** in Output/Debug, then launch with **F5** or **F9**. Monitoring is enabled by default; the checkbox controls the next launch. Disable it when comparing normal execution performance.

The inspector runs only inside IDE-launched processes. Generated source, visual preview and deployment builds are not instrumented. Snapshots stay in the temporary session folder and are not saved into the project or uploaded.

## Available scopes

- **Locals**: variables in currently active project frames, including worker threads when sampled during execution. Paused debug includes local scopes from the selected frame and its project callers.
- **Last locals**: a bounded copy of the last observed returning project function when no project function is active. This is explicitly historical, not a currently live scope. Rapid repeated calls are throttled.
- **Globals**: generated application globals plus Python files explicitly included in the project's deployment resources when those files execute. Dunder interpreter metadata is omitted; ordinary underscore-prefixed user variables remain visible.
- **self attributes**: ordinary stored fields of the generated Application instance, such as `self.counter`. Tk widgets and other complex objects are summarized rather than queried.
- **Call stack**: frame names, file paths and line numbers. During live execution it shows sampled project frames; while paused it includes the selected frame's callers. This first version does not switch pdb frames by clicking the stack.

Filter by variable name, expand standard dictionaries/lists/tuples/sets and compare successive samples: changed displayed values use an accent color. Values are read-only. Existing pdb console commands remain available separately.

## Sampling and limits

Values refresh approximately every **0.5 seconds**, after serialization and delivery. This is sampled monitoring, not a hard real-time trace of every assignment. Short-lived locals can be missed, and independent threads can change values during a sample. Use a breakpoint for a specific point in the selected debug thread; other threads may continue.

Values are bounded: strings are excerpts, container trees stop after three levels and at most 30 items per container, namespace and overall node budgets apply. Large collections are marked with an ellipsis. Arbitrary object `repr`, properties, descriptors and expressions are not evaluated to collect values; custom objects are summarized by type. Class attributes, computed properties, external library internals, future local values and unobserved short-lived scopes are not enumerated. This avoids calling application code from the monitor thread.

Instrumentation uses a lightweight call/return profile and a background sampler. It adds overhead and is intended for development. A project that replaces Python profiling hooks can prevent returning-local capture; live global/active-frame sampling can still work. The first version observes the launched process, not child processes it creates.

The last sample remains visible after normal exit or Stop and is marked **Finished**. Each launch uses a separate snapshot path so old sessions cannot overwrite a new session's display.

## Validation

Real isolated subprocess tests cover changing globals/self fields, returning-function locals, pdb pause/next, function-local breakpoints and stack data. Tests also cover cycles, value limits, custom repr/properties/dictionary overrides and stale-session completion. Interactive graphical acceptance remains pending.
