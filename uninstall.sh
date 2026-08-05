#!/usr/bin/env bash
# Removes this plugin from Nemo. The core, the other plugins and the config
# file are left alone.
set -euo pipefail

dataHome="${XDG_DATA_HOME:-$HOME/.local/share}"
extensionsDir="$dataHome/nemo-python/extensions"
target="$extensionsDir/nemoRepoEmblems.py"

if [ -e "$target" ]; then
  rm -f "$target"
  echo "Removed $target"
else
  echo "Not installed: $target"
fi

rm -f "$extensionsDir/__pycache__/nemoRepoEmblems".*.pyc

iconDir="$dataHome/icons/hicolor/scalable/emblems"
for name in emblem-repo-git emblem-repo-claude emblem-repo-dirty emblem-repo-unpushed; do
  if [ -e "$iconDir/$name.svg" ]; then
    rm -f "$iconDir/$name.svg"
    echo "Removed $iconDir/$name.svg"
  fi
done

if command -v gtk-update-icon-cache >/dev/null 2>&1; then
  gtk-update-icon-cache -f -t "$dataHome/icons/hicolor" >/dev/null 2>&1 || true
fi

echo
echo "Restart Nemo to unload it:  nemo -q"
