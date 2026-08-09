---
name: release
description: Cut a versioned release of this CLI tool and publish to PyPI (and optionally conda/Docker). Use when the user asks to release, publish, ship a new version, bump the version, or tag a release.
---

# Cut a release

Publishing to PyPI is automated via GitHub trusted publishing: cutting a GitHub
Release runs `.github/workflows/publish.yml`. Your job is to get a clean,
version-bumped, tagged commit onto `main`.

## Steps

1. **Confirm the target version** with the user (e.g. `0.2.0`). Follow semver:
   patch for fixes, minor for features, major for breaking changes.

2. **Green checks**: `ruff check .` and `pytest` must pass first. Do not release
   a red tree.

3. **Bump the version in both places** (they must match):
   - `src/<pkg>/__init__.py` → `__version__`
   - `pyproject.toml` → `version`
   - Also update `conda/meta.yaml` `version` if publishing to conda.

4. **Commit** on a branch, open a PR, merge to `main`:
   `release: v0.2.0`

5. **Tag and push** (on `main` after merge):
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```

6. **Cut the GitHub Release** for tag `v0.2.0` (via the GitHub UI or
   `gh release create v0.2.0 --generate-notes`). This triggers `publish.yml`,
   which builds with `uv build` and uploads to PyPI via OIDC.

7. **Verify** the release landed: `pip index versions <dist-name>` or check the
   PyPI project page. Confirm the workflow run succeeded in the Actions tab.

## Optional extras

- **Docker**: `make docker`, then tag + push to your registry
  (see `docs/deployment.md`).
- **conda**: rebuild with `conda build conda/` and upload, or open a
  conda-forge `staged-recipes` PR.

## Guardrails

- Never `git push --force` or rewrite tags. If a release is bad, publish a new
  patch version — don't re-tag.
- If trusted publishing isn't set up yet, follow the one-time setup in
  `docs/deployment.md` (PyPI trusted publisher + `pypi` GitHub environment)
  before cutting the release, or fall back to `make publish` with a token.
