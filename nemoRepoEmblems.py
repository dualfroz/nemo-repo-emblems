#!/usr/bin/python3
import importlib.util
import os
import sys


def _ensureCoreOnPath():
    if importlib.util.find_spec("nemoRepoCore") is not None:
        return
    dataHome = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    dataDirs = (os.environ.get("XDG_DATA_DIRS") or "/usr/local/share:/usr/share").split(":")
    for base in [dataHome] + dataDirs:
        candidate = os.path.join(base, "nemo-repo-core")
        if os.path.isdir(os.path.join(candidate, "nemoRepoCore")):
            sys.path.insert(0, candidate)
            return


_ensureCoreOnPath()

import gi

gi.require_version("Nemo", "3.0")
from gi.repository import GObject, Nemo

from nemoRepoCore import (coreConfig, findRepoRoot, hasMarkerDirectory,
                          localDirectoryPath, pluginLogger, repoCache,
                          requireCore)

requireCore("0.1.0")

logger = pluginLogger("emblems")

gitIndicators = ("git_repo", "uncommitted_changes", "unpushed_commits")

pluginDefaults = {
    "indicators": {
        "git_repo": {
            "enabled": True,
            "emblem": "emblem-repo-git",
            "description": "Folder contains a .git directory (or worktree file)",
        },
        "claude_dir": {
            "enabled": True,
            "emblem": "emblem-repo-claude",
            "marker_directory": ".claude",
            "description": "Folder contains a .claude directory",
        },
        "uncommitted_changes": {
            "enabled": True,
            "emblem": "emblem-repo-dirty",
            "description": "git status shows staged, unstaged or untracked changes",
        },
        "unpushed_commits": {
            "enabled": True,
            "emblem": "emblem-repo-unpushed",
            "description": "Branch is ahead of its upstream, or has no upstream",
        },
    },
}

coreConfig.registerDefaults(pluginDefaults)


def _enabledIndicators():
    active = {}
    for key, entry in coreConfig.section("indicators").items():
        if not isinstance(entry, dict) or not entry.get("enabled"):
            continue
        if entry.get("emblem"):
            active[key] = entry
    return active


def _markerMatches(path, entry):
    markerDirectory = entry.get("marker_directory")
    if markerDirectory and hasMarkerDirectory(path, markerDirectory):
        return True
    markerFile = entry.get("marker_file")
    return bool(markerFile) and os.path.isfile(os.path.join(path, markerFile))


class RepoEmblemProvider(GObject.GObject, Nemo.InfoProvider,
                         Nemo.NameAndDescProvider):

    def update_file_info(self, file):
        path = localDirectoryPath(file)
        if path is None:
            return

        active = _enabledIndicators()
        for key, entry in active.items():
            if key not in gitIndicators and _markerMatches(path, entry):
                file.add_emblem(entry["emblem"])

        repoRoot = findRepoRoot(path)
        if repoRoot is None:
            return

        if "git_repo" in active:
            file.add_emblem(active["git_repo"]["emblem"])

        wantsDirty = "uncommitted_changes" in active
        wantsUnpushed = "unpushed_commits" in active
        if not (wantsDirty or wantsUnpushed):
            return

        repoCache.registerFileObject(repoRoot, file)
        info = repoCache.get(repoRoot)
        if info.error:
            return

        if wantsDirty and info.dirty:
            file.add_emblem(active["uncommitted_changes"]["emblem"])
        if wantsUnpushed and info.unpushed:
            file.add_emblem(active["unpushed_commits"]["emblem"])

    def get_name_and_desc(self):
        return ["nemo-repo-emblems:::Emblem overlays for git repositories "
                "and marker directories"]
