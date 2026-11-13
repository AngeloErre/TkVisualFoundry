# VisualTk Studio 1.25

First-stage visual debug position: F9 starts pdb, the output panel reports current line/function and Show line opens a yellow marker in the immutable session source. Resume clears the marker; external frames and process termination update status. Project edits take effect on the next launch; stop before changing GUI breakpoints. Existing pdb commands remain available; graphical watches are not included.

224 tests passed per language, 11 graphical tests skipped. Real piped pdb subprocess and parser/session regressions tested; interactive GUI acceptance pending.
