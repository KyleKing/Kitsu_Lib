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


def rmBrs(line):
    """Replace all whitespace (line breaks, etc) with spaces."""
    return ' '.join(line.split())


def get(URL, debug=False, kwargs={}):
    """Generic Get request for data object."""
    if debug:
        logging.debug(ic('GET: `{}`'.format(URL)))
    raw = requests.get(URL, kwargs)
    try:
        resp = raw.json()
        if debug:
            logging.debug(ic(resp))
        time.sleep(0.1)
        return resp
    except json.decoder.JSONDecodeError as e:
        ic('{}\nFailed to parse response from: {}\n{}\n'.format('=' * 80, URL, raw.text))
        raise e


def getKitsu(endpoint, debug=False):
    """Basic Get request to KitsuAPI."""
    baseURL = 'https://kitsu.io/api/edge/'
    return get('{}{}'.format(baseURL, endpoint), debug)


def run(username=None):
    """TODO: Split into functions.

    username -- optional Kitsu user name. Otherwise falls back to input()

    """
    # Init the CSV output file with legend
    outFn = 'summary.csv'
    legend = [
        'canonicalTitle', 'synopsis', 'My Status', 'progress',  'showType',
        'averageRating', 'userCount', 'favoritesCount', 'popularityRank', 'ratingRank', 'ageRating', 'status',
        'startDate', 'endDate', 'nextRelease', 'posterImage', 'episodeCount', 'episodeLength', 'totalLength',
        'Stream Count', 'funimation', 'crunchyroll', 'hulu', 'amazon', 'netflix', 'tubitv', 'hidive', 'viewster'
    ]
    with open(outFn, 'w') as csvfile:
        csv.writer(csvfile).writerow(legend)

    if username is None:
        username = input('Type your Kitsu username and press enter: ').strip()

    # Get user ID
    data = getKitsu('users?filter[name]={}'.format(username))['data']
    myID = int(data[0]['id'])

    # Loop through a user's library
    libEntry = getKitsu('users/{}/library-entries?filter[kind]=anime'.format(myID))
    while libEntry:
        logging.debug('======== Library Entry ========')
        thisEntry = libEntry
        # >>logging.debug(ic.format(thisEntry))
        for libEData in thisEntry['data']:
            # Store user's ratings and info
            libEAttr = libEData['attributes']
            status = libEAttr['status']
            # Check is status is one of planned, on_hold, or currently watching (?)
            if status not in ['dropped', 'completed']:
                # Get anime specific information
                logging.debug('---- Anime ----')
                anime = get(libEData['relationships']['anime']['links']['related'], kwargs={'include': 'categories'})
                # >>logging.debug(ic.format(anime))
                animeAttr = anime['data']['attributes']

                # ic(animeAttr)
                # ic(animeAttr['slug'])
                categories = [attr['attributes']['slug'] for attr in anime['included']]

                data = {
                    'id': libEData['id'],
                    'createdAt': libEAttr['createdAt'],
                    'updatedAt': libEAttr['updatedAt'],
                    'My Status': status,
                    'progress': libEAttr['progress'],
                    'notes': libEAttr['notes'],
                    'private': libEAttr['private'],
                    'progressedAt': libEAttr['progressedAt'],
                    'startedAt': libEAttr['startedAt'],
                    'finishedAt': libEAttr['finishedAt'],
                    'ratingTwenty': libEAttr['ratingTwenty'],

                    'canonicalTitle': animeAttr['canonicalTitle'],
                    'slug': animeAttr['slug'],
                    'synopsis': rmBrs(animeAttr['synopsis']),
                    'averageRating': animeAttr['averageRating'],
                    'userCount': animeAttr['userCount'],
                    'favoritesCount': animeAttr['favoritesCount'],
                    'startDate': animeAttr['startDate'],
                    'endDate': animeAttr['endDate'],
                    'nextRelease': animeAttr['nextRelease'],
                    'popularityRank': animeAttr['popularityRank'],
                    'ratingRank': animeAttr['ratingRank'],
                    'ageRating': animeAttr['ageRating'],
                    # 'subtype': animeAttr['subtype'],
                    'status': animeAttr['status'],
                    'posterImage': animeAttr['posterImage']['original'],
                    'episodeCount': animeAttr['episodeCount'],
                    'episodeLength': animeAttr['episodeLength'],
                    'totalLength': animeAttr['totalLength'],
                    'showType': animeAttr['showType']
                }

                # Get streaming links
                logging.debug('---- Streams Entry ----')
                streams = get(anime['data']['relationships']['streamingLinks']['links']['related'])
                # >>logging.debug(ic.format(streams))
                data['Stream Count'] = streams['meta']['count']
                if int(streams['meta']['count']) != 0:
                    for stream in streams['data']:
                        streamURL = stream['attributes']['url']
                        key = urlparse(streamURL).netloc
                        try:
                            key = urlparse(streamURL).netloc.split('.')[1]
                        except IndexError:
                            pass
                        data[key] = streamURL

                # Add data as new line to CSV file
                with open(outFn, 'a') as csvfile:
                    csv.writer(csvfile).writerow([data[leg] if (leg in data) else '---' for leg in legend])

        # Check if there is a 'next' URL available
        try:
            url = thisEntry['links']['next']
            ic('Fetching: {}'.format(url))
            libEntry = get(url)

            # raise AttributeError('BREAK!')  # FIXME: remove!
        except (AttributeError, KeyError) as err:
            libEntry = False
            ic(err)
