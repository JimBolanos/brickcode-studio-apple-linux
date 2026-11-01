# Block editor

`brickcode-blocks.html` is a visual editor that writes NQC for the RCX and
Scout, or NXC for the NXT. It is one self-contained file: Blockly, the icons
and every style are inlined, so it works from `file://` with no network at
all. Open it on its own, or from **File → Block editor…** inside BrickCode
Studio.

The app passes `#nqc` or `#nxc` in the URL so the editor comes up on the same
language as the toolbar. Opening the file directly starts on NQC.

## Blocks ride inside the program

Blocks cannot be reconstructed from code — `OnFwd(OUT_AC, 75);` could have
come from any number of block arrangements, and most NQC in the wild has no
block equivalent at all. So **Save** writes the workspace into the file as a
trailing C comment, and **Open** reads it back:

```nqc
task main()
{
    OnFwd(OUT_A + OUT_C);
}

/* The blocks that made this program, for the BrickCode block
   editor. Edit the code by hand and this stops matching it;
   delete these four lines to keep the program alone.
   brickcode-blocks:1:PHhtbD4... */
```

A file saved here comes back with its blocks intact. Any other `.nqc` or
`.nxc` is shown as code, with the page saying plainly that the blocks are not
recoverable, rather than inventing an arrangement that was never there.

Both compilers ignore the comment: `nqc` and `nbc` produce byte-identical
output with and without it.

## The two languages are not the same

Two differences are easy to get wrong, and both are handled in the generator:

- **Motor pairs.** In NQC the output constants are a bit mask (`OUT_A` is 1,
  `OUT_C` is 4), so `OUT_A + OUT_C` really means both motors. In NXC they are
  an enumeration (`OUT_A` is 0, `OUT_C` is 2), so the same expression means
  `OUT_C` alone — it compiles perfectly and drives the wrong motor. The NXC
  side always writes the pair as one token, `OUT_AC`.
- **Definition order.** NXC needs a function defined before it is called;
  NQC does not care. My Blocks definitions are emitted above `task main` on
  the NXT side and below it on the RCX side.

Time units differ too: NQC counts in hundredths of a second, NXC in
milliseconds. Motor power is 0–7 on the RCX, so a percentage is scaled onto
those eight steps; on the NXT the percentage is passed through.

## Building it

`brickcode-blocks.html` is generated. `build.py` inlines `blockly.min.js` and
the Blockly sprite sheet into `index.html` to produce it.

Blockly 13.4.0, Apache 2.0.
