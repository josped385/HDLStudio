# Changelog

## Unreleased / v0.2.0 (planned)

### Added
- Code folding — collapse/expand indented blocks (modules, always, begin/end, etc.)
- Undo/Redo actions in Edit menu (Ctrl+Z / Ctrl+Y)
- Splash screen with app logo while loading
- Window geometry persistence — remembers size and position between sessions
- Testbench templates for quick testbench generation in templates dock

### Changed
- Toolbar labels: "TB:" → "Testbench:", "Sim:" → "Simulator:"
- Refined hover tooltip system — uses `wordAtPoint` instead of raw Scintilla messaging for reliability
- Reduced splash logo size for better proportions
- Hover database now re-indexes files on save

### Fixed
- Hover tooltip crash (0xC0000409) — `SendScintilla` no longer called during event processing
- Off-by-one-line hover precision — replaced font-metric arithmetic with Scintilla coordinate mapping
- Various theme consistency issues across docks
