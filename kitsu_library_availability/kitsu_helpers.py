"""General helpers for the kitsu_library_availability package."""


def rm_brs(line):
    """Replace all whitespace (line breaks, etc) with spaces."""  # noqa: DAR101,DAR201
    return ' '.join(line.split())
