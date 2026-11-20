from candidate import install_command


def test_documented_install_command_is_exact():
    assert install_command() == "pip install arbiter-gate"
