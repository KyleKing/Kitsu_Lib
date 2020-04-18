# Kitsu-Library-Where-Stream

> Check streaming availability for anime in a user's Kitsu library

The app queries the Kitsu API for a specified user's anime library, then creates a CSV with the anime and any streaming links that Kitsu reports

Open an issue if you have any questions or issues.

## Quick Start

Initial commands to clone code from Github, create Python virtual environment, and run first example application. Replace `my_username` with your actual Kitsu username

```sh
git clone https://github.com/KyleKing/kitsu_library_availability.git
cd kitsu_library_availability
poetry install
poetry run python main.py my_username
```

## Testing

Other useful scripts for testing, documentation, and more:

```sh
poetry run ptw -- -m "not CHROME"
poetry run doit run test
poetry run doit
```

## Links

Also checkout the AniList GraphQL API: https://anilist.gitbook.io/anilist-apiv2-docs/
