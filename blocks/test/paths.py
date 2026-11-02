#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Where things are, worked out from this file instead of hard-coded.

The suite used to carry absolute paths from the machine it was written on,
which made it unrunnable anywhere else. Everything is now found relative to
this file, and the two compilers are looked up on PATH.
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
BLOCKS = os.path.dirname(HERE)                       # the blocks/ folder

PAGE_FILE = os.path.join(BLOCKS, "brickcode-blocks.html")
PAGE = "file://" + PAGE_FILE


def page(fragment=""):
    """The editor's URL, with a fragment when a test wants one."""
    return PAGE + fragment


def shot(name):
    """Screenshots go in blocks/shots/, not loose beside the source."""
    d = os.path.join(BLOCKS, "shots")
    if not os.path.isdir(d):
        os.makedirs(d)
    return os.path.join(d, name)


def compiler(name):
    """nqc or nbc: from NQC= / NBC= in the environment, else from PATH.

    A test that cannot find its compiler says so and stops, rather than
    failing later with something that looks like a bug in the editor.
    """
    env = os.environ.get(name.upper())
    if env:
        if not os.path.exists(env):
            raise SystemExit("%s=%s no existe" % (name.upper(), env))
        return env
    found = shutil.which(name)
    if not found:
        raise SystemExit(
            "no encuentro '%s'. Instalalo, ponelo en el PATH, "
            "o corre la prueba con %s=/ruta/a/%s"
            % (name, name.upper(), name))
    return found
