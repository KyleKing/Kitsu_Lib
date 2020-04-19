"""Helpers for Kitsu data analysis."""

import furl

from .kitsu_helpers import rm_brs


def summarize_streams(streams):
    """Create summary dictionary of available stream URLs.

    Args:
        streams: stream dictionary from `get_streams()`

    Returns:
        dict: summary dictionary with keys of the base URL and values of full stream URL

    Raises:
        KeyError: if multiple conflicting streams found (i.e. multiple streams on crunchyroll.com)

    """
    summary = {}
    for stream in streams['data']:
        stream_url = stream['attributes']['url']
        hostname = furl(stream_url).asdict()['host']
        if hostname in summary:
            raise KeyError(f'Too many streams for {hostname}. Found: {streams}')
        summary[hostname] = stream_url
    return summary


def parse_categories(anime):
    """Return list of category names.

    Args:
        anime: anime dictionary from `get_anime()`

    Returns:
        list: category names

    """
    return [attr['attributes']['slug'] for attr in anime['included']]


def merge_anime_info(anime_entry_data, anime):
    """WIP: combines a library entry and corresponding anime entry into single, flat dictionary.

    Notes on the `anime_entry_data` argument

    ```py
    library_page = get_library(user_id, is_anime=True)
    anime_entry_data = library_page['data'][0]['relationships']['anime']['links']['related']
    ```

    Args:
        anime_entry_data: entry from within library response
        anime: anime dictionary from `get_anime()`

    Returns:
        dict: single summary dictionary

    """
    entry_attr = anime_entry_data['attributes']
    anime_attr = anime['data']['attributes']

    entry_keys = ['createdAt', 'updatedAt', 'status', 'progress', 'notes', 'private', 'progressedAt', 'startedAt',
                  'finishedAt', 'ratingTwenty', 'subtype']
    anime_keys = ['canonicalTitle', 'slug', 'averageRating', 'userCount', 'favoritesCount', 'startDate', 'endDate',
                  'nextRelease', 'popularityRank', 'ratingRank', 'ageRating', 'status', 'episodeCount',
                  'episodeLength', 'totalLength', 'showType']
    # Combine and collapse fields of interest
    data = {
        'id': anime_entry_data['id'],
        'synopsis': rm_brs(anime_attr['synopsis']),
        'posterImage': anime_attr['posterImage']['original'],
        'categories': parse_categories(anime),
    }
    for attr, keys in [(entry_attr, entry_keys), (anime_attr, anime_keys)]:
        for key in keys:
            data[key] = attr[key] if key in attr else None

    return data
