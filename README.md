# nemo-repo-emblems

nemo-repo-emblems is an extension for [Nemo](https://github.com/linuxmint/nemo),
the Cinnamon file manager, that draws emblem overlays on folders: whether a
folder is a git repository, whether it has uncommitted changes, whether it has
commits its upstream does not, and whether it contains a marker directory or
file you configured. Open a directory full of checkouts and the state of each
one is visible without opening it. It is a plugin for **nemo-repo-core** and
needs it installed.

## Features

- Four default indicators, each with its own bundled SVG emblem:

  | Indicator | Emblem | Shown when |
  | --- | --- | --- |
  | `git_repo` | `emblem-repo-git` | The folder holds `.git` as a directory or a file (worktree, submodule) |
  | `claude_dir` | `emblem-repo-claude` | The folder contains a `.claude` directory |
  | `uncommitted_changes` | `emblem-repo-dirty` | `git status` reports staged, unstaged or untracked files |
  | `unpushed_commits` | `emblem-repo-unpushed` | The branch is ahead of its upstream, or has no upstream |

- Indicators are config entries, not code: each one can be switched off,
  pointed at any icon name from an installed theme, and new marker rules can be
  added for any subdirectory or file name.
- Emblems update by themselves. A commit, checkout or fetch that changes `.git`
  re-draws the folder at once; other changes appear within
  `cache_ttl_seconds`.
- Config changes are picked up without restarting Nemo and show the next time
  Nemo redraws or reloads a folder.
- git is asked only when a dirty or unpushed indicator is enabled, and the
  result is shared with the other plugins through the core's cache.

## Requirements

- nemo-repo-core 0.1.x
- Nemo with `nemo-python`, `git` in `PATH`

## Install and run

Install nemo-repo-core first (run `./install.sh` in its checkout), then from a
checkout of this repository:

```bash
./install.sh
nemo -q
```

`install.sh` links `nemoRepoEmblems.py` into
`~/.local/share/nemo-python/extensions`, links the SVGs from `emblems/` into
`~/.local/share/icons/hicolor/scalable/emblems`, refreshes the icon cache when
`gtk-update-icon-cache` is available, and checks that the plugin imports. Pass
`--copy` to copy the files instead of linking them. It stops with a message if
nemo-repo-core is not installed. No root is required.

`./uninstall.sh` removes the plugin and the icons it installed.

## Configuration

Settings live in the shared file `~/.config/nemo-repo-core.json`.
`config.example.json` shows the `indicators` section with the four defaults and
two disabled example marker rules:

```json
{
  "indicators": {
    "git_repo": { "enabled": true, "emblem": "emblem-repo-git" },
    "claude_dir": { "enabled": true, "emblem": "emblem-repo-claude", "marker_directory": ".claude" },
    "uncommitted_changes": { "enabled": true, "emblem": "emblem-repo-dirty" },
    "unpushed_commits": { "enabled": true, "emblem": "emblem-repo-unpushed" },

    "node_project": { "enabled": false, "emblem": "emblem-important", "marker_file": "package.json" },
    "virtualenv": { "enabled": false, "emblem": "emblem-symbolic-link", "marker_directory": ".venv" }
  }
}
```

Each entry takes:

| Field | Meaning |
| --- | --- |
| `enabled` | Draw this indicator; entries without `"enabled": true` are skipped |
| `emblem` | Icon name from any installed icon theme; entries without one are skipped |
| `marker_directory` | Marker rules: draw when the folder directly contains this subdirectory |
| `marker_file` | Marker rules: draw when the folder directly contains this file |

`git_repo`, `uncommitted_changes` and `unpushed_commits` are computed from git
and ignore the marker fields. Every other key is a marker rule; `claude_dir` is
one, and the two disabled examples show how to add more. `gtk3-icon-browser`
lists the icon names your theme provides.

The core setting `cache_ttl_seconds` (default 5) bounds how stale the dirty and
unpushed emblems can be when a change did not touch `.git`, for example a new
untracked file.

## Tests

The tests use the standard library `unittest` and need PyGObject with the Nemo
typelib (`gir1.2-nemo-3.0`) and nemo-repo-core: an installed core, a checkout
of nemo-repo-core next to this one (`../nemo-repo-core`), or a path in
`NEMO_REPO_CORE_PATH`. Without the core the suite is skipped. Run them from the
repository root:

```bash
python3 -m unittest discover -s tests
```

They cover indicator selection from the config, marker directory and file
rules, the emblems drawn for plain folders, marker folders and real
repositories (clean, dirty, unpushed, broken, nested), that git is not queried
when no git state indicator is enabled, and that every default emblem ships an
SVG and matches `config.example.json`. Tests that need git create throwaway
repositories in a temporary directory and are skipped when `git` is not
installed. The shared config is redirected to a temporary file, so your real
config is never touched.

## Project layout

```
nemoRepoEmblems.py        the Nemo extension
emblems/                  emblem-repo-git, -dirty, -unpushed, -claude SVGs
config.example.json       indicators section with defaults and examples
install.sh, uninstall.sh  per-user install
tests/
  support.py              temporary config, git helpers and core lookup
  testEmblems.py          unittest suite
```

## Limitations

- Git indicators are drawn only on repository roots, not on every folder
  inside a checkout. Marker rules apply to any local folder.
- Only local directories are handled; remote locations are skipped.
- Nemo shows a limited number of emblems per icon and prefers emblems set by
  hand, so with many indicators active some may not be drawn.
- Worktrees and submodules (`.git` is a file) are refreshed only when the cache
  TTL expires, not immediately on change.

## License

MIT. See `LICENSE`.
