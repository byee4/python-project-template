"""Command-line interface.

Thin wrapper around :mod:`mytool.core`. Add new subcommands as functions
decorated with ``@cli.command()`` — see `.claude/skills/add-command`.
"""

from __future__ import annotations

import click

from mytool import __version__
from mytool.core import greet


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, "-V", "--version")
def cli() -> None:
    """mytool — a starter command-line tool."""


@cli.command()
@click.argument("name", default="world")
@click.option("--shout", is_flag=True, help="Upper-case the greeting.")
def hello(name: str, shout: bool) -> None:
    """Print a greeting."""
    click.echo(greet(name, shout=shout))


def main() -> None:
    """Console-script entry point (see ``[project.scripts]`` in pyproject)."""
    cli()


if __name__ == "__main__":
    main()
