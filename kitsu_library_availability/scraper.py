"""Main scraper interface."""

import logging
import time

from .analysis import create_kitsu_database, merge_anime_info
from .api_helpers import get_anime, get_library, get_streams, get_user_id, selective_request
from .cache_helpers import CACHE_DIR, KITSU_DATA, initialize_cache, pretty_dump_json
from .kitsu_helpers import export_table_as_csv

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
            streams = get_streams(anime['data']['relationships']['streamingLinks']['links']['related'])
            all_data.append(merge_anime_info(anime_entry, anime, streams))  # FIXME: Improve how data is collected

        # Check if there is a 'next' URL available or if the iterations have reached their limit
        index += 1
        next_url = None
        try:
            next_url = this_lib_page['links']['next']
        except (AttributeError, KeyError) as error:
            logging.info(f'Failed to find next URL (index:{index}) with error: {error}')
        library_page = False
        if next_url:
            logging.debug(f'Fetching next library page URL: {next_url}')
            library_page = selective_request('library-next', next_url)

    summary_file_path = CACHE_DIR / 'all_data.json'
    pretty_dump_json(summary_file_path, {'data': all_data})
    create_kitsu_database(summary_file_path)

    csv_filename = CACHE_DIR / '_database_kitsu.csv'
    export_table_as_csv(csv_filename, KITSU_DATA.db['kitsu'])


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
