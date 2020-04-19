"""Main scraper interface."""

import logging
import time

from icecream import ic

from .analysis import merge_anime_info
from .api_helpers import get_anime, get_library, get_user_id, selective_request
from .cache_helpers import CACHE_DIR, initialize_cache, pretty_dump_json

logging.basicConfig(
    filemode='w',
    filename=f'app_debug-{time.time()}.log',
    format='%(asctime)s\t%(levelname)s\t%(filename)s:%(lineno)d\t%(funcName)s():\t%(message)s',
    level=logging.DEBUG,
)


def scrape_kitsu_unsafe(username=None, limit=None):
    """Scrape the anime from the user's database into local storage.

    Args:
        username: optional Kitsu user name. Otherwise falls back to input()
        limit: optional maximum number of library pages to request. Useful for initial testing. Default is no limit

    """
    initialize_cache()
    user_id = get_user_id(username)
    logging.debug(f'Scraping Kitsu for {username} ({user_id})')

    # Loop through a user's library
    index = 0
    all_data = []
    library_page = get_library(user_id, is_anime=True)
    while library_page and (limit is None or index <= limit):
        this_lib_page = library_page
        for anime_entry in this_lib_page['data']:
            anime = get_anime(anime_entry['relationships']['anime']['links']['related'])
            all_data.append(merge_anime_info(anime_entry, anime))  # FIXME: Improve how data is collected

        # Check if there is a 'next' URL available or if the iterations have reached their limit
        index += 1
        library_page = False
        try:
            url = this_lib_page['links']['next']
            logging.debug(f'Fetching next library page URL: {url}')
            library_page = selective_request('library-next', url)
        except (AttributeError, KeyError) as error:
            msg = f'Failed to find next URL (index:{index}) with error: {error}'
            ic(msg)
            logging.debug(msg)

    pretty_dump_json(CACHE_DIR / 'all_data.json', {'data': all_data})


def scrape_kitsu(username=None, limit=None):
    """Capture log exception from scrape_kitsu_unsafe.

    Args:
        username: optional Kitsu user name. Otherwise falls back to input()
        limit: optional maximum number of library pages to request. Useful for initial testing. Default is no limit

    """
    try:
        scrape_kitsu_unsafe(username, limit)
    except Exception:
        logging.exception(f'Scraping Kitsu Library for {username} Failed')
        raise
