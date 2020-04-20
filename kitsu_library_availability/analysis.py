"""Helpers for Kitsu data analysis."""

import json
from pathlib import Path

import humps
from furl import furl
from icecream import ic

from .cache_helpers import KITSU_DATA
from .kitsu_helpers import LOGGER, rm_brs


def filter_stream_urls(streams):
    """Create a list of valid stream URLs.

    Args:
        streams: stream dictionary from `get_streams()`

    Returns:
        list: list of string URLs for each unique stream

    """
    stream_urls = []
    for stream_url in [stream['attributes']['url'] for stream in streams['data']]:
        # Some links that pointed to Netflix now just are 't'?
        if stream_url != 't' and len(stream_url):
            if not stream_url.startswith('http'):
                stream_url = f'https://{stream_url}'
            stream_urls.append(stream_url)
    return stream_urls


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
    ic_streams = ic.format(streams)
    for stream_url in filter_stream_urls(streams):
        # Create a key for each hostname
        if 'a.co/' in stream_url:
            key = 'amazon'  # Handle case of the shortened Amazon link, example: http://a.co/d/9hJEmKC
        else:
            key = furl(stream_url).asdict()['host'].split('.')[-2]
        for style in ['sub', 'dub']:
            if style in stream_url.lower():
                key += f'_{style}'
        # Add unique hostname key to the summary
        if key in summary:
            LOGGER.warning(f'Too many streams. Overwriting {key}. Found: {ic_streams}')
        summary[key] = stream_url
    return summary


def parse_categories(anime):
    """Return list of category names.

    Args:
        anime: anime dictionary from `get_anime()`

    Returns:
        list: category names

    """
    return [attr['attributes']['slug'] for attr in anime['included']]


def merge_anime_info(anime_entry_data, anime, streams):
    """WIP: combines a library entry and corresponding anime entry into single, flat dictionary.

    Note: `anime_entry_data` argument is from:
    `anime_entry_data = get_library(user_id, is_anime=True)['data'][n]`

    Args:
        anime_entry_data: entry from within library response
        anime: anime dictionary from `get_anime()`
        streams: stream dictionary from `get_streams()`

    Returns:
        dict: single summary dictionary

    """
    entry_attr = anime_entry_data['attributes']
    anime_attr = anime['data']['attributes']

    entry_keys = ['createdAt', 'updatedAt', 'progress', 'notes', 'private', 'progressedAt', 'startedAt',
                  'finishedAt', 'ratingTwenty', 'subtype']
    anime_keys = ['canonicalTitle', 'slug', 'averageRating', 'userCount', 'favoritesCount', 'startDate', 'endDate',
                  'nextRelease', 'popularityRank', 'ratingRank', 'ageRating', 'status', 'episodeCount',
                  'episodeLength', 'totalLength', 'showType']
    if any(key in entry_keys for key in anime_keys):
        raise RuntimeError('FOUND DUPLICATE KEYS')

    # Combine and collapse fields of interest
    poster_image = anime_attr['posterImage']
    data = {
        'id': anime_entry_data['id'],
        'synopsis': rm_brs(anime_attr['synopsis']),
        'posterImage': poster_image['original'] if poster_image else None,
        'categories': parse_categories(anime),
        'watch_status': entry_attr['status'],
        **summarize_streams(streams),
    }
    for attr, keys in [(entry_attr, entry_keys), (anime_attr, anime_keys)]:
        for key in keys:
            data[key] = attr[key] if key in attr else None

    return data


def create_kitsu_database(summary_file_path):
    """Create the Kitsu database with data from cached `merge_anime_info()` file.

    Args:
        summary_file_path: path to the JSON summary file

    """
    table = KITSU_DATA.db.create_table('kitsu', primary_id='slug', primary_type=KITSU_DATA.db.types.text)
    table.drop()  # Clear database

    # Insert each entry from JSON file into the table
    all_data = json.loads(Path(summary_file_path).read_text())
    entries = []
    for entry in all_data['data']:
        # Lists are unsupported types, need to unwrap and remove dashes
        categories = entry.pop('categories')
        for category in categories:
            entry[humps.camelize(category)] = True
        entries.append(entry)
    table.insert_many(entries)  # much faster than insert()
