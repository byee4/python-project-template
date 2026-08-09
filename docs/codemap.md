# Codemap

A quick orientation to where things live. Update this when you add or remove a
module or change a public surface.

## Runtime

- `src/mytool/core.py` — pure logic. No I/O beyond return values. Unit-tested
  directly. **Add new behavior here first.**
- `src/mytool/cli.py` — Click CLI. `cli` is the `@click.group`; each subcommand
  is a thin wrapper that parses args, calls into `core`, and prints. `main()` is
  the console-script entry point referenced by `[project.scripts]`.
- `src/mytool/__main__.py` — makes `python -m mytool` work.
- `src/mytool/__init__.py` — holds `__version__` (single source of truth for the
  package version; keep it in sync with `pyproject.toml`).

## Tests

- `tests/test_core.py` — exercises `core` functions directly.
- `tests/test_cli.py` — exercises commands via `click.testing.CliRunner`.

## Packaging & deploy

- `pyproject.toml` — metadata, dependencies, entry point, ruff + pytest config.
- `.github/workflows/ci.yml` — lint + test matrix.
- `.github/workflows/publish.yml` — PyPI on GitHub Release (trusted publishing).
- `Dockerfile`, `conda/meta.yaml`, `environment.yml` — see `deployment.md`.

## Conventions

- Keep `cli.py` thin; logic goes in `core.py`.
- Bump `__version__` and `pyproject.toml` `version` together on release.
- Document new env vars in `.env.example`.
