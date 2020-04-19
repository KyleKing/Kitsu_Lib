"""Main scraper interface."""

import logging

from icecream import ic

from .analysis import merge_anime_info
from .api_helpers import get_anime, get_data, get_library, get_user_id
from .cache_helpers import CACHE_DIR, initialize_cache, pretty_dump_json

logging.basicConfig(filename='app_debug.log', filemode='w', level=logging.DEBUG)


def scrape_kitsu(username=None, limit=None):
    """Scrape the anime from the user's database into local storage.

    Args:
        username: optional Kitsu user name. Otherwise falls back to input()
        limit: optional maximum number of library pages to request. Useful for initial testing. Default is no limit

    """
    user_id = get_user_id(username)
    initialize_cache()

    # Loop through a user's library
    index = 0
    all_data = []
    library_page = get_library(user_id, is_anime=True)
    while library_page and (limit is None or index <= limit):
        this_lib_page = library_page
        for anime_entry in this_lib_page['data']:
            anime = get_anime(anime_entry['relationships']['anime']['links']['related'])
            all_data.append(merge_anime_info(anime_entry, anime))

        # Check if there is a 'next' URL available or if the iterations have reached their limit
        index += 1
        library_page = False
        try:
            url = this_lib_page['links']['next']
            ic(f'Fetching: {url}')
            library_page = get_data(url)
        except (AttributeError, KeyError) as error:
            ic(f'Failed to find next URL with error: {error}')

    # FIXME: Store output as a JSON file for now - will need to be converted to SQLite at some point
    pretty_dump_json(CACHE_DIR / 'all_data.json', {'data': all_data})
