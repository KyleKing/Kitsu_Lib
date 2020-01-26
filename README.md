# Kitsu-Library-Where-Stream

> Check streaming availability for anime in user's Kitsu library

The app queries the Kitsu API for a specified user's anime library, then creates a CSV with the anime and streaming links (if any). Open an issue if you have any questions or issues.

## Quick Start

If you have Python ^3.6 and the required packages from `poetry.toml` (`requests`). You can quickly run this app with `python main.py my_username` (replace my_username with your actual Kitsu username)

The app is best run with Poetry ([https://github.com/sdispater/poetry](https://github.com/sdispater/poetry#installation)). Run `poetry install` and `poetry run python main.py my_username`

## Testing

With `poetry` installed, run `poetry run pytest -x`
