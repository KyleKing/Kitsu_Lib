"""Test the analysis.py file."""

import json

from kitsu_library_availability.analysis import (create_kitsu_database, filter_stream_urls, merge_anime_info,
                                                 parse_categories, summarize_streams)

from .configuration import TEST_DATA_DIR

# FYI: ^ Will rework functions in this file. Expect these to change

USER = json.loads((TEST_DATA_DIR / 'user.json').read_text())
"""Example user response."""

LIB_ENTRY = json.loads((TEST_DATA_DIR / 'lib_entry.json').read_text())
"""Example lib_entry response."""

STREAMS = json.loads((TEST_DATA_DIR / 'streams.json').read_text())
"""Example streams response."""

ANIME = json.loads((TEST_DATA_DIR / 'anime.json').read_text())
"""Example anime response."""


def test_filter_stream_urls():
    """Test_filter_stream_urls."""
    expected_urls = [
        'https://www.amazon.com/gp/video/detail/B06VW8K7ZJ/',
        'http://www.crunchyroll.com/cowboy-bebop',
        'https://www.hulu.com/cowboy-bebop',
        'http://www.funimation.com/shows/43625',
        'http://tubitv.com/series/2052/cowboy_bebop',
    ]

    urls = filter_stream_urls(STREAMS)  # act

    assert urls == expected_urls


def test_summarize_streams():
    """Test_summarize_streams."""
    expected_summary = {
        'amazon': 'https://www.amazon.com/gp/video/detail/B06VW8K7ZJ/',
        'crunchyroll': 'http://www.crunchyroll.com/cowboy-bebop',
        'hulu': 'https://www.hulu.com/cowboy-bebop',
        'funimation': 'http://www.funimation.com/shows/43625',
        'tubitv': 'http://tubitv.com/series/2052/cowboy_bebop',
    }

    summary = summarize_streams(STREAMS)  # act

    assert summary == expected_summary


def test_parse_categories():
    """Test_parse_categories."""
    expected_categories = [
        'science-fiction', 'space', 'drama', 'action', 'space-travel', 'post-apocalypse', 'other-planet',
        'future', 'shipboard', 'detective', 'bounty-hunter', 'gunfights', 'adventure', 'comedy',
    ]

    categories = parse_categories(ANIME)  # act

    assert categories == expected_categories


def test_merge_anime_info():
    """Test_merge_anime_info."""
    expected_data = {
        'ageRating': 'R',
        'amazon': 'https://www.amazon.com/gp/video/detail/B06VW8K7ZJ/',
        'averageRating': '82.69',
        'canonicalTitle': 'Cowboy Bebop',
        'categories': [
            'science-fiction', 'space', 'drama', 'action', 'space-travel', 'post-apocalypse', 'other-planet',
            'future', 'shipboard', 'detective', 'bounty-hunter', 'gunfights', 'adventure', 'comedy',
        ],
        'createdAt': '2018-10-15T01:26:50.783Z',
        'crunchyroll': 'http://www.crunchyroll.com/cowboy-bebop',
        'endDate': '1999-04-24',
        'episodeCount': 26,
        'episodeLength': 25,
        'favoritesCount': 4380,
        'finishedAt': None,
        'funimation': 'http://www.funimation.com/shows/43625',
        'hulu': 'https://www.hulu.com/cowboy-bebop',
        'id': '36121977',
        'favoritesCount': 4380,
        'finishedAt': None,
        'funimation': 'http://www.funimation.com/shows/43625',
        'hulu': 'https://www.hulu.com/cowboy-bebop',
        'id': '36121977',
        'nextRelease': None,
        'notes': None,
        'popularityRank': 24,
        'posterImage': 'https://media.kitsu.io/anime/poster_images/1/original.jpg?1431697256',
        'private': False,
        'progress': 6,
        'progressedAt': '2020-04-03T01:38:56.762Z',
        'ratingRank': 73,
        'ratingTwenty': None,
        'showType': 'TV',
        'slug': 'cowboy-bebop',
        'startDate': '1998-04-03',
        'startedAt': '2020-01-04T15:02:36.103Z',
        'status': 'finished',
        'subtype': None,
        'synopsis': ('In the year 2071, humanity has colonized several of the planets '
                     'and moons of the solar system leaving the now uninhabitable '
                     'surface of planet Earth behind. The Inter Solar System Police '
                     'attempts to keep peace in the galaxy, aided in part by outlaw '
                     'bounty hunters, referred to as "Cowboys". The ragtag team aboard '
                     'the spaceship Bebop are two such individuals. Mellow and '
                     'carefree Spike Spiegel is balanced by his boisterous, pragmatic '
                     'partner Jet Black as the pair makes a living chasing bounties '
                     'and collecting rewards. Thrown off course by the addition of new '
                     'members that they meet in their travels—Ein, a genetically '
                     'engineered, highly intelligent Welsh Corgi; femme fatale Faye '
                     'Valentine, an enigmatic trickster with memory loss; and the '
                     'strange computer whiz kid Edward Wong—the crew embarks on '
                     "thrilling adventures that unravel each member's dark and "
                     'mysterious past little by little. Well-balanced with high '
                     'density action and light-hearted comedy, Cowboy Bebop is a space '
                     'Western classic and an homage to the smooth and improvised music '
                     'it is named after. [Written by MAL Rewrite]'),
        'totalLength': 626,
        'tubitv': 'http://tubitv.com/series/2052/cowboy_bebop',
        'updatedAt': '2020-04-03T01:38:56.763Z',
        'userCount': 106156,
        'watch_status': 'dropped',
    }
    anime_entry_data = LIB_ENTRY['data'][0]

    data = merge_anime_info(anime_entry_data, ANIME, STREAMS)  # act

    assert data == expected_data


def test_create_kitsu_database():
    """Test_create_kitsu_database."""
    summary_file_path = TEST_DATA_DIR / 'all_data.json'

    create_kitsu_database(summary_file_path)  # act

    # TODO: test database created from summary file!
    # WIP: assert db.get_table('anime').distinct('something') == ['vash', 'cowboy']
