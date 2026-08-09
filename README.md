# python-project-template

A batteries-included starter for an **AI-agent-driven Python command-line tool**.
Clone it, run one script to rename it, and you have a working CLI with tests,
linting, CI, and one-command paths to PyPI, uv, conda, and Docker.

Ships with `AGENTS.md` / `CLAUDE.md` and `.claude/skills/` so an AI agent knows
the project's conventions and how to extend it from the first prompt.

## What's inside

| Area        | Files |
|-------------|-------|
| Package     | `src/mytool/` — `cli.py` (thin Click wrapper) + `core.py` (logic) |
| Tests       | `tests/` — pytest + Click's `CliRunner` |
| Lint/format | `ruff` (config in `pyproject.toml`) |
| CI          | `.github/workflows/ci.yml` — ruff + pytest on 3.10–3.12 |
| Publish     | `.github/workflows/publish.yml` — PyPI trusted publishing on release |
| Packaging   | `pyproject.toml` (hatchling, `[project.scripts]` entry point) |
| Conda       | `environment.yml` (dev env) + `conda/meta.yaml` (recipe) |
| Docker      | `Dockerfile` (multi-stage) + `.dockerignore` |
| Automation  | `Makefile`, `scripts/init.py` |
| AI docs     | `AGENTS.md`, `CLAUDE.md`, `.claude/skills/` |

## Quickstart

```bash
# 1. Copy the template to your new project's home and enter it
cp -R python-project-template ~/Documents/work/01_active/my-cli && cd ~/Documents/work/01_active/my-cli

# 2. Rename all the placeholders ("mytool" -> "my_cli", slug -> "my-cli")
python scripts/init.py my-cli     # the script deletes itself when done

# 3. Set up the environment and verify (uv)
make setup        # uv venv + editable install with dev extras
make test         # pytest
make lint         # ruff

# 4. Run your CLI
my-cli hello Brian --shout        # -> HELLO, BRIAN!
python -m my_cli --help
```

No `uv`? Use plain pip: `python -m venv .venv && source .venv/bin/activate && make dev`.

## Developing

- Put real logic in `src/<pkg>/core.py`; keep `cli.py` a thin wrapper.
- Add a subcommand: see [`.claude/skills/add-command/SKILL.md`](.claude/skills/add-command/SKILL.md).
- `make help` lists every convenience target.

## Deploying

Full walkthrough in [`docs/deployment.md`](docs/deployment.md). Short version:

**PyPI** — bump the version, tag, and cut a GitHub Release; `publish.yml` builds
and uploads via trusted publishing (no stored token). Manual fallback:
```bash
make build && make publish        # uv build + twine upload
```

**uv** — build and publish, or install the published tool globally:
```bash
uv build && uv publish            # publish
uv tool install my-cli            # install the CLI on your PATH
uvx my-cli --help                 # run without installing
```

**conda** — dev env from `environment.yml`; build a package from `conda/meta.yaml`:
```bash
conda env create -f environment.yml && conda activate my-cli
conda build conda/ -c conda-forge
```

**Docker**:
```bash
make docker                       # build image
docker run --rm my-cli hello      # args go straight to the CLI
```

## License

MIT — see [LICENSE](LICENSE).
