#!/bin/bash
# BrickCode Studio - Arch / Omarchy installer.
# Builds nqc, nbc (compile-only) and the app from source into ~/.local/brickcode.
# Only the pacman packages and the optional udev rule need sudo.
set -e

PREFIX="$HOME/.local/brickcode"
SRC="$(cd "$(dirname "$0")/.." && pwd)/brickcode-studio"
FW="$(cd "$(dirname "$0")/.." && pwd)/firmware"
WORK="$HOME/.cache/brickcode-build"
mkdir -p "$PREFIX/bin" "$PREFIX/share/brickcode/nbc" "$PREFIX/share/firmware" "$WORK"
[ -f "$SRC/brickcode-studio.c" ] || { echo "Cannot find $SRC/brickcode-studio.c"; exit 1; }

echo "==> 1/5 Packages (sudo password needed)"
sudo pacman -S --needed --noconfirm base-devel git gtk4 libusb fontconfig pkgconf fpc bison flex perl

# Everything after the packages is the same on every distribution.
. "$(cd "$(dirname "$0")" && pwd)/_build.sh"
