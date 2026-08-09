---
name: add-command
description: Add a new subcommand to this Click-based CLI tool. Use when the user asks to add, create, or wire up a new command / subcommand to the CLI. Keeps logic in core.py and the command thin, with a test.
---

# Add a CLI subcommand

This project keeps the CLI thin: real work lives in `src/<pkg>/core.py`, and
`src/<pkg>/cli.py` only parses args and prints. Follow that split.

## Steps

1. **Write the logic in `core.py`** as a plain, pure function. No printing, no
   `sys.exit`, no Click — just inputs → return value (or a raised exception).

   ```python
   def word_count(text: str) -> int:
       return len(text.split())
   ```

2. **Add a unit test in `tests/test_core.py`** for that function. Cover the
   normal case and one edge case.

   ```python
   from <pkg>.core import word_count

   def test_word_count():
       assert word_count("a b c") == 3
       assert word_count("") == 0
   ```

3. **Add the thin command in `cli.py`** under the `cli` group. Parse args,
   call core, echo the result.

   ```python
   from <pkg>.core import word_count

   @cli.command()
   @click.argument("text")
   def count(text: str) -> None:
       """Count words in TEXT."""
       click.echo(word_count(text))
   ```

4. **Add a CLI test in `tests/test_cli.py`** using `CliRunner`.

   ```python
   def test_count():
       result = CliRunner().invoke(cli, ["count", "a b c"])
       assert result.exit_code == 0
       assert result.output.strip() == "3"
   ```

5. **Verify**: `ruff check .` and `pytest` both pass.

6. **Document**: add the command to `README.md` usage and `docs/codemap.md` if it
   introduces a new module or public surface.

## Guidelines

- One responsibility per command. If a callback grows past a few lines, push the
  work into `core.py`.
- Use `click.echo` (not `print`) so output is testable and stream-aware.
- For errors the user caused, raise `click.ClickException("message")` — Click
  renders it cleanly and sets a non-zero exit code.
