# VisualTk Studio 1.24

Adaptive anchors now support controls inside Notebook pages. Client-area calibration accounts for theme borders and tab headers, including pages first opened after resizing. Each page has independent resize handlers. Nested ordinary frames retain their existing support.

Use Edit → Adaptive anchors or inspector Actions. Try examples/Layout/NotebookAnchorsDemo.vtk.json. CustomTkinter controls and scrollable internals remain unsupported.

218 tests passed per language, 11 graphical tests skipped. Actual graphical resizing and theme/platform acceptance remain pending.
