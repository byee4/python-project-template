# Deployment

Four distribution channels: **PyPI**, **uv**, **conda**, and **Docker**. Names
below use `mytool` / `my-cli` — substitute your own after `scripts/init.py`.

## Prerequisites

- A clean, tested tree: `make lint && make test`.
- Version bumped in **both** `src/mytool/__init__.py` and `pyproject.toml`
  (see `.claude/skills/release`).

---

## PyPI

### Automated (recommended): trusted publishing

No API tokens stored anywhere. One-time setup:

1. Create the project on https://pypi.org (upload once manually, or reserve the
   name).
2. On PyPI → the project → *Publishing* → add a **Trusted Publisher**:
   - Owner: `brian-yee`, Repository: `mytool`
   - Workflow: `publish.yml`, Environment: `pypi`
3. In GitHub → repo → *Settings → Environments* → create an environment named
   `pypi`.

Then every published **GitHub Release** triggers `.github/workflows/publish.yml`,
which builds with `uv build` and uploads via OIDC.

### Manual fallback

```bash
make build                 # uv build (sdist + wheel into dist/)
twine upload dist/*        # or: make publish  (needs a PyPI token)
# Dry run first:
twine upload --repository testpypi dist/*   # or: make publish-test
```

Set the token via `~/.pypirc` or `TWINE_USERNAME=__token__ TWINE_PASSWORD=pypi-...`.

---

## uv

`uv` reads the same `pyproject.toml` — nothing extra to maintain.

```bash
uv build                   # build sdist + wheel
uv publish                 # upload to PyPI (uv publish --index testpypi for TestPyPI)
```

Consumers can install or run the CLI without a manual venv:

```bash
uv tool install my-cli     # install the command globally, isolated
uvx my-cli --help          # run the latest without installing
```

---

## conda

**Dev environment** (from `environment.yml`):

```bash
conda env create -f environment.yml
conda activate my-cli
pip install -e ".[dev]"
```

**Build a conda package** (from `conda/meta.yaml`):

```bash
conda install -n base conda-build
conda build conda/ -c conda-forge
```

For a real release, edit `conda/meta.yaml` to pull the sdist from PyPI and pin
its `sha256` instead of building from the working tree (`source: path: ..`).
Publish to a channel with `anaconda upload <path-to-.conda>` (needs
`anaconda-client` and a login), or submit to conda-forge via a `staged-recipes` PR.

---

## Docker

Multi-stage build: stage one builds a wheel, stage two installs it into a slim
runtime whose entrypoint is the CLI.

```bash
make docker                            # docker build -t mytool:latest .
docker run --rm mytool:latest hello Brian --shout
```

Arguments after the image name are passed straight to the CLI (via `ENTRYPOINT`).

To publish the image:

```bash
docker tag mytool:latest ghcr.io/brian-yee/mytool:0.1.0
docker push ghcr.io/brian-yee/mytool:0.1.0
```

---

## Release checklist

1. `make lint && make test` green.
2. Bump version in `__init__.py` + `pyproject.toml` (+ `conda/meta.yaml`).
3. Commit, tag `vX.Y.Z`, push tag.
4. Cut a GitHub Release → `publish.yml` ships to PyPI.
5. (Optional) `make docker` + push image; rebuild conda package.
