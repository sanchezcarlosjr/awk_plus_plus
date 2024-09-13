import pytest
from awk_plus_plus.actions import interpret_url
import keyring


def test_interpret_interpolation():
    keyring.set_password("system", "username", "1")
    keyring.set_password("system", "password", "2")
    result = interpret_url("{{keyring.system.username}}:{{keyring.system.password}}")
    assert result.path == "1:2"

