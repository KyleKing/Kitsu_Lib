"""Test the api_helpers.py file."""

from kitsu_lib.api_helpers import (get_anime, get_data, get_kitsu, get_library, get_streams, get_user, get_user_id,
                                   selective_request)

# def test_get_data():
#     """Test get_data with simple smoke test."""
#     resp = get_data(url, kwargs=None, debug=False)  # act
#
#     assert len(resp['data']) == 1


# def test_selective_request():
#     """Test selective_request with simple smoke test."""
#     resp = selective_request(prefix, url, **get_kwargs)  # act
#
#     assert len(resp['data']) == 1


# def test_get_kitsu():
#     """Test get_kitsu with simple smoke test."""
#     resp = get_kitsu(endpoint, prefix='kitsu', **kwargs)  # act
#
#     assert len(resp['data']) == 1


# def test_get_user():
#     """Test get_user with simple smoke test."""
#     resp = get_user(username)  # act
#
#     assert len(resp['data']) == 1


# def test_get_user_id():
#     """Test get_user_id with simple smoke test."""
#     resp = get_user_id(username)  # act
#
#     assert len(resp['data']) == 1


# def test_get_library():
#     """Test get_library with simple smoke test."""
#     resp = get_library(user_id, is_anime=True)  # act
#
#     assert len(resp['data']) == 1


# def test_get_anime():
#     """Test get_anime with simple smoke test."""
#     resp = get_anime(anime_link)  # act
#
#     assert len(resp['data']) == 1


# def test_get_streams():
#     """Test get_streams with simple smoke test."""
#     resp = get_streams(stream_link)  # act
#
#     assert len(resp['data']) == 1
