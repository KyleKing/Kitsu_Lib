"""General helpers for the kitsu_library_availability package."""

import json
import logging
import time
from json.decoder import JSONDecodeError
from pathlib import Path

import requests
from icecream import ic


def pretty_dump_json(filename, obj):
    """Write indented JSON file.

    Args:
        filename: Path or plain string JSON filename to write
        obj: JSON object to write

    """
    Path(filename).write_text(json.dumps(obj, indent=4, separators=(',', ': ')))


def rm_brs(line):
    """Replace all whitespace (line breaks, etc) with spaces."""  # noqa: DAR101,DAR201
    return ' '.join(line.split())


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
