# IntelliSense

Import a module, then type a dot to request members: `from tkinter import messagebox`, followed by `messagebox.`. Typing an opening parenthesis requests a signature. Suggestions follow the imports, aliases, variables and component types visible in the current editing context.

Jedi runs in a separate persistent worker using the selected project interpreter. Install it through the engine setup action. Escape dismisses completion; stale responses are discarded. Libraries must be available in the selected environment. Static analysis cannot fully describe every dynamic API. Contextual snippets remain available as a fallback.
