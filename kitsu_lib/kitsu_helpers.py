"""General helpers for the kitsu_lib package."""

import csv
import logging
import time
from pathlib import Path

LOGGER = logging.getLogger('kitsu')
"""Module logger instance."""


def configure_logger():
    """Configure LOGGER to output to a new file on each call.

    See guides on configuring logging and best practices

    - https://www.digitalocean.com/community/tutorials/how-to-use-logging-in-python-3
    - https://www.loggly.com/ultimate-guide/python-logging-basics/
    - https://docs.python.org/3/howto/logging-cookbook.html
    - https://docs.python.org/3/library/logging.handlers.html#rotatingfilehandler
    - https://stackoverflow.com/a/44718431/3219667
    - https://docs.python-guide.org/writing/logging/
    - https://pymotw.com/3/logging/

    - https://blog.muya.co.ke/configuring-multiple-loggers-python/
    - https://dzone.com/articles/python-how-to-create-an-exception-logging-decorato

    """
    log_dir = Path(__file__).parent / 'logs'
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        filemode='w',
        filename=log_dir / f'app_debug-{time.time()}.log',
        format='%(asctime)s\t%(levelname)s\t%(filename)s:%(lineno)d\t%(funcName)s():\t%(message)s',
        level=logging.DEBUG,
    )


def rm_brs(line):
    """Replace all whitespace (line breaks, etc) with spaces."""  # noqa: DAR101,DAR201
    return ' '.join(line.split())


def export_table_as_csv(csv_filename, table):
    """Create a CSV file summarizing a table of a dataset database.

    Args:
        csv_filename: Path to csv file
        table: table from dataset database

    """
    with open(csv_filename, 'w', newline='\n', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(table.columns)
        for row in table:
            writer.writerow([*row.values()])
