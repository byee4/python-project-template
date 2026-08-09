# python-project-template

A batteries-included starter for an **AI-agent-driven Python command-line tool**.
Copy it, run one command to rename it, and you have a working CLI with tests,
linting, CI, and one-command paths to **PyPI, uv, conda, and Docker** — plus the
`AGENTS.md` / `CLAUDE.md` / `.claude/skills/` docs an AI agent needs to extend it
correctly from the first prompt.

> New here? Jump to [Quickstart](#quickstart). Want to know what every file does?
> See [Component reference](#component-reference).

---

## Quickstart

### Option A — Devboard (one click)

In Devboard's **Quick Start** panel, click **Python CLI tool**, enter a name, and
(optionally) tick *Create GitHub repo*. Devboard runs the generator below for you
and drops a ready-to-develop project into `01_active/`. See
[Devboard integration](#devboard-integration).

### Option B — the generator script

Creates a new, renamed, git-initialized project **without touching the template**:

```bash
cd ~/Documents/work/03_templates/python-project-template
python3 scripts/create_project.py ~/Documents/work/01_active/my-cli \
    --slug my-cli --name "My CLI"
# add --github byee4/my-cli to also create and push a GitHub repo
```

Then:

```bash
cd ~/Documents/work/01_active/my-cli
make setup      # uv venv + editable install with dev extras
make test       # pytest
my-cli hello Brian --shout      # -> HELLO, BRIAN!
```

### Option C — copy + rename in place

For when you've already copied the folder and just want to rename it:

```bash
cp -R python-project-template my-cli && cd my-cli
python scripts/init.py my-cli   # rewrites placeholders, then deletes itself
make setup && make test
```

No `uv`? Use plain pip: `python -m venv .venv && source .venv/bin/activate && make dev`.

---

## What you get

| Concern | How it's handled |
|---------|------------------|
| Package layout | `src/` layout — import-safe, no accidental local imports |
| CLI framework | [Click](https://click.palletsprojects.com/) group + subcommands |
| Logic/CLI split | `core.py` (pure, tested) vs `cli.py` (thin wrapper) |
| Tests | `pytest` + Click's `CliRunner` |
| Lint/format | `ruff` (config in `pyproject.toml`) |
| CI | GitHub Actions: ruff + pytest on Python 3.10–3.12 |
| Publish to PyPI | GitHub Actions **trusted publishing** on release (no stored token) |
| Build backend | `hatchling` |
| Distribution | PyPI · uv · conda · Docker |
| AI-agent docs | `AGENTS.md`, `CLAUDE.md`, `.claude/skills/` |
| Scaffolding | `scripts/create_project.py`, `scripts/init.py`, `Makefile` |

---

## Component reference

Every file and folder, what it is, and how to use it.

### Package — `src/mytool/`

`src/`-layout package. The name `mytool` is a placeholder the rename step
rewrites to your package name.

- **`core.py`** — the real logic, kept pure and I/O-free so it's easy to unit
  test and reuse. **Add new behavior here first.** Ships with a `greet()`
  placeholder to demonstrate the pattern.
- **`cli.py`** — the Click command-line interface. `cli` is the top-level group;
  each subcommand is a thin function that parses arguments, calls into `core`,
  and prints. `main()` is the console entry point referenced by `pyproject.toml`.
- **`__main__.py`** — enables `python -m mytool`.
- **`__init__.py`** — holds `__version__`, the single source of truth for the
  package version (keep it in sync with `pyproject.toml`).

**Golden rule:** keep `cli.py` thin, put logic in `core.py`. The
[`add-command`](.claude/skills/add-command/SKILL.md) skill walks through it.

### Tests — `tests/`

- **`test_core.py`** — exercises `core` functions directly.
- **`test_cli.py`** — exercises commands through `click.testing.CliRunner`, so
  you test the real argument parsing and output.

Run with `make test` (or `pytest`). CI runs these on every push and PR.

### Packaging & tooling config — `pyproject.toml`

The single config file for the whole project:

- `[project]` — name, version, dependencies, Python floor, metadata.
- `[project.scripts]` — `mytool = "mytool.cli:main"`. This is what turns your
  package into a `mytool` command on `PATH` when installed (PyPI, uv, pipx, conda).
- `[project.optional-dependencies].dev` — dev tools (`pytest`, `ruff`, `build`,
  `twine`), installed by `make setup` / `make dev`.
- `[build-system]` — `hatchling` build backend.
- `[tool.ruff]` / `[tool.pytest.ini_options]` — lint and test configuration.

### AI-agent documentation

- **`AGENTS.md`** — operating instructions for AI agents *and* humans: project
  shape, the core/CLI split rule, branch/commit conventions, and a
  "before reporting done" checklist. The provider-neutral source of truth.
- **`CLAUDE.md`** — one line pointing Claude at `AGENTS.md` (so both tools read
  the same rules).
- **`.claude/skills/`** — task-scoped runbooks an agent auto-loads when relevant:
  - **`add-command/SKILL.md`** — how to add a new CLI subcommand the right way
    (logic in `core.py`, thin command, tests, docs).
  - **`release/SKILL.md`** — how to cut a versioned release and publish to PyPI.

### Docs — `docs/`

- **`codemap.md`** — a one-screen orientation to where things live. Update it when
  you add/remove a module or change a public surface.
- **`deployment.md`** — the full walkthrough for PyPI, uv, conda, and Docker
  (see [Deploying](#deploying)).
- **`specs/`** — drop dated design specs here (`YYYY-MM-DD-<topic>.md`) for
  non-trivial features.

### Deployment artifacts

- **`Dockerfile`** — multi-stage build: stage one builds a wheel, stage two
  installs it into a slim runtime image whose `ENTRYPOINT` is your CLI, so
  `docker run <image> <args>` runs the tool.
- **`.dockerignore`** — keeps the build context small and clean.
- **`environment.yml`** — a conda **dev environment** definition.
- **`conda/meta.yaml`** — a `conda-build` **recipe** to package the tool for a
  conda channel.

### CI/CD — `.github/workflows/`

- **`ci.yml`** — runs `ruff` + `pytest` across Python 3.10/3.11/3.12 on every
  push to `main` and every PR.
- **`publish.yml`** — on a published GitHub Release, builds and uploads to PyPI
  via **trusted publishing** (OIDC — no API token stored in the repo). One-time
  setup is in `docs/deployment.md`.

### Automation & scaffolding

- **`Makefile`** — convenience targets; run `make help` to list them
  (`setup`, `dev`, `test`, `lint`, `fmt`, `build`, `docker`, `publish`, …).
- **`scripts/create_project.py`** — non-interactive generator that stamps out a
  new project *to a new location* and leaves the template untouched. Used by both
  the CLI and Devboard's one-click button. Flags: `--slug`, `--name`,
  `--github OWNER/REPO`, `--visibility`, `--skip-sync`, `--skip-index`.
- **`scripts/init.py`** — renames the template **in place** (for when you copied
  the folder first), then deletes itself.

> Both generators leave a fresh project — they never carry over `.git`, caches,
> or the generator scripts themselves.

### Project metadata

- **`LICENSE`** — MIT (edit the holder/year as needed).
- **`.python-version`** — default interpreter for `uv` / `pyenv` (3.12).
- **`.gitignore`** — Python, venv, build, cache, and secret-file ignores.
- **`.env.example`** — copy to `.env` (gitignored) for local settings; document
  every new env var here.

---

## Developing

- Put real logic in `src/<pkg>/core.py`; keep `cli.py` a thin wrapper.
- **Add a subcommand:** follow [`.claude/skills/add-command`](.claude/skills/add-command/SKILL.md).
- `make help` lists every target. Typical loop: `make fmt && make test`.

---

## Deploying

Full walkthrough: [`docs/deployment.md`](docs/deployment.md). Short version:

**PyPI** — bump the version, tag, and publish a GitHub Release; `publish.yml`
builds and uploads via trusted publishing. Manual fallback:
```bash
make build && make publish        # uv build + twine upload
```

**uv**:
```bash
uv build && uv publish            # publish to PyPI
uv tool install my-cli            # install the CLI on your PATH
uvx my-cli --help                 # run it without installing
```

**conda**:
```bash
conda env create -f environment.yml && conda activate my-cli   # dev env
conda build conda/ -c conda-forge                              # build a package
```

**Docker**:
```bash
make docker                       # build image
docker run --rm my-cli hello      # args pass straight to the CLI
```

---

## Devboard integration

This template plugs into Devboard's **Quick Start** feature, so a new CLI project
is one click. The button is defined in `05_shared_tools/devboard/config.json`
under `quick_start.types`:

```json
{
  "id": "python-cli",
  "label": "Python CLI tool",
  "template": "03_templates/python-project-template",
  "generator": "scripts/create_project.py",
  "runner": "python3",
  "args": ["{target}", "--slug", "{slug}", "--name", "{name}",
           "--skip-sync", "--skip-index", "--skip-beads"],
  "supports_github": true,
  "github_args": ["--github", "{owner}/{slug}", "--visibility", "private"],
  "post_setup": "make setup"
}
```

Devboard substitutes `{target}` / `{slug}` / `{name}` / `{owner}`, runs the
generator (create-only — it never deploys), and shows `make setup` as the next
step. This mirrors the existing **Django web app** button exactly. Restart
Devboard's server after editing `config.json` to pick up the new button.

---

## License

MIT — see [LICENSE](LICENSE).
