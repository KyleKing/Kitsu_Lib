# kitsu_lib

**Archival Update**: this was a good project to experiment with web scraping and caching, but my watch list is so small (<20) that I no longer need any kind of scripting. `Reelgood` has such a [great (paid) database](https://www.protocol.com/reelgood) that this wouldn't make sense to expand in for my broader watch list

This project was [built on `dash_dev`](https://github.com/KyleKing/Kitsu_Lib/blob/main/poetry.lock#L395), the precursor to calcipy. `Kitsu_lib` won't run out-of-the-box, but with the help of [`calcipy_template` could be ported](https://github.com/KyleKing/calcipy_template) to the latest version of calcipy

---

Check streaming availability for anime in Kitsu library (Crunchyroll, Funimation, Netflix, Hulu, Amazon, Tubi, etc.)

The Python package uses the [KitsuAPI](https://kitsu.docs.apiary.io/#) and caches responses to minimize calls

Open an issue if you have any questions or run into any issues

## Quick Start

Initial commands to clone code from Github, create Python virtual environment, and run first example application. Replace `my_username` with your actual Kitsu username

```sh
git clone https://github.com/KyleKing/kitsu_lib.git
cd kitsu_lib
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
  - Write tables for each of library entry, streams, and anime / use "slug" to connect data
    - Look into `from pandas.io.json import json_normalize` / `json_normalize(thing['data'])`
    - Or use flatdict / `from sklearn.feature_extraction import DictVectorizer` ([see issue](https://github.com/scikit-learn/scikit-learn/issues/7652#issuecomment-253649565))
  - Add tests to >80% coverage (currently 55%)
    - Improve tests and add additional conditions
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
| `kitsu_lib/__init__.py` | 3 | 0 | 0 | 100.0 |
| `kitsu_lib/analysis.py` | 53 | 4 | 0 | 92.5 |
| `kitsu_lib/api_helpers.py` | 54 | 39 | 0 | 27.8 |
| `kitsu_lib/app.py` | 60 | 3 | 0 | 95.0 |
| `kitsu_lib/app_helpers.py` | 45 | 30 | 0 | 33.3 |
| `kitsu_lib/app_tabs.py` | 102 | 12 | 0 | 88.2 |
| `kitsu_lib/cache_helpers.py` | 43 | 19 | 0 | 55.8 |
| `kitsu_lib/kitsu_helpers.py` | 17 | 0 | 0 | 100.0 |
| `kitsu_lib/scraper.py` | 39 | 33 | 0 | 15.4 |
| `kitsu_lib/upload_module.py` | 90 | 25 | 0 | 72.2 |

Generated on: 2020-04-26T22:34:44.222860

<!-- /COVERAGE -->
