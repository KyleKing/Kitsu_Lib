"""General helpers for the kitsu_library_availability package."""

import csv


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
