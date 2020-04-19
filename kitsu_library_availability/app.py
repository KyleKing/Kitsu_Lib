"""Main application."""

import logging

from icecream import ic

from .analysis import merge_anime_info
from .api_helpers import STORE_PATH, get_anime, get_library, get_user_id
from .kitsu_helpers import get_data, pretty_dump_json

logging.basicConfig(filename='app_debug.log', filemode='w', level=logging.DEBUG)
