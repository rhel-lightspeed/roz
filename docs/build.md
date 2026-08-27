# roz build

Submits Koji builds for each target dist-git branch.

## Usage

```
roz build --project <project> --forge <forge> [options]
```

## Arguments

| Flag | Required | Description |
|------|----------|-------------|
| `--project {goose}` | Yes | Package to build. |
| `--forge {pagure,gitlab}` | Yes | Forge whose dist-git to clone. |
| `--branch BRANCH` | No | Limit to specific branch(es). Repeatable. Defaults to all forge branches. |
| `--scratch-build` | No | Run a scratch build before the real build. |
| `--arches ARCH [ARCH ...]` | No | Architectures for the scratch build (`x86_64`, `aarch64`, `ppc64le`, `s390x`). |

## What it does

1. Clones the dist-git repo.
2. For each branch:
   - Checks out the branch.
   - Optionally runs `fedpkg scratch-build --nowait` and prints the Koji task URL.
   - Runs `fedpkg build --nowait` and prints the Koji task URL.

## Example

```
roz build --project goose --forge pagure --branch f44 --scratch-build --arches x86_64 aarch64
```

## Caveats

- Requires a valid **Kerberos ticket**. Run `fkinit -u <username>` if authentication fails.
- `--arches` is only effective when combined with `--scratch-build`; it is silently ignored otherwise.
