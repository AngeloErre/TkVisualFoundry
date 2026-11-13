# VisualTk Studio 1.26

Add Variables / Inspector for F5/F9: read-only sampled locals, globals, Application self attributes and stack, expandable standard containers, name filtering and changed-value accents. Updates run about every 0.5 seconds; paused pdb captures selected-frame scopes. Last returning-function locals are labeled historical. Each launch has a private temporary snapshot; normal exit/Stop preserves last values as finished.

Values and scope counts are bounded; complex objects use type summaries without user repr/property evaluation. Sampling can miss short-lived locals and adds development overhead. Disable monitoring for the next launch when needed. Export, preview and deployment remain uninstrumented.

230 tests passed per language, 11 graphical tests skipped. Real live/debug subprocess tests passed; graphical acceptance pending. See docs/VARIABLE_INSPECTOR.md for full limits.
