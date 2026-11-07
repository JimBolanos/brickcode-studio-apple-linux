# Changelog

All notable changes to BrickCode Studio. Dates are release dates.

## 2.4.0 — 2026-11-06

### Added
- **A block editor for the EV3**, in `pybricks/`. It writes Pybricks Python:
  nothing is compiled or sent from the app, you copy the code and paste it
  into Pybricks. It opens from a fourth card on the dashboard, or from
  **File → Pybricks block editor (EV3)…**.
  - **Devices are set up once, by name,** the way Pybricks' own editor does
    it: a **set up** block names the brick, each motor and sensor with its
    port, and a drive base, and every other block picks one from a list of
    those names. The output reads like a program written by hand
    (`arm1 = Motor(Port.B)`, `arm1.run_angle(...)`), not `motor_b`.
    Renaming a device carries every block that uses it.
  - EV3 sensors (touch, colour, gyro, ultrasonic, infrared) and NXT sensors
    (touch, light, colour, sound, ultrasonic). The NXT classes are imported
    as `NXTTouchSensor` and so on, because three of them share a name with an
    EV3 class and both can sit in one program.
  - A block pointing at a missing device, two devices on one port or two with
    one name get a warning triangle, and the file says so in an `# ERROR:`
    line at the top.
  - Same palette, category order and look as the NQC/NXC editor. It shares
    that editor's copy of Blockly rather than carrying a second one.
  - **Motors and Movement work like the NXT editor**, with no Set up for
    them. A motor block has a port, A to D, and the program declares the
    motor itself; the speed is in per cent and the amount in seconds,
    degrees or rotations: `motor A run for 1 seconds at 75 % speed`,
    `start motor A at 75 % speed`, `stop motor A brake`, `stop all motors`,
    `reset motor A degrees counted`, `reset all motors`. Movement is the
    two-wheel robot: `set movement motors to B+C wheel 56 mm axle track
    114 mm` (B+C, 56 and 114 when left out), `move forward for 1 seconds at
    75 % speed`, `turn right for 90 degrees at 50 % speed`, `start moving`,
    `stop moving` and `tank`. 100 % is 1000 °/s for a motor, 500 mm/s for the
    robot and 300 °/s for a turn. Degrees and rotations of the robot come
    from the wheel size. A number typed in is calculated in the Python
    (`run_time(750, 1000)`); a variable stays an expression.
  - **Display and Light & Sound** are separate categories. Light & Sound has
    the brick light, beep, play notes and volume. Display gains **dot at x y** (`draw_pixel()`) and, under
    "Terminal", **print in the terminal** (`print()`, which goes to the
    computer's terminal and not to the EV3 screen).
  - **Pictures on the EV3 screen.** Display starts with **show image**, a
    dropdown of the EV3's built-in pictures (eyes neutral, angry, sleepy,
    evil, dizzy, crazy, winking, looking up/down/left/right; thumbs up/down,
    warning, question mark, stop, arrows…), written as
    `ev3.screen.load_image(ImageFile.ANGRY)` with
    `from pybricks.media.ev3dev import ImageFile`. Names taken from
    pybricks.com/ev3-micropython/media.html. Below it, **show … on the
    screen** draws a happy, sad or serious face, eyes open or closed, or an
    arrow in the four directions, a smiling, winking or unsure face, a big
    or small heart, sleeping ZZZ, a speech bubble, an explosion and mouths with
    teeth or fangs, with plain `draw_*` calls in a small
    function written above the program. A program that only draws needs a
    final **wait**, because the screen goes back to normal when it ends.
  - **Set up can still declare the devices, as in Pybricks' own editor**:
    `motor named … on port A with forward clockwise ↻` (or counterclockwise
    ↺), `drive base named … left motor … right motor … wheel 56 mm axle track
    114 mm` and `car named … steering motor … drive motor …`. A motor block
    on a port Set up already has uses that motor; the movement blocks drive
    the drive base declared in Set up when there is one, and otherwise the
    robot from `set movement motors`. The car has its own `drive at power` and
    `steer by` blocks at the bottom of Movement.

### Fixed
- **Run from the source tree, the app could not open the block editor.** It
  found the page by a relative path, and a `file://` address has to be
  absolute, so the click only logged an error. Installed copies were never
  affected.
- **The four bricks on the dashboard were not the same size.** Each drawing
  was fitted to the card by its own box, so the EV3 (tall and narrow) came
  out biggest and the NXT smallest. All four are now scaled to the same
  height, whatever the shape of the card, and the widths stay natural. The
  cards were also different widths (the EV3 footer line is the longest), and
  the drawing grows with the card, so the row is now homogeneous.
- The dashboard cards use blended gradients of four or five colours, with
  colours taken from the Robot Inventor home screen in the same order:
  violet to wine (RCX), teal-grey to magenta (Scout), teal to deep purple
  (NXT) and teal to indigo to violet (EV3).

### Changed
- The dashboard screenshot in the README was stale; it is regenerated, with the
  current RCX and the new card.

## 2.3.3 — 2026-11-02

### Fixed
- **`linux/install-arch.sh` could not build the app.** It compiled without
  fontconfig, so linking died on `undefined reference to
  FcConfigAppFontAddFile` — and it died at step 4 of 5, after spending
  minutes building nqc and nbc. It also never installed the block editor or
  the Orbitron font, and never passed `-DBLOCKS_DIR`, so even a binary that
  had linked would not have found the editor. Reported from Omarchy.
- The three Linux installers each carried their own copy of everything after
  the package step — about 55 identical lines, three times over. Arch was
  simply the copy nobody updated when fontconfig and the block editor were
  added. Those steps live in `linux/_build.sh` now, sourced by all three, so
  the next fix lands everywhere at once. Verified by running the Debian one
  end to end on Ubuntu 24.04 after the change: nqc, nbc, the app, the editor
  and the font all install, and both compilers produce working output.

## 2.3.2 — 2026-11-02

### Fixed
- **The Links in About were unreadable.** 2.3.1 stopped them wrapping into
  ragged lines by cutting them with an ellipsis instead, but the column only
  gives an address about 190px beside its label: every github row came out as
  the same `github.com/JimBolano…`, so Repository and Issues read identically.
  The address now sits under its own label, with the full width, and the two
  github rows drop the `github.com/JimBolanos/` that was eating it. Hovering
  still shows the real address.
- **`linux/install-debian.sh` failed at the first step on Debian, Ubuntu and
  Mint.** It asked apt for `libfontconfig-1-dev`, which is not a package —
  the name is `libfontconfig-dev` — so `apt` stopped with "Unable to locate
  package" and nothing was installed. Nobody on that family of distributions
  could have used the script. The README repeated the same wrong name in its
  manual steps.

### Added
- **Install instructions that assume nothing**, for macOS and for Debian,
  Ubuntu and Mint: numbered steps from opening a terminal to opening the app,
  one block per step. They used to start at `bash macos/install-mac.sh`,
  which is no use to someone who has not got the code yet or does not have
  Homebrew.
- `update-mac.sh` run outside a clone said only "Not a git clone" and
  stopped. Most people arrive from a release zip, where there is nothing to
  pull, so it now points at `install-mac.sh`.

### Changed
- The Linux instructions said `cd brickcode-studio/brickcode-studio` after
  cloning, a path that stopped existing when the repository was renamed.
- `install-debian.sh` was marked "not tested yet". It has now been run end to
  end on Ubuntu 24.04: nqc 3.2 and nbc 1.2.1 both build, and both produce
  working output. No brick was attached, so the tower is still untested there.
- The README's "What's new in 2.3.0" heading needed editing every release to
  stay true, and had already stopped being true. It is "What's new" now, with
  a pointer to this file for the full history. The About screenshot beside it
  still showed 2.3.0 and the repository's old name.

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
