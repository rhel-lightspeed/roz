# roz propose

Generates an SRPM from upstream, imports it into dist-git, and opens pull requests on the target forge.

## Usage

```
roz propose --project <project> --forge <forge> --version <version> [options]
```

## Arguments

| Flag | Required | Description |
|------|----------|-------------|
| `--project {goose}` | Yes | Package to release. |
| `--forge {pagure,gitlab}` | Yes | Target forge for PR creation. |
| `--branch BRANCH` | No | Limit to specific branch(es). Repeatable. Defaults to all forge branches. |
| `--offline` | No | Skip tarball upload to lookaside cache. |
| `--resolve TICKET` | No | Bug/ticket to close (e.g. `rhbz#12345`, `RSPEED-678`). Repeatable. Added as `Resolve:` commit trailers. |

## What it does

1. Clones the upstream repo and runs `make vendor-tarball`.
2. Builds a `.src.rpm` via `fedpkg srpm` and reads the version from it.
3. For each target branch:
   - Clones the dist-git repo.
   - Creates a `roz/<version>/<branch>` working branch.
   - Imports the SRPM with `fedpkg import`.
   - Commits and pushes to a personal fork (auto-created if absent).
   - Opens a PR against the dist-git project and prints its URL.

## Example

```
roz propose --project goose --forge pagure --branch f44 --branch epel10 --resolve rhbz#2300001
```

## Caveats

- **GitLab forge is not yet implemented.** `--forge gitlab` will fail with a `NotImplementedError` at the PR creation step.
- Requires a valid **Pagure API token** — set it via `keyring set roz pagure` or the `PAGURE_TOKEN` environment variable.
- Requires **SSH access** to push to forks.
- The `--offline` flag skips lookaside upload; useful for testing, not suitable for real releases.
