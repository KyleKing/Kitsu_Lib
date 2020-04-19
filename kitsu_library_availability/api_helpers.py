"""Helpers for Kitsu API requests."""

import logging
import time
from json.decoder import JSONDecodeError

import requests
from icecream import ic

from .cache_helpers import store_response


def get_data(url, kwargs=None, debug=False):
    """Return response from generic get request for data object.

    Args:
        url: URL for request
        kwargs: Additional arguments to pass to `requests.get()`. Default is None
        debug: if True, will print additional output to STDOUT. Default is False

    Returns:
        dict: request response

    Raises:
        JSONDecodeError: if response cannot be decoded to JSON

    """
    if debug:
        logging.debug(ic(f'GET: `{url}`'))
    if kwargs is None:
        kwargs = {}
    raw = requests.get(url, kwargs)
    try:
        resp = raw.json()
        if debug:
            logging.debug(ic(resp))
        time.sleep(0.1)
        return resp
    except JSONDecodeError as error:
        ic(f"{'=' * 80}\nFailed to parse response from: {url}\n{raw.text}\n\nerror:{error}")
        raise


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
    url = f'users?filter[name]={username}'
    user = get_kitsu(url)
    store_response(username, url, user)
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
    url = f'users/{user_id}/library-entries?filter[kind]={source_type}'
    lib_entry = get_kitsu(url)
    store_response('library', url, lib_entry)
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
    store_response('anime', anime_link, anime)
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
    store_response('stream', stream_link, streams)
    return streams
