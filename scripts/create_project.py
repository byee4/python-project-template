#!/usr/bin/env python3
"""Create a renamed, git-initialized CLI project from this template.

Non-interactive generator used both by hand and by Devboard's one-click
Quick Start. It copies this template to a new location, rewrites every
placeholder, initializes git, and optionally sets up the environment,
refreshes the codebase-memory graph, and creates a GitHub repo.

Unlike `scripts/init.py` (which renames the template *in place*), this
writes a brand-new project at ``target`` and leaves the template untouched.

Example:
    python3 scripts/create_project.py ../my-cli --slug my-cli --name "My CLI"
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Never copy these into the new project.
EXCLUDED_NAMES = {
    ".git",
    ".venv",
    "__pycache__",
    "dist",
    "build",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".DS_Store",
}
EXCLUDED_SUFFIXES = {".pyc", ".egg-info"}
# The template's own generator should not travel into generated projects;
# `scripts/init.py` is the in-place renamer and is equally irrelevant there.
EXCLUDED_SCRIPTS = {"create_project.py", "init.py"}

TEMPLATE_SLUG = "python-project-template"
TEMPLATE_OWNER = "brian-yee"
PLACEHOLDER_PKG = "mytool"


def parse_args() -> argparse.Namespace:
    """Parse command-line options for creating a CLI project.

    Returns
    -------
    argparse.Namespace
        Validated command-line values supplied to :func:`main`.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path, help="new project directory; must not exist")
    parser.add_argument("--slug", required=True, help="lowercase slug, e.g. my-cli")
    parser.add_argument("--name", required=True, help="display name, e.g. My CLI")
    parser.add_argument("--github", help="GitHub OWNER/REPOSITORY to create and push to")
    parser.add_argument(
        "--visibility",
        choices=("private", "public"),
        default="private",
        help="visibility for a repo created with --github (default: private)",
    )
    parser.add_argument(
        "--skip-sync", action="store_true", help="do not set up the virtual environment"
    )
    parser.add_argument(
        "--skip-index",
        action="store_true",
        help="do not refresh the codebase-memory graph after the rename",
    )
    parser.add_argument(
        "--skip-beads",
        action="store_true",
        help="accepted for generator-contract compatibility; this template has no Beads step",
    )
    return parser.parse_args()


def validate_slug(slug: str) -> None:
    """Validate a project slug used in generated paths and identifiers.

    Parameters
    ----------
    slug : str
        Candidate lowercase, hyphen-delimited project slug.

    Raises
    ------
    ValueError
        If the slug does not begin with a lowercase letter or contains an
        unsupported character.
    """
    if not re.fullmatch(r"[a-z][a-z0-9-]*", slug):
        raise ValueError(
            "--slug must start with a lowercase letter and contain only lowercase "
            "letters, digits, and hyphens"
        )


def validate_github_repository(repository: str | None) -> None:
    """Validate an optional GitHub ``OWNER/REPOSITORY`` identifier.

    Parameters
    ----------
    repository : str or None
        Repository identifier to validate, or ``None`` when GitHub creation is
        disabled.

    Raises
    ------
    ValueError
        If a supplied identifier is not in ``OWNER/REPOSITORY`` form.
    """
    if repository and not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("--github must use OWNER/REPOSITORY form")


def copy_template(source: Path, target: Path) -> None:
    """Copy the reusable template files into a new project directory.

    Parameters
    ----------
    source : pathlib.Path
        Template repository root.
    target : pathlib.Path
        New project directory, which must not already exist.

    Raises
    ------
    FileExistsError
        If ``target`` already exists.
    OSError
        If a template file cannot be read, copied, or created.
    """
    def ignore(directory: str, names: list[str]) -> set[str]:
        skip = {
            name
            for name in names
            if name in EXCLUDED_NAMES or Path(name).suffix in EXCLUDED_SUFFIXES
        }
        if Path(directory).name == "scripts":
            skip |= {name for name in names if name in EXCLUDED_SCRIPTS}
        return skip

    shutil.copytree(source, target, ignore=ignore)


def replace_template_identifiers(target: Path, slug: str, name: str, owner: str) -> None:
    """Replace template identity markers and rename the import package.

    Parameters
    ----------
    target : pathlib.Path
        Root of the copied project.
    slug : str
        Distribution and command slug for the generated project.
    name : str
        Human-readable project name.
    owner : str
        Repository owner used in generated GitHub references.

    Raises
    ------
    OSError
        If a readable text file cannot be rewritten or the package directory
        cannot be renamed.

    Notes
    -----
    Binary files that cannot be decoded as UTF-8 are left unchanged. Hyphens
    in ``slug`` become underscores only in Python import-package references.
    """
    package = slug.replace("-", "_")
    for path in target.rglob("*"):
        if not path.is_file() or path.suffix in EXCLUDED_SUFFIXES:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        # GitHub slug first, before the bare package token inside it is rewritten.
        content = content.replace(f"{TEMPLATE_OWNER}/{PLACEHOLDER_PKG}", f"{owner}/{slug}")
        # The template's own repo name: H1 becomes the human name, the rest the slug.
        content = content.replace(f"# {TEMPLATE_SLUG}", f"# {name}")
        content = content.replace(TEMPLATE_SLUG, slug)
        # The package / console-command token.
        content = content.replace(PLACEHOLDER_PKG, package)
        # Keep the distribution name and console command dashed; only the import
        # package and entry-point target use the underscore form.
        content = content.replace(f'name = "{package}"', f'name = "{slug}"')
        content = content.replace(
            f'{package} = "{package}.cli:main"', f'{slug} = "{package}.cli:main"'
        )  # pyproject [project.scripts]
        content = content.replace(
            f"{package} = {package}.cli:main", f"{slug} = {package}.cli:main"
        )  # conda meta.yaml entry_points
        content = content.replace(f"{package}:latest", f"{slug}:latest")  # docker image tag

        path.write_text(content, encoding="utf-8")

    (target / "src" / PLACEHOLDER_PKG).rename(target / "src" / package)


def run(command: list[str], cwd: Path) -> None:
    """Run a command in the generated project and require success.

    Parameters
    ----------
    command : list[str]
        Executable and arguments to run without a shell.
    cwd : pathlib.Path
        Working directory for the child process.

    Raises
    ------
    subprocess.CalledProcessError
        If the command exits with a nonzero status.
    OSError
        If the executable cannot be started.
    """
    subprocess.run(command, cwd=cwd, check=True)


def git_environment() -> dict[str, str]:
    """Build the environment for the template's initial Git commit.

    Returns
    -------
    dict[str, str]
        Current environment variables plus deterministic bootstrap author and
        committer identities.
    """
    return os.environ | {
        "GIT_AUTHOR_NAME": "Template Bootstrap",
        "GIT_AUTHOR_EMAIL": "template-bootstrap@localhost",
        "GIT_COMMITTER_NAME": "Template Bootstrap",
        "GIT_COMMITTER_EMAIL": "template-bootstrap@localhost",
    }


def initialize_git(target: Path) -> None:
    """Initialize and commit the generated project on a ``main`` branch.

    Parameters
    ----------
    target : pathlib.Path
        Generated project directory to initialize.

    Raises
    ------
    subprocess.CalledProcessError
        If Git initialization, staging, or the initial commit fails.
    OSError
        If Git cannot be started.
    """
    run(["git", "init", "-b", "main"], target)
    run(["git", "add", "-A"], target)
    subprocess.run(
        ["git", "commit", "-m", "Initial template bootstrap"],
        cwd=target,
        check=True,
        env=git_environment(),
    )


def setup_environment(target: Path) -> None:
    """Create a ``uv`` environment and install the generated project.

    Parameters
    ----------
    target : pathlib.Path
        Generated project directory containing ``pyproject.toml``.

    Raises
    ------
    RuntimeError
        If the ``uv`` executable is unavailable.
    subprocess.CalledProcessError
        If environment creation or editable installation fails.
    OSError
        If ``uv`` cannot be started.
    """
    if shutil.which("uv") is None:
        raise RuntimeError("uv is required to set up the environment; install uv or pass --skip-sync.")
    run(["uv", "venv"], target)
    run(["uv", "pip", "install", "-e", ".[dev]"], target)


def refresh_codebase_graph(target: Path) -> None:
    """Refresh the generated project's persistent codebase graph when available.

    Parameters
    ----------
    target : pathlib.Path
        Generated project directory to index.

    Raises
    ------
    subprocess.CalledProcessError
        If the installed graph indexer exits with a nonzero status.
    OSError
        If the installed graph indexer cannot be started.

    Notes
    -----
    A missing ``codebase-memory-mcp`` executable is reported to standard output
    and treated as a non-fatal skipped refresh.
    """
    payload = json.dumps({"repo_path": str(target), "persistence": True})
    if shutil.which("codebase-memory-mcp") is None:
        print(
            "codebase-memory-mcp not found; skipping graph refresh. On an MCP-enabled "
            f"host, run:\n  echo '{payload}' | codebase-memory-mcp cli index_repository"
        )
        return
    subprocess.run(
        ["codebase-memory-mcp", "cli", "index_repository"],
        cwd=target,
        check=True,
        input=payload,
        text=True,
    )


def create_github_repository(target: Path, repository: str, visibility: str) -> None:
    """Create and push a GitHub repository for the generated project.

    Parameters
    ----------
    target : pathlib.Path
        Generated project directory to publish.
    repository : str
        GitHub repository identifier in ``OWNER/REPOSITORY`` form.
    visibility : str
        Visibility flag accepted by ``gh repo create``.

    Raises
    ------
    RuntimeError
        If the GitHub CLI is unavailable.
    subprocess.CalledProcessError
        If repository creation or the initial push fails.
    OSError
        If the GitHub CLI cannot be started.
    """
    if shutil.which("gh") is None:
        raise RuntimeError("GitHub CLI is required for --github; install and authenticate `gh`.")
    run(
        ["gh", "repo", "create", repository, f"--{visibility}",
         "--source", str(target), "--remote", "origin", "--push"],
        target,
    )


def main() -> int:
    """Create a project from validated command-line arguments.

    Returns
    -------
    int
        Zero after the project is generated and optional setup steps succeed.

    Raises
    ------
    ValueError
        If the slug, GitHub identifier, target constraints, or other generator
        input is invalid.
    RuntimeError
        If a requested optional tool is unavailable.
    subprocess.CalledProcessError
        If Git, ``uv``, graph indexing, or GitHub repository creation fails.
    OSError
        If project files or a required executable cannot be accessed.
    """
    args = parse_args()
    source = Path(__file__).resolve().parents[1]
    target = args.target.resolve()
    validate_slug(args.slug)
    validate_github_repository(args.github)
    if target.exists():
        raise ValueError(f"target already exists: {target}")

    owner = args.github.split("/", 1)[0] if args.github else TEMPLATE_OWNER

    copy_template(source, target)
    replace_template_identifiers(target, args.slug, args.name, owner)
    initialize_git(target)
    if not args.skip_sync:
        setup_environment(target)
    if not args.skip_index:
        refresh_codebase_graph(target)
    if args.github:
        create_github_repository(target, args.github, args.visibility)

    print(f"Created {args.name} at {target}")
    print(f"Next: cd {target} && make setup && make test")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, ValueError, subprocess.CalledProcessError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2) from error
