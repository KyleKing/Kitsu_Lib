# Kitsu-Library-Where-Stream

> Check streaming availability for anime in Kitsu library

The app queries the Kitsu API for a specified user's anime library, then creates a CSV with the anime and streaming links (if any)

This project is WIP and generally works. If I have time, I'll probably improve the test and documentation. Open an issue if you run into any trouble
Open an issue if you have a different library to search.

## Quick Start

If you have Python ^3.6 and the required packages from `poetry.toml` (`requests`). You can run this app with `python kitsu_library_availability/app.py`

The more reliable way is to install Poetry ([https://github.com/sdispater/poetry](https://github.com/sdispater/poetry#installation)). Then run `poetry install` and `poetry run python kitsu_library_availability/app.py`.

## Testing

With `poetry` installed, run `poetry shell` then `pytest`
