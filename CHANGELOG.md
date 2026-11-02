# Changelog

All notable changes to BrickCode Studio. Dates are release dates.

## 2.3.1 — 2026-11-02

### Fixed
- **The Links column in About came out ragged.** Those labels wrapped, so a
  long address broke into three lines and pushed the rows under it out of
  line. They are cut with an ellipsis on one line now, with the whole address
  on hover.
- **Every link pointed at the repo's old name.** GitHub redirects it, so
  nothing looked broken — but that redirect stops working the moment a repo
  called `brickcode-studio` exists on the account again, and then the links
  go somewhere wrong instead of failing loudly.

### Added
- `blocks/pin.py` and `blocks/test/`. The script that builds the Windows
  edition's copy of the editor, and the suite that compiles everything the
  generator writes, both lived outside the repo — so neither edition could be
  rebuilt from what was committed anywhere. `blocks/test/run_all.py` runs the
  twelve tests that assert something.
- `CLAUDE.md`, with the handful of traps that have each already cost a
  rebuild.

## 2.3.0 — 2026-11-02

Two lines of work landed together: the NXT Screen, and a new front end with a
visual block editor.

### Added
- **Dashboard.** The app opens on the three bricks it can program. Picking one
  sets the language and the target in a single click; they used to be two
  separate controls in two different places.
- **Visual block editor** (`BLOCKS` in the bottom bar, or the button in the
  drawer). One self-contained offline page that writes NQC or NXC, with the
  MINDSTORMS palette, Save as, and the language fixed by the host when it can
  only compile one of the two.
- **Programs keep their blocks.** Saving from the block editor writes the
  workspace into the file as a trailing C comment, so the program opens back
  into blocks. Measured: `nqc` and `nbc` produce byte-identical output with and
  without it.
- **NXT Screen.** The NXT display shown live over USB, drawn as the brick, with
  clickable buttons and keyboard keys to walk its menus.
- **VLL panel.** The Scout sends VLL codes to a Micro Scout.
- **Bottom navigation**: HOME, CODE, BLOCKS, ABOUT.
- **ABOUT screen** with what the app uses, the documentation, the links and the
  author — all of it opening the guide installed beside the app, so it works
  with no network.

### Changed
- The window is painted in the MINDSTORMS Robot Inventor palette, sampled colour
  by colour. First run opens dark; Light stays one click away in Settings and
  keeps its own palette.
- The wordmark is set in Orbitron, which ships with the app under the SIL OFL.
- `make install` now also installs the block editor, the font and the user guide.

### Fixed
- The chosen language in the NQC/NXC switch was filled with a colour darker than
  the track behind it, so the selection read as a hole rather than a highlight.
- `PREFIX` is compiled into the binary, so `make && make install PREFIX=elsewhere`
  used to install a binary that looked for its data under the old prefix and
  silently found none. Changing `PREFIX` now forces the rebuild.
- `bricks.inc` was missing from the Makefile prerequisites, so editing the brick
  art did not trigger a rebuild.

## 2.1.1 and earlier

See the git history and the release tags.
