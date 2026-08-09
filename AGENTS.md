# AGENTS.md — mytool

Operating instructions for AI agents (and humans) working in this project.
Adheres to the parent workspace's `~/Documents/work/CLAUDE.md` guidelines.

## Project shape

```
mytool/
  src/mytool/       Package. cli.py (thin Click wrapper) + core.py (real logic)
  tests/            pytest — test_core.py (logic) + test_cli.py (CliRunner)
  scripts/init.py   One-time rename of template placeholders (deletes itself)
  docs/             codemap.md, deployment.md, specs/
  .claude/skills/   add-command, release — task-scoped runbooks for agents
  .github/workflows/  ci.yml (test matrix), publish.yml (PyPI on release)
  Dockerfile        Multi-stage build → CLI entrypoint image
  conda/meta.yaml   conda-build recipe;  environment.yml is the dev env
  pyproject.toml    hatchling build, [project.scripts] entry point, ruff, pytest
```

## Core principle: keep the CLI thin

`cli.py` parses arguments and prints; `core.py` does the work and is pure and
testable. New behavior goes in `core.py` with a unit test, then gets a thin
Click command in `cli.py`. Don't put business logic in command callbacks.

## Before every change

1. **Read first.** Skim `docs/codemap.md`. Don't guess at structure.
2. **Branch.** `claude/<short-desc>` for AI work, `brian/<desc>` for features,
   `fix/<desc>` for bugs. Never commit to `main` directly.
3. **State your plan.** For multi-step work, write a numbered plan with verify
   steps before editing.

## While changing

- **Surgical edits.** Touch only what the task requires. Don't reformat adjacent
  code or "improve" unrelated bits.
- **No speculative abstractions.** Single-use code stays single-use until a
  second caller appears.
- **Match existing style.** Follow what's already there.
- **Bump `__version__`** in `src/mytool/__init__.py` and the `version` in
  `pyproject.toml` together when releasing (see `.claude/skills/release`).
- **Secrets stay in `.env`.** Never hard-code keys or tokens. Read from
  `os.environ`. `.env` is gitignored; document new vars in `.env.example`.

## Before reporting done

Every feature or bug fix MUST:

1. Have a test that would fail if the behavior regressed (`pytest`).
2. Pass `ruff check .`.
3. If it adds/changes a command, update `README.md` usage and `docs/codemap.md`.

## Commit conventions

- Subject: `<area>: <imperative summary>` (e.g. `cli: add convert command`).
- One logical change per PR. Keep diffs reviewable.

## Adding a command / cutting a release

See the runbooks in `.claude/skills/add-command/SKILL.md` and
`.claude/skills/release/SKILL.md`.
