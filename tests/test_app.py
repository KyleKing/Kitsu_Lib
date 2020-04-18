"""Application tests."""

from kitsu_library_availability import app


def test_rm_brs():
    """Verify that rm_brs formats all whitespace as single spaces."""
    assert '1 2 3 4' == app.rm_brs('\n\n\r1\t2\n3\n\r\n4  ')  # act
