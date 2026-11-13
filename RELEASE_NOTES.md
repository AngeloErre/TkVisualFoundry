# VisualTk Studio 1.27

Set persisted event-local breakpoints with the Breakpoint button or Shift+F9 inside the code editor; project startup/import code is supported too. F9 maps markers to exact executable generated-source lines, while unresolved/comment points are reported and skipped. Existing inspector and debugger positions remain available.

Text insertion/replacement/deletion remaps points; smart rename preserves metadata and deleted objects naturally remove their own points. Review markers after large rewrites because text diff is approximate. Stop debug before changing markers. Generated-source manual breakpoints remain transient; F5/export/deploy never activate project markers.

235 tests passed per language, 11 graphical tests skipped. A real pdb process stopped on a generated event method without creating Tk. Graphical marker/shortcut acceptance remains pending.
