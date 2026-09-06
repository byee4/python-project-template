#!/usr/bin/env python3
"""Rename the template placeholders to your new project's name.

Usage:
    python scripts/init.py my-cli-name
    python scripts/init.py            # prompts for the name

This rewrites the "mytool" package/command name and the "brian-yee/mytool"
GitHub slug across the tree, renames the src package directory, and then
deletes itself. Run it once, right after copying the template.

The distribution name becomes the dashed form you pass (e.g. "my-cli-name");
the importable package becomes its underscore form ("my_cli_name").
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Files/dirs we never rewrite.
SKIP_DIRS = {".git", ".venv", "dist", "build", "__pycache__", ".pytest_cache", ".ruff_cache"}
TEXT_SUFFIXES = {".py", ".toml", ".yml", ".yaml", ".md", ".cfg", ".txt", ".sh", ""}
# Files with no suffix we still want to treat as text:
TEXT_NAMES = {"Dockerfile", "Makefile", "LICENSE", ".dockerignore", ".gitignore", ".env.example"}


def valid(name: str) -> str:
    """Normalize and validate a distribution name.

    Parameters
    ----------
    name : str
        Candidate distribution name. Surrounding whitespace is ignored and
        underscores are normalized to hyphens.

    Returns
    -------
    str
        Lowercase, hyphen-delimited distribution slug.

    Raises
    ------
    SystemExit
        If the normalized name does not begin with a letter or contains an
        unsupported character.
    """
    slug = name.strip().lower().replace("_", "-")
    if not re.fullmatch(r"[a-z][a-z0-9-]*", slug):
        sys.exit(f"Invalid name {name!r}: use letters, digits, and hyphens; start with a letter.")
    return slug


def main() -> None:
    """Rename template placeholders and remove the one-time initializer.

    Raises
    ------
    SystemExit
        If the command-line or prompted project name is invalid.
    OSError
        If a template file cannot be rewritten, the package cannot be renamed,
        or this initializer cannot remove itself.

    Notes
    -----
    The distribution name remains hyphen-delimited while the import package
    uses underscores. Files that cannot be decoded as UTF-8 are left unchanged.
    """
    raw = sys.argv[1] if len(sys.argv) > 1 else input("New project name (e.g. my-cli): ")
    dist = valid(raw)
    pkg = dist.replace("-", "_")

    replacements = {
        "brian-yee/mytool": f"brian-yee/{dist}",  # GitHub slug (do this before "mytool")
        "mytool": pkg,  # importable package + console command
    }

    for path in ROOT.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if not path.is_file():
            continue
        if path.suffix not in TEXT_SUFFIXES and path.name not in TEXT_NAMES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        new = text
        for old, repl in replacements.items():
            new = new.replace(old, repl)
        # The dashed distribution name in pyproject/conda/urls where it differs.
        new = new.replace(f'name = "{pkg}"', f'name = "{dist}"')
        # Keep the console command as the dashed name; only the entry-point
        # target uses the underscore package name.
        new = new.replace(f'{pkg} = "{pkg}.cli:main"', f'{dist} = "{pkg}.cli:main"')  # pyproject
        new = new.replace(f"{pkg} = {pkg}.cli:main", f"{dist} = {pkg}.cli:main")  # conda meta.yaml
        new = new.replace(f"{pkg}:latest", f"{dist}:latest")  # docker image tag (Makefile/README)
        if new != text:
            path.write_text(new, encoding="utf-8")

    # Rename the package directory.
    src_pkg = ROOT / "src" / "mytool"
    if src_pkg.is_dir():
        src_pkg.rename(ROOT / "src" / pkg)

    print(f"Renamed template to '{dist}' (package '{pkg}').")
    print("Next: git init && python scripts/init.py is done — now `make setup && make test`.")
    (ROOT / "scripts" / "init.py").unlink()


if __name__ == "__main__":
    main()
