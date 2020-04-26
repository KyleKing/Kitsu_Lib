"""Run the Kitsu tool. Pass your username as an argument (poetry run python main.py my_username)`."""

import sys

from kitsu_lib import scraper

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise RuntimeError(f'Expected username as CLI argument. Received: {sys.argv[1:]}')

    scraper.scrape_kitsu(username=sys.argv[1], limit=100)
