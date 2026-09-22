#!/usr/bin/env bash
set -euo pipefail

sourceDir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dataHome="${XDG_DATA_HOME:-$HOME/.local/share}"
extensionsDir="$dataHome/nemo-python/extensions"
target="$extensionsDir/nemoRepoEmblems.py"

if [ -e "$target" ] || [ -L "$target" ]; then
  rm -f "$target"
  echo "Removed $target"
else
  echo "Not installed: $target"
fi

rm -f "$extensionsDir/__pycache__/nemoRepoEmblems".*.pyc

iconDir="$dataHome/icons/hicolor/scalable/emblems"
for svg in "$sourceDir"/emblems/*.svg; do
  name="$(basename "$svg")"
  if [ -e "$iconDir/$name" ] || [ -L "$iconDir/$name" ]; then
    rm -f "$iconDir/$name"
    echo "Removed $iconDir/$name"
  fi
done

if command -v gtk-update-icon-cache >/dev/null 2>&1; then
  gtk-update-icon-cache -f -t "$dataHome/icons/hicolor" >/dev/null 2>&1 || true
fi

echo
echo "Restart Nemo to unload it:  nemo -q"
