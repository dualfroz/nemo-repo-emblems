# nemo-repo-emblems

Emblem overlays for repository folders in [Nemo](https://github.com/linuxmint/nemo),
the Cinnamon file manager.

Open a directory full of checkouts and you can see, without opening any of
them, which folders are repositories, which have uncommitted work, and which
have commits that never left the machine.

Four indicators ship by default:

| Indicator | Emblem | Shown when |
| --- | --- | --- |
| `git_repo` | `emblem-repo-git` | The folder holds a `.git` directory or worktree file |
| `claude_dir` | `emblem-repo-claude` | The folder holds a `.claude` directory |
| `uncommitted_changes` | `emblem-repo-dirty` | `git status` reports staged, unstaged or untracked files |
| `unpushed_commits` | `emblem-repo-unpushed` | The branch is ahead of its upstream, or has no upstream at all |

Indicators are entries in a config file rather than hardcoded, so you can turn
any of them off, point them at different icons, or add your own.

Emblems refresh by themselves. The repository is watched, so committing or
pulling in a terminal updates the folder in Nemo without a restart and without
a reload.

## Requirements

- [nemo-repo-core](https://github.com/dualfroz/nemo-repo-core) 1.x
- Nemo with `nemo-python`, `git` in `PATH`

## Install

```bash
git clone https://github.com/dualfroz/nemo-repo-core
cd nemo-repo-core && ./install.sh && cd ..

git clone https://github.com/dualfroz/nemo-repo-emblems
cd nemo-repo-emblems && ./install.sh

nemo -q
```

`install.sh` links the plugin into `~/.local/share/nemo-python/extensions`, the
bundled SVGs into `~/.local/share/icons/hicolor/scalable/emblems`, refreshes
the icon cache, and checks that the plugin imports. Pass `--copy` to copy
instead of link. `./uninstall.sh` removes both the plugin and the icons.

Nothing is written outside your home directory and no root is required.

## Configuration

Shared file, read live, no restart needed:

```
~/.config/nemo-repo-core.json
```

```json
{
  "indicators": {
    "git_repo": { "enabled": true, "emblem": "emblem-repo-git" },
    "claude_dir": { "enabled": true, "emblem": "emblem-repo-claude", "marker_directory": ".claude" },
    "uncommitted_changes": { "enabled": true, "emblem": "emblem-repo-dirty" },
    "unpushed_commits": { "enabled": true, "emblem": "emblem-repo-unpushed" }
  }
}
```

Each entry takes:

| Field | Meaning |
| --- | --- |
| `enabled` | Draw this indicator at all |
| `emblem` | Icon name, from any installed icon theme |
| `marker_directory` | Draw it when the folder contains this subdirectory |
| `marker_file` | Draw it when the folder contains this file |

`git_repo`, `uncommitted_changes` and `unpushed_commits` are computed from git
and ignore the marker fields. Any other entry is a marker rule, which is how
`claude_dir` works, and how you add your own:

```json
{
  "indicators": {
    "node_project": { "enabled": true, "emblem": "emblem-important", "marker_file": "package.json" },
    "virtualenv":   { "enabled": true, "emblem": "emblem-symbolic-link", "marker_directory": ".venv" }
  }
}
```

Any icon name your theme provides works. `gtk3-icon-browser` lists them.

The one setting worth knowing about lives in the core:
`cache_ttl_seconds` (default 5) bounds how stale a dirty or unpushed emblem can
be when the change did not touch `.git`, for example a new untracked file.
Changes inside `.git` are picked up immediately regardless.

See `config.example.json` for a complete file.

## Notes

- Emblems are drawn on directories only, and only on local paths. Remote
  locations are skipped rather than queried over the network.
- Nemo has a limited number of emblem slots per icon and gives priority to
  emblems you set by hand, so with all four indicators on plus a manual emblem
  some may not be drawn.
- Only repository roots are marked, not every folder inside a checkout. That
  keeps a listing of a large source tree free of noise.

## Migrating from the single file version

This plugin used to be one file, `nemo_repo_emblems.py`, containing the
emblems, the columns, the properties tab and the context menu. It is now five
plugins on a shared core, so you can install just the parts you use.

Your config carries over: `~/.config/nemo-repo-emblems.json` is copied to
`~/.config/nemo-repo-core.json` on first run, with every key keeping its name.
The old file is not modified.

After installing the core and the plugins you want, remove the old extension so
things are not drawn twice:

```bash
rm ~/.local/share/nemo-python/extensions/nemo_repo_emblems.py
nemo -q
```

To go back, restore that file and remove the new plugins from the same
directory. Your old config file is untouched.

## Tested on

Linux Mint 22.2 (Zara), Cinnamon 6.4.14, Nemo 6.4.5, python-nemo 6.4.0,
Python 3.12.3.

## License

MIT. See `LICENSE`.
