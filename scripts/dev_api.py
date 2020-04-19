"""Experiment with the Kitsu API.

WARN: This script is for development-only and may not work

"""

import sys
from pathlib import Path

from kitsu_library_availability import api_helpers
from kitsu_library_availability.kitsu_helpers import pretty_dump_json

WIP_DIR = Path(__file__).parent / 'WIP-Untracked'

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise RuntimeError(f'Expected username as CLI argument. Received: {sys.argv[1:]}')

    WIP_DIR.mkdir(exist_ok=True)

    username = sys.argv[1]
    profile = api_helpers.get_kitsu(f'users?filter[name]={username}')
    pretty_dump_json(WIP_DIR / 'profile.json', profile)

    my_id = int(profile['data'][0]['id'])
    lib_entry = api_helpers.get_kitsu(f'users/{my_id}/library-entries?filter[kind]=anime')
    pretty_dump_json(WIP_DIR / 'lib_entry.json', lib_entry)

    this_entry = lib_entry
    for entry_data in this_entry['data']:
        anime = api_helpers.get_data(
            entry_data['relationships']['anime']['links']['related'],
            kwargs={'include': 'categories'},
        )
        pretty_dump_json(WIP_DIR / 'anime.json', anime)

        streams = api_helpers.get_data(anime['data']['relationships']['streamingLinks']['links']['related'])
        pretty_dump_json(WIP_DIR / 'streams.json', streams)

        break

        # lib_entry = api_helpers.get_data(this_entry['links']['next'])
