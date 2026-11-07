#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A pinned copy must come up in one language with the switch gone.

The whole point of the pin is that it survives a host that cannot pass a URL
fragment, so the pinned page is opened here with a bare path and nothing
after the "#". The Windows edition depends on this: it opens the editor
through ShellExecute, which resolves a file: URL to a plain path before the
browser sees it and loses the fragment on the way.

The copy is built here by pin.py rather than read out of the Windows
package, so this runs with only this repo present.
"""

import os
import subprocess
import sys
import tempfile

from playwright.sync_api import sync_playwright

import paths

WORK = tempfile.mkdtemp(prefix="pin-")
GENERIC = paths.PAGE

bad = 0


def check(label, got, want):
    global bad
    ok = got == want
    if not ok:
        bad += 1
    print("%-34s %-22r %s"
          % (label, got, "OK" if ok else "FAIL, wanted %r" % want))


def pinned_copy(which="nqc-only"):
    """Build a pinned page with pin.py, the way the Windows package is made."""
    dest = os.path.join(WORK, "pinned-%s.html" % which)
    r = subprocess.run([sys.executable, os.path.join(paths.BLOCKS, "pin.py"),
                        which, dest],
                       capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(dest):
        raise SystemExit("pin.py fallo: " + (r.stderr or r.stdout))
    return "file://" + dest


with sync_playwright() as pw:
    br = pw.chromium.launch()
    ctx = br.new_context(accept_downloads=True)
    page = ctx.new_page()
    page.on("pageerror", lambda e: print("PAGEERROR", str(e)[:200]))

    PINNED = pinned_copy("nqc-only")

    # ---------------- the pinned copy, opened with no fragment --------------
    print("--- copia pineada, abierta sin fragmento ---")
    page.goto(PINNED)
    page.wait_for_function("window.__ready === true")
    page.wait_for_timeout(250)

    check("modo", page.evaluate("window.__mode()"), "nqc")
    check("bloqueado", page.evaluate("window.__locked()"), True)
    check("conmutador oculto", page.is_hidden("#seg"), True)
    check("etiqueta", page.inner_text("#tag"), "for the RCX / Scout")
    check("extension en el boton", ".nqc" in page.get_attribute("#miSave", "title"), True)

    # the NXC button must be unreachable, not merely invisible
    check("boton NXC no clickeable", page.is_visible("#mNxc"), False)

    # and a program saved from it still compiles. The in-page sheet is used
    # rather than the browser's own picker, which no one can click here.
    page.evaluate("delete window.showSaveFilePicker; true")
    page.evaluate("window.__saveAs(); true")
    page.wait_for_selector("#nameModal:not([hidden])", timeout=4000)
    page.fill("#nameIn", "desde_bloques")
    with page.expect_download() as dl:
        page.click("#nameOk")
    d = dl.value
    path = os.path.join(WORK, d.suggested_filename)
    d.save_as(path)
    check("nombre guardado", d.suggested_filename, "desde_bloques.nqc")
    out = path + ".rcx"
    subprocess.run([paths.compiler("nqc"), "-TRCX2", "-O" + out, path],
                   capture_output=True, cwd=WORK)
    if os.path.exists(out):
        print("%-34s %d bytes               OK"
              % ("compila con nqc", os.path.getsize(out)))
    else:
        print("%-34s %s" % ("compila con nqc", "FAIL"))
        bad += 1

    # a fragment asking for the other language must not override the pin
    print("--- y el fragmento no puede ganarle al pin ---")
    page.goto(PINNED + "#nxc")
    page.wait_for_function("window.__ready === true")
    page.wait_for_timeout(250)
    check("modo con #nxc pegado", page.evaluate("window.__mode()"), "nqc")
    check("sigue bloqueado", page.evaluate("window.__locked()"), True)

    # the other direction, so the pin is not just hard-coded to NQC
    print("--- y pineada al otro idioma ---")
    page.goto(pinned_copy("nxc-only"))
    page.wait_for_function("window.__ready === true")
    page.wait_for_timeout(250)
    check("modo", page.evaluate("window.__mode()"), "nxc")
    check("conmutador oculto", page.is_hidden("#seg"), True)
    check("etiqueta", page.inner_text("#tag"), "for the NXT")

    # ---------------- the generic copy still obeys the hash -----------------
    print("--- copia generica, el hash sigue sirviendo ---")
    for frag, want_mode, want_locked, want_hidden in (
        ("", "nqc", False, False),
        ("#nxc", "nxc", False, False),
        ("#nqc-only", "nqc", True, True),
        ("#nxc-only", "nxc", True, True),
    ):
        # about:blank in between, because goto to the same document with only
        # a different fragment does not reload: it just fires hashchange, and
        # then this would be testing the listener, not a fresh load.
        page.goto("about:blank")
        page.goto(GENERIC + frag)
        page.wait_for_function("window.__ready === true")
        page.wait_for_timeout(200)
        label = frag or "(sin hash)"
        check("%-10s modo" % label, page.evaluate("window.__mode()"), want_mode)
        check("%-10s bloqueado" % label,
              page.evaluate("window.__locked()"), want_locked)
        check("%-10s conmutador oculto" % label,
              page.is_hidden("#seg"), want_hidden)

    # and the switch must also come and go when only the fragment changes on
    # a page that is already open, so locked() and the screen never disagree
    print("--- y sobre un documento ya abierto, solo el fragmento ---")
    page.goto("about:blank")
    page.goto(GENERIC)
    page.wait_for_function("window.__ready === true")
    page.goto(GENERIC + "#nxc-only")
    page.wait_for_timeout(250)
    check("tras hashchange modo", page.evaluate("window.__mode()"), "nxc")
    check("tras hashchange bloqueado", page.evaluate("window.__locked()"), True)
    check("tras hashchange oculto", page.is_hidden("#seg"), True)

    br.close()

print("\nFALLOS: %d" % bad)
raise SystemExit(1 if bad else 0)
