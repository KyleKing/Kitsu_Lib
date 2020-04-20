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
poetry run python scripts/run_scraper.py my_username
```

Launch the Plotly/Dash application for exploring a user's library, with:

```sh
poetry run python scripts/run_app.py
```

See `scripts/` for other files

## Testing

Examples of other useful commands for testing, documentation, and more:

```sh
poetry run ptw -- -m "not CHROME"
poetry run doit run test
poetry run doit
```

## Development Notes

Tasks:

- QUEUE
  - Add tests to >80% coverage (currently 55%)
    - Improve tests and add additional conditions
  - Write tables for each of library entry, streams, and anime / use "slug" to connect data
    - Look into `from pandas.io.json import json_normalize` / `json_normalize(thing['data'])`
    - Or use flatdict / `from sklearn.feature_extraction import DictVectorizer` ([see issue](https://github.com/scikit-learn/scikit-learn/issues/7652#issuecomment-253649565))
  - Create Dash table to filter by streaming platform, category, and rating
    - Use pandas to load the tables into memory
  - ex_px variation - notes:
    - Along bottom of screen - file select - give keyword name to select from dropdowns for each px app/tab
      - This way multiple data sets can be loaded in PD DataFrames
    - In dropdown option of default or loaded data
    - Data should be tidy, then regular dropdown can be used
    - Should show table with data below input
  - Start implementation of exploratory Dash app
    - Make sure relevant data is in Tidy data format - connect to the px demo app from dash_charts
    - Create custom views. Could be good to see distribution of scores for an anime and where my score falls
- Planned
  - Add Cerberus validation to tests and to check downloaded responses
  - Write function to handle keeping local database in sync as library entries could be removed or moved between lists - would likely want to check for list changes (change number of episodes, chapters, moved to complete, etc.) and force a re-download of the relevant data or removal of data if removed from lists

Other notes related to development:

- See various TODO/FIXME comments in code
- May want to look into the AniList GraphQL API: [anilist-api-v2-docs](https://anilist.gitbook.io/anilist-apiv2-docs/) or the APIs used in: [wopian/tracker-killer#anime](https://github.com/wopian/tracker-killer#anime)

## Coverage

Latest coverage table

<!-- COVERAGE -->

| File | Statements | Missing | Excluded | Coverage |
| --: | --: | --: | --: | --: |
| `kitsu_library_availability/__init__.py` | 3 | 0 | 0 | 100.0 |
| `kitsu_library_availability/analysis.py` | 55 | 5 | 0 | 90.9 |
| `kitsu_library_availability/api_helpers.py` | 54 | 39 | 0 | 27.8 |
| `kitsu_library_availability/app.py` | 3 | 0 | 0 | 100.0 |
| `kitsu_library_availability/cache_helpers.py` | 43 | 19 | 0 | 55.8 |
| `kitsu_library_availability/kitsu_helpers.py` | 17 | 0 | 0 | 100.0 |
| `kitsu_library_availability/scraper.py` | 39 | 33 | 0 | 15.4 |

Generated on: 2020-04-19T22:46:40.308063

<!-- /COVERAGE -->
