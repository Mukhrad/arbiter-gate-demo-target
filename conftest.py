"""These contract tests under tests/ are not meant to be collected directly
by a bare `pytest` run at the repo root -- they import a `candidate` module
that only exists because scripts/route_and_verify.py copies it in next to
a copy of the test file, inside a throwaway temp directory, before running
pytest there. Collecting them here would fail with ModuleNotFoundError and
look like a broken repo rather than what it actually is: fixtures used by
the harness. Run `python scripts/route_and_verify.py` (what CI does) to
exercise them for real."""

collect_ignore_glob = ["tests/test_*_contract.py"]
