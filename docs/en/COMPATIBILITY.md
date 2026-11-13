# Compatibility

The macOS installer targets stable Python 3.15 or later with Tkinter. Prereleases are rejected. Source tests can also exercise non-GUI logic on other Python versions, but this does not establish installer support.

Optional packages may not yet provide wheels for every Python/macOS combination. The wizard displays installation output and can use source distributions unless wheel-only mode is enabled. Native libraries, permissions and physical hardware remain separate requirements.

The IDE interface supports Italian and English. Language changes take effect after restart. Exported component labels use the project language; existing text and code are not translated.
