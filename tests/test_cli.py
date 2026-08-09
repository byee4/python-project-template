from click.testing import CliRunner

from mytool import __version__
from mytool.cli import cli


def test_hello_default():
    result = CliRunner().invoke(cli, ["hello"])
    assert result.exit_code == 0
    assert result.output.strip() == "Hello, world!"


def test_hello_name_and_shout():
    result = CliRunner().invoke(cli, ["hello", "Brian", "--shout"])
    assert result.exit_code == 0
    assert result.output.strip() == "HELLO, BRIAN!"


def test_version():
    result = CliRunner().invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output
