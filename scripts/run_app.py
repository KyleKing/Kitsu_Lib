"""Launch the Plotly/Dash application for exploring user library."""

from dash_charts.dash_helpers import parse_dash_cli_args
from kitsu_lib.app import KitsuExplorer

instance = KitsuExplorer
if __name__ == '__main__':
    app = instance()
    app.create()
    app.run(**parse_dash_cli_args())
else:
    app = instance()
    app.create()
    FLASK_HANDLE = app.get_server()
