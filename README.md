# Kitsu_Library_Availability

While originally only built to find legal streaming links for a user's Kitsu watch list, I have since added a dashboard with Plotly/Dash to filter for ratings, categories, and other attributes to help choose what to watch.

The Python package uses the [KitsuAPI](https://kitsu.docs.apiary.io/#) and tries to cache as much as possible to avoid too many calls

Open an issue if you have any questions or run into any issues

## Quick Start

Initial commands to clone code from Github, create Python virtual environment, and run first example application. Replace `my_username` with your actual Kitsu username

```sh
git clone https://github.com/KyleKing/kitsu_library_availability.git
cd kitsu_library_availability
poetry install
poetry run python main.py my_username
```

## Testing

Examples of other useful commands for testing, documentation, and more:

```sh
poetry run ptw -- -m "not CHROME"
poetry run doit run test
poetry run doit
```

## Dev Notes

Other notes related to development:

- See various TODO/FIXME comments in code
- May want to look into the AniList GraphQL API: https://anilist.gitbook.io/anilist-apiv2-docs/ or the APIs used in: https://github.com/wopian/tracker-killer#anime
