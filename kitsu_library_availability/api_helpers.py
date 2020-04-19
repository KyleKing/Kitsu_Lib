"""Helpers for Kitsu API requests."""

import json
import logging
import time
from json.decoder import JSONDecodeError
from pathlib import Path

import requests
from icecream import ic

from .cache_helpers import FILE_DATA, match_url_in_cache, store_response


def get_data(url, kwargs=None, debug=False):
    """Return response from generic get request for data object.

    Args:
        url: URL for request
        kwargs: Additional arguments to pass to `requests.get()`. Default is None
        debug: if True, will print full response to log file

    Returns:
        dict: request response

    Raises:
        JSONDecodeError: if response cannot be decoded to JSON

    """
    logging.debug(f'get_data for: `{url}`')
    if kwargs is None:
        kwargs = {}
    raw = requests.get(url, kwargs)
    resp = None
    try:
        resp = raw.json()
        time.sleep(0.1)
    except JSONDecodeError as error:
        msg = f"{'=' * 80}\nFailed to parse response from: {url}\n{raw.text}\n\nerror:{error}"
        ic(msg)
        logging.debug(msg)
        raise

    if debug:
        logging.debug(resp)
    return resp


def selective_request(prefix, url, **get_kwargs):
    """Store the response object as a JSON file and track in a SQLite database.

    Args:
        prefix: string used to create more recognizable filenames
        url: full URL to use as a reference if already downloaded
        get_kwargs: additional keyword arguments to pass to `get_data()`

    Returns:
        dict: Kitsu API response

    Raises:
        RuntimeError: if duplicates found in database

    """
    matches = match_url_in_cache(url)

    obj = None
    if len(matches) == 0:
        logging.debug(f'Making new get request for {url}')
        obj = get_data(url, **get_kwargs)
        store_response(prefix, url, obj)
    elif len(matches) == 1:
        logging.debug(f"Loading response from {matches[0]['filename']} for {url}")
        obj = json.loads(Path(matches[0]['filename']).read_text())
    else:
        raise RuntimeError(f'Too many matches for url={url} in {FILE_DATA.database_path}. Matches: {matches}')

    return obj  # noqa: R504


def get_kitsu(endpoint, prefix='kitsu', **kwargs):
    """Make request against Kitsu API.

    Args:
        endpoint: URL subpath to be appended to base Kitsu API URL
        prefix: string used to create more recognizable filenames
        **kwargs: Additional keyword arguments passed to `get_data()`

    Returns:
        dict: Kitsu API response

    """
    return selective_request(prefix, f'https://kitsu.io/api/edge/{endpoint}', **kwargs)


def get_user(username):
    """Get anime response from Kitsu API.

    Args:
        username: Kitsu user name

    Returns:
        dict: Kitsu API response

    """
    url = f'users?filter[name]={username}'
    return get_kitsu(url, prefix='user')


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
    url = f'users/{user_id}/library-entries?filter[kind]={source_type}'
    return get_kitsu(url, prefix='library')


def get_anime(anime_link):
    """Get anime response from Kitsu API.

    `anime_link = lib_entry['data'][0]['relationships']['anime']['links']['related']`

    Args:
        anime_link: URL to the anime. Typically from `relationships:anime:links:related`

    Returns:
        dict: Kitsu API response

    """
    return selective_request('anime', anime_link, kwargs={'include': 'categories'})


def get_streams(stream_link):
    """Get list of streams from Kitsu API.

    `stream_link = anime['data']['relationships']['streamingLinks']['links']['related']`

    Args:
        stream_link: URL to fetch available streams. Typically from `relationships:streamingLinks:links:related`

    Returns:
        dict: Kitsu API response

    """
    return selective_request('streams', stream_link)
