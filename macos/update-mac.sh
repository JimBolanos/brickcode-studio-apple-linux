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

if [ ! -d "$REPO/.git" ]; then
  # Most people arrive here from a release zip, where there is nothing to
  # pull. Saying only "not a git clone" leaves them stuck holding the thing
  # they are trying to install.
  echo "This is not a git clone: $REPO"
  echo
  echo "update-mac.sh pulls, so it needs one. If you downloaded a release"
  echo "zip, there is nothing to pull — install what is already here:"
  echo
  echo "    bash macos/install-mac.sh"
  echo
  echo "To follow the project with git instead:"
  echo
  echo "    git clone https://github.com/JimBolanos/brickcode-studio-osx-linux.git"
  echo "    cd brickcode-studio-osx-linux && bash macos/update-mac.sh"
  exit 1
fi

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
