from mytool.core import greet


def test_greet_default():
    assert greet("world") == "Hello, world!"


def test_greet_shout():
    assert greet("world", shout=True) == "HELLO, WORLD!"
