"""Helpers for managing the JSON response cache to reduce load on API."""

import json
import time
from pathlib import Path

import dataset
from dash_charts.dash_helpers import uniq_table_id
from icecream import ic

CACHE_DIR = Path(__file__).parent / 'local_cache'
"""Path to folder with all downloaded responses from Kitsu API."""


class DBConnect:
    """Manage database connection since closing connection isn't possible."""

    database_path = None
    """Path to the local storage SQLite database file. Initialize in `__init__()`."""

    _db = None

    @property
    def db(self):
        """Return connection to database. Will create new connection if one does not exist already.

        Returns:
            FIXME: dataset database instance

        """
        if self._db is None:
            self._db = dataset.connect(f'sqlite:///{self.database_path}')
        return self._db

    def __init__(self, database_path):
        """Store the database path and ensure the parent directory exists.

        Args:
            database_path: path to the SQLite file

        """
        self.database_path = database_path.resolve()
        self.database_path.parent.mkdir(exist_ok=True)


FILE_DATA = DBConnect(CACHE_DIR / '_file_lookup_database.db')
"""Global instance of the DBConnect() for the file lookup database."""

# FIXME: Implement this database for the Dash application
KITSU_DATA = DBConnect(CACHE_DIR / '_kitsu_data.db')
"""Global instance of the DBConnect() for the output for the Kitsu API parser."""


def pretty_dump_json(filename, obj):
    """Write indented JSON file.

    Args:
        filename: Path or plain string JSON filename to write
        obj: JSON object to write

    """
    Path(filename).write_text(json.dumps(obj, indent=4, separators=(',', ': ')))


def initialize_cache():
    """Ensure that the directory and database exist. Remove files from database if manually removed."""
    table = FILE_DATA.db['files']

    removed_files = []
    for row in table:
        if not Path(row['filename']).is_file():
            removed_files.append(row['filename'])
    ic(removed_files)

    for filename in removed_files:
        table.delete(filename=filename)


def store_response(prefix, url, obj):
    """Store the response object as a JSON file and track in a SQLite database.

    Args:
        prefix: string used to create more recognizable filenames
        url: full URL to use as a reference if already downloaded
        obj: JSON object to write

    """
    filename = CACHE_DIR / f'{prefix}_{uniq_table_id()}.json'
    FILE_DATA.db['files'].insert({'filename': str(filename), 'url': url, 'timestamp': time.time()})
    pretty_dump_json(filename, obj)
