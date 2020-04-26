"""Helpers for managing the JSON response cache to reduce load on API.

Notes on dataset. Full documentation: https://dataset.readthedocs.io/en/latest/api.html

```py
db = KITSU_DATA.db
db.create_table('anime', primary_id='slug', primary_type=db.types.text)
db.load_table('anime')  # Fails if table does not exist

ic(db.tables, db['anime'].columns, len(db['anime']))
ic([*db['anime'].all()][:2])

table = db['anime']
# ic([*table.find(id=[1, 3, 7])])
# ic([*table.find_one(id=4)])
ic([*table.find(status='completed')])
ic([*table.find(status={'<>': 'dropped'}, averageRating={'between': [60, 80]})])
ic([*table.distinct('status')])
# gt, >; || lt, <; || gte, >=; || lte, <=; || !=, <>, not; || between, ..

# Other
table.update(dict(name='John Doe', age=47), ['name'])
```

"""

import json
import time
from pathlib import Path

import dataset
from dash_charts.dash_helpers import uniq_table_id

from .kitsu_helpers import LOGGER

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
            dict: `dataset` database instance

        """
        if self._db is None:
            LOGGER.debug(f'Initializing dataset instance for {self.database_path}')
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

KITSU_DATA = DBConnect(CACHE_DIR / '_kitsu_data.db')
"""Global instance of the DBConnect() for the output for the Kitsu API parser."""


def pretty_dump_json(filename, obj):
    """Write indented JSON file.

    Args:
        filename: Path or plain string filename to write (should end with `.json`)
        obj: JSON object to write

    """
    LOGGER.debug(f'Creating file: {filename}')
    Path(filename).write_text(json.dumps(obj, indent=4, separators=(',', ': ')))


def initialize_cache():
    """Ensure that the directory and database exist. Remove files from database if manually removed."""
    table = FILE_DATA.db.create_table('files')

    removed_files = []
    for row in table:
        if not Path(row['filename']).is_file():
            removed_files.append(row['filename'])
    LOGGER.debug(f'Removing files: {removed_files}' if len(removed_files) > 0 else 'No removed files found')

    for filename in removed_files:
        table.delete(filename=filename)


def match_url_in_cache(url):
    """Return list of matches for the given URL in the file database.

    Args:
        url: full URL to use as a reference if already downloaded

    Returns:
        list: list of match object with keys of the SQL table

    """
    return [*FILE_DATA.db.load_table('files').find(url=url)]


def store_response(prefix, url, obj):
    """Store the response object as a JSON file and track in a SQLite database.

    Args:
        prefix: string used to create more recognizable filenames
        url: full URL to use as a reference if already downloaded
        obj: JSON object to write

    Raises:
        RuntimeError: if duplicate match found when storing

    """
    filename = CACHE_DIR / f'{prefix}_{uniq_table_id()}.json'
    new_row = {'filename': str(filename), 'url': url, 'timestamp': time.time()}
    # Check that the URL isn't already in the database
    LOGGER.debug(f'inserting row: {new_row}')
    matches = match_url_in_cache(url)
    if len(matches) > 0:
        raise RuntimeError(f'Already have an entry for this URL (`{url}`): {matches}')
    # Update the database and store the file
    FILE_DATA.db.load_table('files').insert(new_row)
    pretty_dump_json(filename, obj)
