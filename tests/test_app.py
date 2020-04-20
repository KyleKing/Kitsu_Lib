"""Test the app.py file."""

import time

import pytest
from kitsu_library_availability.app import KitsuExplorer


@pytest.mark.CHROME
def test_kitsu_explorer(dash_duo):
    """Smoke test the KitsuExplorer app class."""
    app = KitsuExplorer()
    app.create()

    dash_duo.start_server(app.app)  # act

    time.sleep(1)
    assert not dash_duo.get_logs()
