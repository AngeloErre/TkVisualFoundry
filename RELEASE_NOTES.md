# VisualTk Studio 1.28

Add a persistent Watch tab with read-only scope/type/value, expandable captured containers and changed-value accents. Support names, Application fields, non-negative indices/string keys and explicit globals/locals/last scope prefixes. Resolve only existing inspector samples without executing calls, arithmetic or properties.

Add/remove watches with project undo, preserve direct self component paths through smart rename, clear data for unmonitored launches and isolate samples when another project opens. Limit paths, child rendering and hidden-tab work. Values outside bounded snapshots remain unavailable. Update the variable inspector example and bilingual READMEs; see docs/WATCHES.md for scope precedence and limits.

242 tests passed per language, 11 graphical tests skipped. A real isolated runner test observes a watched global changing; graphical acceptance remains pending.
