#!/usr/bin/env python3
"""Build the single-file page: inline Blockly, the Spanish messages and the
icon sprite, so the result works offline from a file:// URL."""

import base64
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
# Blockly and the icon sprite are the NQC/NXC editor's, not a second copy:
# two editors on two copies of Blockly would drift apart the first time one
# of them was upgraded.
SHARED = os.path.join(os.path.dirname(HERE), "blocks")
MEDIA = os.path.join(SHARED, "sprites.svg")
OUT = os.path.join(HERE, "pybricks-blocks.html")


def read(name):
    folder = SHARED if name == "blockly.min.js" else HERE
    with io.open(os.path.join(folder, name), encoding="utf-8") as fh:
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
