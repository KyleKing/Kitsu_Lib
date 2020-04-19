"""Experimenting with using dataset for managing local data storage.

Mostly just the quick start guide for now

"""

from pathlib import Path

import dataset
from icecream import ic

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


if __name__ == '__main__':
    quick_start_guide()
