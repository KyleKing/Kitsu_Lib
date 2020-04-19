"""Helpers for Kitsu API requests."""

from pathlib import Path

from .kitsu_helpers import get_data, pretty_dump_json

STORE_PATH = Path(__file__).parent / 'local_storage'
"""Path to folder with all downloaded responses from Kitsu API."""

STORE_PATH.mkdir(exist_ok=True)


def get_kitsu(endpoint, *kwargs):
    """Make request against Kitsu API.

    Args:
        endpoint: URL subpath to be appended to base Kitsu API URL
        kwargs: Additional keyword arguments passed to `get_data()`

    Returns:
        dict: Kitsu API response

    """
    return get_data(f'https://kitsu.io/api/edge/{endpoint}', *kwargs)


def get_user(username):
    """Get anime response from Kitsu API.

    Args:
        username: Kitsu user name

    Returns:
        dict: Kitsu API response

    """
    user = get_kitsu(f'users?filter[name]={username}')
    pretty_dump_json(STORE_PATH / f'{username}.json', user)
    return user


def get_user_id(username=None):
    """Retrieve user's ID number.

    Args:
        username: optional Kitsu user name. Otherwise falls back to input()

    Returns:
        int: user id

    Raises:
        RuntimeError: if user does not input a valid username when prompted

    """
    if username is None:
        username = input('Type your Kitsu username and press enter: ').strip()
    if len(username) == 0:
        raise RuntimeError('User did not enter a username. Exiting.')

    user = get_user(username)
    return int(user['data'][0]['id'])


def get_library(user_id, is_anime=True):
    """Get user's library. Will either be manga or anime.

    Args:
        user_id: Kitsu user ID
        is_anime: optional boolean if the returned library should be for anime or manga. Default is True (anime)

    Returns:
        dict: Kitsu API response

    """
    source_type = 'anime' if is_anime else 'manga'
    lib_entry = get_kitsu(f'users/{user_id}/library-entries?filter[kind]={source_type}')
    pretty_dump_json(STORE_PATH / 'library.json', lib_entry)  # FIXME: Give file unique name!
    return lib_entry


def get_anime(anime_link):
    """Get anime response from Kitsu API.

    `anime_link = lib_entry['data'][0]['relationships']['anime']['links']['related']`

    Args:
        anime_link: URL to the anime. Typically from `relationships:anime:links:related`

    Returns:
        dict: Kitsu API response

    """
    anime = get_data(anime_link, kwargs={'include': 'categories'})
    pretty_dump_json(STORE_PATH / 'anime.json', anime)  # FIXME: Give file unique name!
    return anime


def get_streams(stream_link):
    """Get list of streams from Kitsu API.

    `stream_link = anime['data']['relationships']['streamingLinks']['links']['related']`

    Args:
        stream_link: URL to fetch available streams. Typically from `relationships:streamingLinks:links:related`

    Returns:
        dict: Kitsu API response

    """
    streams = get_data(stream_link)
    pretty_dump_json(STORE_PATH / 'stream.json', streams)  # FIXME: Give file unique name!
    return streams
