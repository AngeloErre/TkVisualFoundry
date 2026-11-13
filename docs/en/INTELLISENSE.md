# IntelliSense

Import a module, then type a dot to request members: `from tkinter import messagebox`, followed by `messagebox.`. Typing an opening parenthesis requests a signature. Suggestions follow the imports, aliases, variables and component types visible in the current editing context.

Jedi runs in a separate persistent worker using the selected project interpreter. Install it through the engine setup action. Escape dismisses completion; stale responses are discarded. Libraries must be available in the selected environment. Static analysis cannot fully describe every dynamic API. Contextual snippets remain available as a fallback.

## Guided values, documentation and startup checks (1.14)

Typing `self.Button1.configure(text=` inserts paired quotes with the cursor inside. Accepting `text=` from completion does the same. Type the closing quote to step over the generated quote; Backspace in an empty pair removes both. Disable this feature in Configuration if preferred.

Guidance derives types from component properties and descriptor/designer defaults: strings, numbers, booleans and known choices such as state/orientation/anchor. It preserves existing values, comments and literals. Unknown types and general library calls continue to use Jedi without speculative value insertion. External descriptors can supply typed `defaults`.

The inspector **Documentation** tab includes an offline reference, examples, requirements, the official website and **Installed API (pydoc)**. The latter explicitly imports the selected component module in a separate process with a timeout; project event source is never executed. Installed docstrings may remain in the library's original language. No remote browser is embedded. External descriptors may add `"documentation": "https://example.org/documentation"`.

At startup, background checks inspect distribution metadata in the configured Python, declared project/IDE requirements, PIP, and all installed distributions. PyPI results exclude prerelease/development/yanked files and respect Python metadata and declared constraints. `pip check` reports dependency inconsistencies. This is not a native import, hardware or remote API test; also use the component wizard and diagnostics.

Use **PIP → Startup checks** or the inspector button. **Check again** uses the current project/interpreter. **Update with PIP wizard…** prepares updates for declared requirements only and preserves extras/constraints; PIP resolves transitive dependencies and checks wheel/platform availability. Unused optional libraries are not installed. Updates are not silently applied.

Documentation URLs are checked on every startup. Redirects are followed; 404/410 mean broken links. Network/certificate errors, restrictions and temporary failures remain unverified. Links are never silently removed or rewritten. The local reference works offline. Disable startup checks in Configuration if needed. HTTPS access to PyPI and documentation hosts is required; project source, credentials and files are not uploaded.
