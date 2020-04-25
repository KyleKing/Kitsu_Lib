"""General Exploratory Dashboard Interface."""
# PLANNED: Generalize and move to Dash_Charts

from collections import OrderedDict
from pathlib import Path

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
# import dash_table
import pandas as pd
import plotly.express as px
from dash.exceptions import PreventUpdate
from dash_charts.components import dropdown_group, opts_dd
from dash_charts.utils_app_with_navigation import AppWithTabs
from dash_charts.utils_callbacks import map_args, map_outputs

from .app_helpers import parse_uploaded_df
from .app_tabs import InstructionsTab, TabIris, TabTip

#   Require user to submit "Tidy" data with non-value headers
#   > Update static tab with example data_table of tidy data and links to more explanation
#     dash_table.DataTable(
#         data=df_example_tidy.to_dict('records'),
#         columns=[{'name': i, 'id': i} for i in df_example_tidy.columns]
#     ),

# ( ) [1/2-storage] Create single SQLite DB file to hold upload dataframes
#     > Show error if failed to parse data source
#     > For each upload file, create table with filename and dump user uploaded data (use datasete for SQL management and to check if tables exists already - may need pandas to load CSV/JSON data first before dumping into SQL with datasete)
#     > Create main table that stores meta information on each table - date added, source filename (with full path?), (last accessed?), etc.
#     > Add dcc.Input to select SQL table and table to show raw data (use dash_charts table class)

# ( ) [2/2-storage] Create user-specific SQLite DB file f'{username}.db'. Have user enter username, which could be stored in URL or in dcc.Store(). This defines which SQLite database is loaded

# ( ) Edge Cases
#     > Allow user to clear data (either specific tables or all database)
#     > show table of raw data (handle really wide tables - clip columns?)
#     > If uploading a file with the same name - offer to clear already uploaded data or if a new name should be entered (prompt user for input suggesting "-1"/"-2"/etc)

# ( ) Allow selecting of the datatable from SQL, then update the inputs so that the selected data can be charted in the px charts (like the demo px.Tips data is shown now) - need to get column names, update dataframe in tab, etc.


# ( ) Visualization
#     > Create Dash_Charts table to filter by streaming platform, category, and rating
#     > Create custom views. Could be good to see distribution of scores for an anime and where my score falls

# Other notes
# > PLANNED: Make the tabs and chart compact as well when the compact argument is set to True
# > PLANNED: select chart types from type and generate multiple charts on same page?
#   > Need way to store state of charts when switching tabs...
# > methods for conerting to and from `dcc.Store`: df_to_store() // store_to_df()
# > Maybe popover will be useful for describing inputs? https://dash-bootstrap-components.opensource.faculty.ai/docs/components/popover/
# > Maybe auto-delete data after 30 days of inactivity?
#
# > ex_px variation - notes:
#   > Along bottom of screen - file select - give keyword name to select from dropdowns for each px app/tab
#     > This way multiple data sets can be loaded in PD DataFrames
#   > In dropdown option of default or loaded data
#   > Data should be tidy, then regular dropdown can be used
#   > Should show table with data below input
# > Pdoc3 search? {May not work for local docs, but checkout how pdoc does it's pdoc: https://github.com/pdoc3/pdoc/blob/master/doc/pdoc_template/}


class KitsuExplorer(AppWithTabs):  # noqa: H601
    """Kitsu User Dataset Explorer Plotly/Dash Application."""

    name = 'KitsuExplorer'

    external_stylesheets = TabTip.external_stylesheets

    tabs_location = 'right'
    """Tab orientation setting. One of `(left, top, bottom, right)`."""

    tabs_margin = '110px'
    """Adjust this setting based on the width or height of the tabs to prevent the content from overlapping the tabs."""

    tabs_compact = True
    """Boolean setting to toggle between a padded tab layout if False and a minimal compact version if True."""

    id_upload = 'upload-drop-area'
    """Unique name for the upload component."""

    id_upload_output = 'upload-output'
    """Unique name for the div to contain output of the parse-upload."""

    modal = 'modal'
    """Unique name for the pop-up modal."""

    modal_close = 'modal-close'
    """Unique name for the close button of the pop-up modal."""

    def initialization(self):
        """Initialize ids with `self.register_uniq_ids([...])` and other one-time actions."""
        super().initialization()
        self.register_uniq_ids([self.id_upload, self.id_upload_output, self.modal, self.modal_close])

    def define_nav_elements(self):
        """Return list of initialized tabs.

        Returns:
            list: each item is an initialized tab (ex `[AppBase(self.app)]` in the order each tab is rendered

        """
        return [
            TabTip(app=self.app),
            TabIris(app=self.app),
            InstructionsTab(app=self.app),
        ]

    def return_layout(self):
        """Return Dash application layout.

        Returns:
            dict: Dash HTML object

        """
        return html.Div([
            dbc.Row([dbc.Col([
                html.H3('Kitsu Library Explorer', style={'padding': '10px 0 0 10px'}),
                super().return_layout(),
            ])]),
            html.Hr(),
            dbc.Row([dbc.Col([
                dcc.Upload(
                    id=self.ids[self.id_upload],
                    children=html.Div(['Drag and Drop or ', html.A('Select a File')]),
                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px',
                    },
                    multiple=False,
                ),
                html.Div(id=self.ids[self.id_upload_output]),
            ])]),
            # Demo using a modal with form - if additional user information is necessary
            #   dbc form: https://dash-bootstrap-components.opensource.faculty.ai/docs/components/input/
            dbc.Modal(
                [
                    dbc.ModalHeader('Header'),
                    dbc.ModalBody('This is the content of the modal'),
                    dbc.ModalFooter(
                        dbc.Button('Close', id=self.ids[self.modal_close], className='ml-auto')
                    ),
                ],
                backdrop='static',
                centered=True,
                id=self.ids[self.modal],

                # is_open=True,  # Needs to be handled in callback to toggle open state
            ),
            # Example warning
            dbc.Toast(
                'This toast is placed in the top right',
                id='positioned-toast',
                header='Positioned toast',
                dismissable=True,
                duration=1000 * 5,
                # primary|secondary|success|warning|danger|info|light|dark
                icon='danger',
                # Position in the top left (note: will occlude the tabs when open, could be moved elsewhere)
                style={'position': 'fixed', 'top': 10, 'right': 10, 'width': 350, 'zIndex': 1900},

                # is_open=True,  # Needs to be handled in callback to toggle open state
            ),
        ])

    def create_callbacks(self):
        """Create Dash callbacks."""
        super().create_callbacks()
        self.register_upload_handler()

    def register_upload_handler(self):
        """Register the upload_handler callbacks."""
        outputs = [(self.id_upload_output, 'children')]
        inputs = [(self.id_upload, 'contents')]
        states = [(self.id_upload, 'filename'), (self.id_upload, 'last_modified')]

        @self.callback(outputs, inputs, states)
        def upload_handler(*raw_args):
            a_in, a_state = map_args(raw_args, inputs, states)
            b64_file = a_in[self.id_upload]['contents']
            if b64_file is None:
                raise PreventUpdate()

            filename = a_state[self.id_upload]['filename']
            timestamp = a_state[self.id_upload]['last_modified']
            return [parse_uploaded_df(b64_file, filename, timestamp)]
