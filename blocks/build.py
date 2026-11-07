#!/usr/bin/env python3
"""Build the single-file page: inline Blockly, the Spanish messages and the
icon sprite, so the result works offline from a file:// URL."""

import base64
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MEDIA = os.path.join(HERE, "sprites.svg")   # vendored, so this builds anywhere
OUT = os.path.join(HERE, "brickcode-blocks.html")


def read(name):
    with io.open(os.path.join(HERE, name), encoding="utf-8") as fh:
        return fh.read()


html = read("index.html")

# 1. the icon sprite as a data URI
with open(MEDIA, "rb") as fh:
    sprite = base64.b64encode(fh.read()).decode("ascii")
html = html.replace("__SPRITES_DATA_URI__", "data:image/svg+xml;base64," + sprite)

# 2. Blockly itself (and the Spanish messages, when the page asks for them)
for tag, name in (
    ('<script src="blockly.min.js"></script>', "blockly.min.js"),
    ('<script src="es.js"></script>', "es.js"),
):
    if tag not in html:
        continue
    js = read(name)
    if "</script" in js:
        raise SystemExit("cannot inline, the file closes the tag: " + name)
    html = html.replace(tag, "<script>\n" + js + "\n</script>")

with io.open(OUT, "w", encoding="utf-8") as fh:
    fh.write(html)

print("escrito", OUT, "-", round(os.path.getsize(OUT) / 1024), "KB")

# 3. one page per brick family, pinned to its language with the switch gone.
# The app opens the one that matches, by file name instead of a #fragment:
# macOS `open` drops everything after the "#", so the NXT button used to land
# on the RCX editor. Same pin as pin.py (the Windows edition uses that one).
for pin, name in (("nqc-only", "brickcode-blocks-rcx.html"),
                  ("nxc-only", "brickcode-blocks-nxt.html")):
    tag = '<html lang="en">'
    if tag not in html:
        raise SystemExit("no encuentro " + tag)
    dest = os.path.join(HERE, name)
    with io.open(dest, "w", encoding="utf-8") as fh:
        fh.write(html.replace(tag, '<html lang="en" data-pin="%s">' % pin, 1))
    print("escrito", dest, "-", pin)
