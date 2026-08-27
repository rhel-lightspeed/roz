# roz update

Creates Bodhi updates for completed Koji builds.

## Usage

```
roz update --project <project> --forge <forge> [options]
```

## Arguments

| Flag | Required | Description |
|------|----------|-------------|
| `--project {goose}` | Yes | Package to update. |
| `--forge {pagure,gitlab}` | Yes | Forge (used for branch lookup). |
| `--type {enhancement,bugfix,security}` | No | Bodhi update type. Default: `enhancement`. |
| `--severity {unspecified,low,medium,high,urgent}` | No | Bodhi severity. Default: `low`. |
| `--resolve BUG_ID` | No | Bug IDs to associate with the update. Repeatable. |
| `--branch BRANCH` | No | Limit to specific branch(es). Repeatable. Defaults to all non-rawhide branches. |
| `--stable-karma KARMA` | No | Stable karma threshold. Default: `1`. Minimum: `1`. |

## What it does

1. Clones the Pagure dist-git (shallow clone).
2. For each branch, checks it out and runs `fedpkg update` using the `changelog` file at the dist-git root as update notes.
3. Prints confirmation for each submitted update.

## Example

```
roz update --project goose --forge pagure --type bugfix --resolve rhbz#2300001 --branch f44 --branch epel10
```

## Caveats

- **Rawhide is always rejected.** Passing `rawhide` via `--branch` is a fatal error; rawhide updates are composed automatically by Bodhi.
- The `--forge` flag does not affect the clone URL — the update flow always uses the Pagure dist-git regardless of the specified forge.
- A `changelog` file must exist at the root of each dist-git branch for the update notes. Missing this file will cause `fedpkg update` to fail.
- Requires a valid **Kerberos ticket**. Run `fkinit -u <username>` if authentication fails.
