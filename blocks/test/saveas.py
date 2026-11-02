#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Save as must never hand nqc or nbc a file they cannot read.

Whatever the user types, the extension is the language's. Both routes are
exercised: the browser's own file picker, and the in-page sheet used where
there is no picker.
"""

import os
import subprocess
import tempfile

from playwright.sync_api import sync_playwright

import paths

PAGE = paths.PAGE
WORK = tempfile.mkdtemp(prefix="saveas-")

TYPED = [
    ("robot", "robot"),
    ("robot.txt", "robot"),
    ("robot.nqc", "robot"),
    ("robot.nxc", "robot"),
    ("  spaced  ", "spaced"),
    ("", "program"),
]

# Replaces the real picker so the headless run can see what we asked for
# and what we wrote, without a dialog nobody can click.
FAKE_PICKER = """
window.__picked = null;
window.__written = null;
window.showSaveFilePicker = function (opts) {
  window.__picked = opts;
  return Promise.resolve({
    name: opts.suggestedName,
    createWritable: function () {
      return Promise.resolve({
        write: function (t) { window.__written = t; return Promise.resolve(); },
        close: function () { return Promise.resolve(); }
      });
    }
  });
};
true;
"""


def main():
    bad = 0
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        ctx = br.new_context(accept_downloads=True)
        page = ctx.new_page()
        page.on("pageerror", lambda e: print("PAGEERROR", str(e)[:200]))
        page.goto(PAGE)
        page.wait_for_function("window.__ready === true")
        page.wait_for_timeout(250)

        # ---------------- the picker route ----------------
        page.evaluate(FAKE_PICKER)
        for mode, ext in (("nqc", ".nqc"), ("nxc", ".nxc")):
            page.click("#mNxc" if mode == "nxc" else "#mNqc")
            page.wait_for_function("window.__mode() === '%s'" % mode)
            page.wait_for_timeout(150)
            page.evaluate("window.__setName('line_follower')")
            page.evaluate("window.__saveAs(); true")  # no esperar la promesa
            page.wait_for_function("window.__written !== null", timeout=4000)
            opts = page.evaluate("window.__picked")
            written = page.evaluate("window.__written")
            want = "line_follower" + ext
            ok = opts["suggestedName"] == want
            print("%s  picker suggests %-20s %s"
                  % (mode.upper(), opts["suggestedName"],
                     "OK" if ok else "FAIL, wanted " + want))
            if not ok:
                bad += 1
            accepts = list(opts["types"][0]["accept"].values())[0]
            if accepts != [ext]:
                print("%s  picker accept   FAIL  %s" % (mode.upper(), accepts))
                bad += 1
            if not opts.get("excludeAcceptAllOption"):
                print("%s  picker          FAIL  'All files' still offered"
                      % mode.upper())
                bad += 1
            if "task main()" not in written:
                print("%s  content         FAIL  nothing useful written" % mode.upper())
                bad += 1
            page.evaluate("window.__written = null")

        # plain Save after a Save as writes back without asking again
        page.evaluate("window.__written = null; window.__picked = null")
        page.click("#btnMenu"); page.wait_for_timeout(150)
        page.click("#miSave"); page.wait_for_timeout(400)
        again = page.evaluate("window.__picked")
        wrote = page.evaluate("window.__written")
        if again is None and wrote:
            print("resave    OK    wrote back to the same file, no dialog")
        else:
            print("resave    FAIL  picked=%s wrote=%s" % (bool(again), bool(wrote)))
            bad += 1

        # ---------------- the fallback sheet ----------------
        page.goto(PAGE)
        page.wait_for_function("window.__ready === true")
        page.evaluate("delete window.showSaveFilePicker")
        page.wait_for_timeout(200)

        for mode, ext in (("nqc", ".nqc"), ("nxc", ".nxc")):
            # Chromium starts blocking automatic downloads after about ten
            # from one page, so each group gets a fresh one. Browser guard,
            # not anything the editor does.
            page.goto(PAGE)
            page.wait_for_function("window.__ready === true")
            page.evaluate("delete window.showSaveFilePicker; true")
            page.click("#mNxc" if mode == "nxc" else "#mNqc")
            page.wait_for_function("window.__mode() === '%s'" % mode)
            page.wait_for_timeout(150)
            for typed, want_base in TYPED:
                page.evaluate("window.__saveAs(); true")  # no esperar la promesa
                page.wait_for_selector("#nameModal:not([hidden])", timeout=4000)
                page.fill("#nameIn", typed)
                with page.expect_download() as dl:
                    page.click("#nameOk")
                name = dl.value.suggested_filename
                want = want_base + ext
                ok = name == want
                if not ok:
                    bad += 1
                print("%s  typed %-11r -> %-15s %s"
                      % (mode.upper(), typed, name,
                         "OK" if ok else "FAIL, wanted " + want))

        page.click("#mNqc")
        page.wait_for_function("window.__mode() === 'nqc'")
        page.evaluate("window.__saveAs(); true")  # no esperar la promesa
        page.wait_for_selector("#nameModal:not([hidden])")
        note = page.inner_text("#nameExt")
        if ".nqc" not in note:
            print("note      FAIL  the sheet does not name the extension")
            bad += 1
        else:
            print("note      OK    %r" % note)
        page.click("#nameCancel")
        page.wait_for_timeout(200)
        if page.is_visible("#nameModal"):
            print("cancel    FAIL  the sheet stayed open")
            bad += 1
        else:
            print("cancel    OK    closed, nothing saved")

        # the name survives a language change, the extension does not
        page.evaluate("window.__setName('line_follower')")
        page.click("#mNxc")
        page.wait_for_function("window.__mode() === 'nxc'")
        page.wait_for_timeout(150)
        full = page.evaluate("window.__fullName()")
        print("switch    %s  %s" % (full, "OK" if full == "line_follower.nxc" else "FAIL"))
        if full != "line_follower.nxc":
            bad += 1

        # and a saved file still compiles
        page.click("#mNqc")
        page.wait_for_function("window.__mode() === 'nqc'")
        page.wait_for_timeout(150)
        page.evaluate("window.__saveAs(); true")  # no esperar la promesa
        page.wait_for_selector("#nameModal:not([hidden])")
        page.fill("#nameIn", "from_blocks.wrong")
        with page.expect_download() as dl:
            page.click("#nameOk")
        d = dl.value
        path = os.path.join(WORK, d.suggested_filename)
        d.save_as(path)
        out = path + ".rcx"
        subprocess.run([paths.compiler("nqc"), "-TRCX2", "-O" + out, path],
                       capture_output=True, cwd=WORK)
        if os.path.exists(out):
            print("compile   OK    %s -> %d bytes"
                  % (d.suggested_filename, os.path.getsize(out)))
        else:
            print("compile   FAIL  nqc refused the saved file")
            bad += 1

        br.close()

    print("\nFAILURES: %d" % bad)
    raise SystemExit(1 if bad else 0)


main()
