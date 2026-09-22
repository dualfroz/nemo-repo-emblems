#!/usr/bin/env bash
set -euo pipefail

sourceDir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dataHome="${XDG_DATA_HOME:-$HOME/.local/share}"
extensionsDir="$dataHome/nemo-python/extensions"
coreDir="$dataHome/nemo-repo-core"
pluginFile="nemoRepoEmblems.py"

mode="link"
if [ "${1:-}" = "--copy" ]; then
  mode="copy"
elif [ -n "${1:-}" ]; then
  echo "usage: $0 [--copy]" >&2
  exit 2
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required but was not found in PATH" >&2
  exit 1
fi

if [ ! -d "$coreDir/nemoRepoCore" ] && ! python3 -c "import nemoRepoCore" >/dev/null 2>&1; then
  echo "nemo-repo-core is not installed. Install it first by running" >&2
  echo "install.sh from a checkout of nemo-repo-core, then run this script again." >&2
  exit 1
fi

mkdir -p "$extensionsDir"
target="$extensionsDir/$pluginFile"
rm -f "$target"
if [ "$mode" = "copy" ]; then
  cp "$sourceDir/$pluginFile" "$target"
  echo "Copied plugin -> $target"
else
  ln -s "$sourceDir/$pluginFile" "$target"
  echo "Linked plugin -> $target"
fi

iconDir="$dataHome/icons/hicolor/scalable/emblems"
mkdir -p "$iconDir"
for svg in "$sourceDir"/emblems/*.svg; do
  name="$(basename "$svg")"
  rm -f "$iconDir/$name"
  if [ "$mode" = "copy" ]; then
    cp "$svg" "$iconDir/$name"
  else
    ln -s "$svg" "$iconDir/$name"
  fi
done
echo "Installed emblem icons -> $iconDir"

if command -v gtk-update-icon-cache >/dev/null 2>&1; then
  gtk-update-icon-cache -f -t "$dataHome/icons/hicolor" >/dev/null 2>&1 || true
fi

if ! PYTHONPATH="$coreDir:$extensionsDir" python3 -c "import nemoRepoEmblems" >/dev/null 2>&1; then
  echo >&2
  echo "The plugin did not import cleanly:" >&2
  PYTHONPATH="$coreDir:$extensionsDir" python3 -c "import nemoRepoEmblems" >&2 || true
  exit 1
fi
echo "Import check passed."

echo
echo "Restart Nemo to load the plugin:  nemo -q"
