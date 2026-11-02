#!/bin/bash
# Update an installed BrickCode Studio on macOS: pull, then rebuild and
# reinstall. Nothing is committed, pushed or tagged — publishing is a separate
# decision, and this script used to make it for you.
#
#   bash macos/update-mac.sh            quick: the app only
#   bash macos/update-mac.sh --full     also rebuild nqc and nbc
set -e

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/.." && pwd)"

[ -d "$REPO/.git" ] || { echo "Not a git clone: $REPO"; exit 1; }

cd "$REPO"

# Tracked files only. An untracked file cannot be lost by a fast-forward
# pull — git refuses the pull itself if one is in the way — so stopping for
# a venv or a stray screenshot would only be in the way.
if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
  echo "There are uncommitted changes to tracked files:"
  git status --short --untracked-files=no
  echo
  echo "Commit or stash them first. This pulls, and a pull on top of local"
  echo "edits is how work gets lost."
  exit 1
fi

echo "==> pulling"
git pull --ff-only

VER=$(sed -n 's/.*APP_VERSION *"\([^"]*\)".*/\1/p' brickcode-studio/brickcode-studio.c | head -1)
[ -n "$VER" ] || { echo "Cannot read APP_VERSION"; exit 1; }

echo "==> installing $VER"
bash "$HERE/install-mac.sh" "$@"

echo
echo "Installed $VER."
echo "To publish it as well, tag and release it yourself:"
echo "  git tag -a v$VER -m \"BrickCode Studio $VER\""
echo "  git push origin v$VER"
