# roz

CLI tool to automate the three-stage downstream release process for Fedora/EPEL packages.

## Requirements

```
uv sync --locked --group dev   # Python deps
```

A valid **Kerberos ticket** (`fkinit -u <username>`) and a **Pagure API token** are required at runtime.

## Usage

```
roz propose --project goose --forge pagure
roz build   --project goose --forge pagure
roz update  --project goose --forge pagure
```

See [`docs/`](docs/) for full command documentation.

## Global flags

| Flag | Description |
|------|-------------|
| `-y` / `--yes` | Skip interactive diff prompts |
| `--keep` | Keep temporary worktrees after completion |
