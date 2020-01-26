"""Main application."""

import csv
import json
import logging
import time
from urllib.parse import urlparse

import requests

try:
    from icecream import ic
except ImportError:  # Graceful fall back if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa: E731

logging.basicConfig(filename='wip.log', filemode='w', level=logging.DEBUG)


# TODO: Write to files in a folder
# Step 2: read files and create summary
# Load into dataframe and spit out CSV with preferred filter
# Creating running list of genres adding Nones to the records until all the same length


def rm_brs(line):
    """Replace all whitespace (line breaks, etc) with spaces."""
    return ' '.join(line.split())


def get_data(url, debug=False, kwargs={}):
    """Return response from generic get request for data object."""
    if debug:
        logging.debug(ic('GET: `{}`'.format(url)))
    raw = requests.get(url, kwargs)
    try:
        resp = raw.json()
        if debug:
            logging.debug(ic(resp))
        time.sleep(0.1)
        return resp
    except json.decoder.JSONDecodeError as e:
        ic('{}\nFailed to parse response from: {}\n{}\n'.format('=' * 80, url, raw.text))
        raise e


def get_kitsu(endpoint, debug=False):
    """Basic Get request to KitsuAPI."""
    base_url = 'https://kitsu.io/api/edge/'
    return get_data('{}{}'.format(base_url, endpoint), debug)


def run(username=None):
    """TODO: Split into functions.

    username -- optional Kitsu user name. Otherwise falls back to input()

    """
    # Init the CSV output file with legend
    out_fn = 'summary.csv'
    legend = [
        'canonicalTitle', 'synopsis', 'My Status', 'progress',  'showType',
        'averageRating', 'userCount', 'favoritesCount', 'popularityRank', 'ratingRank', 'ageRating', 'status',
        'startDate', 'endDate', 'nextRelease', 'posterImage', 'episodeCount', 'episodeLength', 'totalLength',
        'Stream Count', 'funimation', 'crunchyroll', 'hulu', 'amazon', 'netflix', 'tubitv', 'hidive', 'viewster'
    ]
    with open(out_fn, 'w') as csv_file:
        csv.writer(csv_file).writerow(legend)

    if username is None:
        username = input('Type your Kitsu username and press enter: ').strip()

    # Get user ID
    data = get_kitsu('users?filter[name]={}'.format(username))['data']
    my_id = int(data[0]['id'])

    # Loop through a user's library
    lib_entry = get_kitsu('users/{}/library-entries?filter[kind]=anime'.format(my_id))
    while lib_entry:
        logging.debug('======== Library Entry ========')
        this_entry = lib_entry
        # >>logging.debug(ic.format(this_entry))
        for entry_data in this_entry['data']:
            # Store user's ratings and info
            entry_attr = entry_data['attributes']
            status = entry_attr['status']
            # Check is status is one of planned, on_hold, or currently watching (?)
            if status not in ['dropped', 'completed']:
                # Get anime specific information
                logging.debug('---- Anime ----')
                anime = get_data(
                    entry_data['relationships']['anime']['links']['related'],
                    kwargs={'include': 'categories'},
                )
                # >>logging.debug(ic.format(anime))
                anime_attr = anime['data']['attributes']

                # ic(anime_attr)
                # ic(anime_attr['slug'])
                categories = [attr['attributes']['slug'] for attr in anime['included']]

                data = {
                    'id': entry_data['id'],
                    'createdAt': entry_attr['createdAt'],
                    'updatedAt': entry_attr['updatedAt'],
                    'My Status': status,
                    'progress': entry_attr['progress'],
                    'notes': entry_attr['notes'],
                    'private': entry_attr['private'],
                    'progressedAt': entry_attr['progressedAt'],
                    'startedAt': entry_attr['startedAt'],
                    'finishedAt': entry_attr['finishedAt'],
                    'ratingTwenty': entry_attr['ratingTwenty'],

                    'canonicalTitle': anime_attr['canonicalTitle'],
                    'slug': anime_attr['slug'],
                    'synopsis': rm_brs(anime_attr['synopsis']),
                    'averageRating': anime_attr['averageRating'],
                    'userCount': anime_attr['userCount'],
                    'favoritesCount': anime_attr['favoritesCount'],
                    'startDate': anime_attr['startDate'],
                    'endDate': anime_attr['endDate'],
                    'nextRelease': anime_attr['nextRelease'],
                    'popularityRank': anime_attr['popularityRank'],
                    'ratingRank': anime_attr['ratingRank'],
                    'ageRating': anime_attr['ageRating'],
                    # 'subtype': anime_attr['subtype'],
                    'status': anime_attr['status'],
                    'posterImage': anime_attr['posterImage']['original'],
                    'episodeCount': anime_attr['episodeCount'],
                    'episodeLength': anime_attr['episodeLength'],
                    'totalLength': anime_attr['totalLength'],
                    'showType': anime_attr['showType']
                }

                # Get streaming links
                logging.debug('---- Streams Entry ----')
                streams = get_data(anime['data']['relationships']['streamingLinks']['links']['related'])
                # >>logging.debug(ic.format(streams))
                data['Stream Count'] = streams['meta']['count']
                if int(streams['meta']['count']) != 0:
                    for stream in streams['data']:
                        stream_url = stream['attributes']['url']
                        key = urlparse(stream_url).netloc
                        try:
                            key = urlparse(stream_url).netloc.split('.')[1]
                        except IndexError:
                            pass
                        data[key] = stream_url

                # Add data as new line to CSV file
                with open(out_fn, 'a') as csv_file:
                    csv.writer(csv_file).writerow([data[leg] if (leg in data) else '---' for leg in legend])

        # Check if there is a 'next' URL available
        try:
            url = this_entry['links']['next']
            ic('Fetching: {}'.format(url))
            lib_entry = get_data(url)

            # raise AttributeError('BREAK!')  # FIXME: remove!
        except (AttributeError, KeyError) as err:
            lib_entry = False
            ic(err)
