# Notes for Claude

BrickCode Studio: a GTK4 editor in C for the LEGO RCX, Scout and NXT. Programs
are written in NQC (RCX, Scout) or NXC (NXT) and sent over the USB IR tower.

There is a second edition, Windows-only and NQC-only, in its own repo:
[brickcode-studio-win11](https://github.com/JimBolanos/brickcode-studio-win11).
It carries a built copy of the block editor from here. **This repo is the
editor's only home**; see `blocks/README.md`.

## Build and run

```
cd brickcode-studio
make
./brickcode-studio
```

`PKGS = gtk4 libusb-1.0 fontconfig`. The `.prefix` stamp is deliberate: it
records the last `PREFIX` so `make && make install PREFIX=elsewhere` cannot
leave a binary with the wrong path baked in. Its helper rules sit **after**
the default goal, or `FORCE` becomes the default target.

On a Mac, `macos/install-mac.sh` builds `nqc` and `nbc` from source and
installs everything under `~/.local/brickcode`. The compilers end up in
`~/.local/brickcode/bin`, which is where the test suite expects to find them.

## The block editor

`blocks/index.html` is the source. `blocks/brickcode-blocks.html` is
**generated** by `build.py` — editing it is wasted work, the next build
overwrites it. The Windows copy is made with `pin.py`.

```
cd blocks/test
PATH="$HOME/.local/brickcode/bin:$PATH" python3 run_all.py
```

Plain `python3`, not `python3 -I`: the tests import `paths.py` from that
folder and isolated mode is exactly what keeps it off `sys.path`.

Nothing about generated code is taken on trust. Every program the generator
writes is handed to the real `nqc` or `nbc`, and the test fails if no `.rcx`
or `.rxe` comes out. Keep it that way — two bugs got through review because
the generated source reads perfectly well:

- **Motor pairs.** In NQC the output constants are a bit mask (`OUT_A` is 1,
  `OUT_C` is 4), so `OUT_A + OUT_C` means both motors. In NXC they are an
  enumeration (`OUT_A` is 0, `OUT_C` is 2), so the same expression means
  `OUT_C` alone: it compiles, and drives the wrong motor. NXC must emit the
  pair as one token, `OUT_AC`.
- **Definition order.** NXC rejects a function used before it is defined; NQC
  does not care. My Blocks go above `task main` on the NXT side.

## Traps that have already cost time

- **`[hidden]` loses to `display: flex`.** An element styled with a class and
  then given the `hidden` attribute stays on screen. Every such element needs
  its own `.thing[hidden] { display: none }` — see the five in `index.html`.
  This shipped once and was caught in a screenshot, not by a test.
- **The font family is `Orbitron`, not `Orbitron ExtraBold`.** The ExtraBold
  face reports family `Orbitron` with style `ExtraBold`.
- **The font must be loaded before GTK starts.** Once Pango has built its font
  map, a font added later is ignored and the wordmark silently falls back.
  `load_app_font()` is called from `main()` for that reason, not from
  `activate()`.
- **`cairo_show_text` leaves a current point**, so the next `cairo_line_to`
  draws a stray line from wherever the text ended. `bricks.inc` calls
  `cairo_new_path()` after text for that reason.
- **Check the remote before pushing.** Never force-push a branch without
  looking at what is on it; a blind force here nearly destroyed three commits
  of unrelated work. Tags do not travel in `git pull <bundle> main`.

## Things not to do

- Do not reproduce the LEGO or MINDSTORMS wordmark, or official LEGO product
  renders. The app uses its own icon and bricks drawn in Cairo from scratch.
- [NXT-Scratch](https://github.com/a10036gt/NXT-Scratch) was used only as a
  reference for which blocks an NXT editor needs. It is freeware with all
  rights reserved: do not copy its code or its strings.
