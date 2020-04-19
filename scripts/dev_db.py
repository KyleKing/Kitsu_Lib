"""Experimenting with using dataset for managing local data storage.

Mostly just the quick start guide for now

"""

import json
from pathlib import Path

import dataset
import humps
from icecream import ic
from kitsu_library_availability.cache_helpers import CACHE_DIR

WIP_DIR = Path(__file__).parent / 'WIP-Untracked'


def quick_start_guide():
    database_path = (WIP_DIR / 'dev_database.db').resolve()
    db = dataset.connect(f'sqlite:///{database_path}')

    # get a reference to the table 'user'
    table = db['user']

    # Insert a new record.
    table.insert(dict(name='John Doe', age=46, country='China'))

    # dataset will create "missing" columns any time you insert a dict with an unknown key
    table.insert(dict(name='Jane Doe', age=37, country='France', gender='female'))

    table.update(dict(name='John Doe', age=47), ['name'])

    with dataset.connect() as tx:
        tx['user'].insert(dict(name='John Doe', age=46, country='China'))

    ic(db.tables)
    ic(db['user'].columns)
    ic(len(db['user']))

    users = db['user'].all()
    ic(users)
    for user in db['user']:
        ic(user['age'])

    # We can search for specific entries using find() and find_one()

    # All users from China
    chinese_users = table.find(country='China')
    ic(chinese_users)
    # Get a specific user
    john = table.find_one(name='John Doe')
    ic(john)
    # Find multiple at once
    winners = table.find(id=[1, 3, 7])
    ic(winners)

    # Find by comparison operator
    elderly_users = table.find(age={'>=': 70})
    ic(elderly_users)
    possible_customers = table.find(age={'between': [21, 80]})
    ic(possible_customers)

    # Use the underlying SQLAlchemy directly
    elderly_users = table.find(table.table.columns.age >= 70)
    ic(elderly_users)

    # Possible comparison operators:
    # gt, >; || lt, <; || gte, >=; || lte, <=; || !=, <>, not; || between, ..

    # Using distinct() we can grab a set of rows with unique values in one or more columns:
    # Get one user per country
    ic(db['user'].distinct('country'))


def create_db(database_path):
    if database_path.is_file():
        database_path.unlink()

    db = dataset.connect(f'sqlite:///{database_path}')
    table = db['anime']

    all_data = json.loads((CACHE_DIR / 'all_data.json').read_text())
    for entry in all_data['data']:
        # Lists are unsupported types, need to unwrap and remove dashes
        categories = entry.pop('categories')
        for category in categories:
            entry[humps.camelize(category)] = True
        ic(entry)

        table.insert(entry)

    return db


def inspect_db(db):
    ic(db.tables, db['anime'].columns, len(db['anime']))
    ic([*db['anime'].all()][:2])


def experiment_db():
    # Experiment with loading JSON into database. Use data created by early version of ./run_scraper.py
    create = False

    database_path = (WIP_DIR / 'dev_library.db').resolve()
    if create:
        db = create_db(database_path)
        inspect_db(db)
    else:
        db = dataset.connect(f'sqlite:///{database_path}')

    table = db['anime']
    ic([*table.find(status={'<>': 'not_a_status'}, averageRating={'<=': 85})])
    ic([*table.distinct('status')])


if __name__ == '__main__':
    # quick_start_guide()
    # experiment_db()

    pass
