"""Create test JSON files."""

import sys

from kitsu_library_availability import app
from kitsu_library_availability.kitsu_helpers import pretty_dump_json

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise RuntimeError(f'Expected username as CLI argument. Received: {sys.argv[1:]}')

    username = sys.argv[1]
    profile = app.get_kitsu(f'users?filter[name]={username}')
    pretty_dump_json('profile.json', profile)

    my_id = int(profile['data'][0]['id'])
    lib_entry = app.get_kitsu(f'users/{my_id}/library-entries?filter[kind]=anime')
    pretty_dump_json('lib_entry.json', lib_entry)

    this_entry = lib_entry
    for entry_data in this_entry['data']:
        anime = app.get_data(
            entry_data['relationships']['anime']['links']['related'],
            kwargs={'include': 'categories'},
        )
        pretty_dump_json('anime.json', anime)

        streams = app.get_data(anime['data']['relationships']['streamingLinks']['links']['related'])
        pretty_dump_json('streams.json', streams)

        break

        # lib_entry = app.get_data(this_entry['links']['next'])
