"""Global variables for testing."""

from pathlib import Path

TEST_DIR = Path(__file__).parent
"""Test file directory."""

TEST_DATA_DIR = TEST_DIR / 'data'
"""Source data directory for tests."""

TEMP_DIR = TEST_DIR / 'temp'
"""Untracked temporary directory for intermediary test files."""

TEMP_DIR.mkdir(exist_ok=True)
