"""Test the kitsu_helpers.py file."""

import filecmp

import dataset
from kitsu_library_availability.kitsu_helpers import configure_logger, export_table_as_csv, rm_brs

from .configuration import TEMP_DIR, TEST_DATA_DIR


def test_configure_logger():
    """Simple smoke test of the configure logger function."""
    configure_logger()  # act


def test_rm_brs():
    """Verify that rm_brs formats all whitespace as single spaces."""
    assert '1 2 3 4' == rm_brs('\n\n\r1\t2\n3\n\r\n4  ')  # act


def test_export_table_as_csv():
    """Test that a CSV file is correctly exported for a given SQL table."""
    expected_csv = TEST_DATA_DIR / 'test_export_table_as_csv.csv'
    csv_filename = TEMP_DIR / expected_csv.name
    rows = [
        {'col1': 'Alpha', 'col2': 123, 'col3': None},
        {'col1': 'Alpha', 'col2': 1.20, 'col3': 'Mixed'},
    ]
    db = dataset.connect(f"sqlite:///{TEMP_DIR / 'test_export_table_as_csv.db'}")
    table = db.create_table('TEST')
    table.drop()
    table.insert_many(rows)

    export_table_as_csv(csv_filename, table)  # act

    # Check that new file is identical to expected format
    assert filecmp.cmp(expected_csv, csv_filename, shallow=False)
