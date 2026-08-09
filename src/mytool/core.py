"""Core logic, kept separate from the CLI layer.

Put the actual work here so it can be unit-tested and reused without going
through argument parsing. The CLI in `cli.py` should stay a thin wrapper.
"""

from __future__ import annotations


def greet(name: str, *, shout: bool = False) -> str:
    """Return a greeting for ``name``.

    This is a placeholder to demonstrate the core/CLI split and the test
    pattern. Replace it with your tool's real logic.
    """
    message = f"Hello, {name}!"
    return message.upper() if shout else message
