"""General Exploratory Dashboard Interface."""
# PLANNED: Generalize and move to Dash_Charts

import re
import time
from datetime import datetime

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.express as px
from dash.exceptions import PreventUpdate
from dash_charts.components import dropdown_group, opts_dd
from dash_charts.modules_datatable import ModuleFilteredTable
from dash_charts.utils_app_modules import DataCache
from dash_charts.utils_app_with_navigation import AppWithTabs
from dash_charts.utils_callbacks import map_args, map_outputs
from icecream import ic

from .app_tabs import InstructionsTab, TabIris, TabTip
from .upload_module import UploadModule

# add popup module with datatable vertically so that all data fits (add column that says "more" with button that will
#   open and populate the modal)

# Create Data Module
#  > See dbc form: https://dash-bootstrap-components.opensource.faculty.ai/docs/components/input/
# (*) [1/2-storage] Create single SQLite DB file to hold upload dataframes
#     > Show error if failed to parse data source
#     > For each upload file, create table with filename and dump user uploaded data (use dataset for SQL management
#           and to check if tables exists already - may need pandas to load CSV/JSON data first before dumping into SQL
#           with dataset)
#     > Create main table that stores meta information on each table - date added, source filename (with full path?),
#       (last accessed?), etc.
#     > Add dcc.Input to select SQL table and table to show raw data (use dash_charts table class)

# ( ) [2/2-storage] Create user-specific SQLite DB file f'{username}.db'. Have user enter username, which could be
#   stored in URL or in dcc.Store(). This defines which SQLite database is loaded

# ( ) Edge Cases
#     > Allow user to clear data (either specific tables or all database)
#     > show table of raw data (handle really wide tables - clip columns?)
#     > If uploading a file with the same name - offer to clear already uploaded data or if a new name should be
#       entered (prompt user for input suggesting "-1"/"-2"/etc)

# ( ) Allow selecting of the datatable from SQL, then update the inputs so that the selected data can be charted in the
#   px charts (like the demo px.Tips data is shown now) - need to get column names, update dataframe in tab, etc.


# ( ) Visualization
#     > Create Dash_Charts table to filter by streaming platform, category, and rating
#     > Create custom views. Could be good to see distribution of scores for an anime and where my score falls

# Other notes
# > PLANNED: Make sure the tab navigation fits within the boundary - currently blocks any rows above/below the tabs if
#   not the only thing in the app
# > PLANNED: Make the tabs and chart compact as well when the compact argument is set to True
# > PLANNED: select chart types from type and generate multiple charts on same page?
#   > Need way to store state of charts when switching tabs...
# > methods for conerting to and from `dcc.Store`: df_to_store() // store_to_df()
# > Maybe popover will be useful for describing inputs?
#   https://dash-bootstrap-components.opensource.faculty.ai/docs/components/popover/
# > Maybe auto-delete data after 30 days of inactivity?
#
# > ex_px variation - notes:
#   > Along bottom of screen - file select - give keyword name to select from dropdowns for each px app/tab
#     > This way multiple data sets can be loaded in PD DataFrames
#   > In dropdown option of default or loaded data
#   > Data should be tidy, then regular dropdown can be used
#   > Should show table with data below input
# > Pdoc3 search? {May not work for local docs, but checkout how pdoc does it's pdoc:
#   https://github.com/pdoc3/pdoc/blob/master/doc/pdoc_template/}


# PLANNED: HOIST TO DASH_CHARTS
def get_triggered_id():
    """Use Dash context to get the id of the input element that triggered the callback.

    See advanced callbacks: https://dash.plotly.com/advanced-callbacks

    Returns:
        str: id of the input that triggered the callback

    Raises:
        PreventUpdate: if callback was fired without an input

    """
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    prop_id = ctx.triggered[0]['prop_id']  # in format: `id.key` where we only want the `id`
    return re.search(r'(^.+)\.[^\.]+$', prop_id).group(1)


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

    id_modal = 'modal'
    """Unique name for the pop-up modal."""

    id_modal_close = 'modal-close'
    """Unique name for the close button of the pop-up modal."""

    id_wip_button = 'button-wip'
    """Placeholder button ID for testing."""

    mod_table = ModuleFilteredTable('filtered_table')
    """Main table module (DataTable)."""

    mod_cache = DataCache('user_session')
    """Data cache module for storing session information."""

    mod_upload = UploadModule('main_upload')
    """Upload module for loading data."""

    def initialization(self):
        """Initialize ids with `self.register_uniq_ids([...])` and other one-time actions."""
        super().initialization()
        self.register_uniq_ids([self.id_modal, self.id_modal_close, self.id_wip_button])

        # Register modules
        self.modules = [self.mod_table, self.mod_cache, self.mod_upload]

    def find_user(self, username):
        """Return the database row for the specified user.

        Args:
            username: string username

        Returns:
            dict: for row from table or None if no match

        """
        return self.user_table.find_one(username=username)

    def add_user(self, username):
        """Add the user to the table or update the user's information if already registered.

        Args:
            username: string username

        """
        now = time.time()
        if self.find_user(username):
            self.user_table.upsert({'username': username, 'last_loaded': now}, ['username'])
        else:
            self.user_table.insert({'username': username, 'creation': now, 'last_loaded': now})

    def upload_data(self, username, df_name, df_upload):
        """Store dataframe in database for specified user.

        Args:
            username: string username
            df_name: name of the stored dataframe
            df_upload: pandas dataframe to store

        """
        now = time.time()
        table_name = f'{username}-{df_name}-{int(now)}'
        self.inventory_table.insert({'table_name': table_name, 'df_name': df_name, 'username': username,
                                     'creation': now})
        table = self.database.db.create_table(table_name)
        table.insert_many(df_upload.to_dict(orient='records'))

    def get_data(self, table_name):
        """Retrieve stored data for specified dataframe name.

        Args:
            table_name: unique name of the table to retrieve

        Returns:
            pd.DataFrame: pandas dataframe retrieved from the database

        """
        table = self.database.db.load_table(table_name)
        return pd.DataFrame.from_records(table.all())

    def delete_data(self, table_name):
        """Remove specified data from the database.

        Args:
            table_name: unique name of the table to delete

        """
        self.database.db.load_table(table_name).drop()

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
                dbc.Button('Primary', color='primary', className='mr-1', id=self.ids[self.id_wip_button]),
                super().return_layout(),
            ])], style={'margin': 0, 'padding': 0}),
            html.Hr(),
            dbc.Row([dbc.Col([
                self.mod_upload.return_layout(self.ids),
                self.mod_cache.return_layout(self.ids),
            ])], style={'maxWidth': '90%', 'paddingLeft': '5%'}),

            dbc.Row([dbc.Col([
                html.H2('Data Interaction'),
                html.P(' FIXME: Needs dropdown to select table_name. Filtered data should be applied to px chart'),
                self.mod_table.return_layout(self.ids, px.data.gapminder()),
            ])], style={'maxWidth': '90%', 'paddingLeft': '5%'}),

            dbc.Modal([
                dbc.ModalHeader('Module Header'),
                dbc.ModalBody('Module body text'),
                dbc.ModalFooter(dbc.Button('Close', id=self.ids[self.id_modal_close], className='ml-auto')),
            ], backdrop='static', centered=True, id=self.ids[self.id_modal]),
        ])

    def create_callbacks(self):
        """Create Dash callbacks."""
        super().create_callbacks()
        self.register_modal_handler()

    def register_modal_handler(self):
        """Handle opening and closing the modal."""
        outputs = [(self.id_modal, 'is_open'), (self.mod_cache.get(self.mod_cache.id_cache), 'data')]
        inputs = [(self.id_wip_button, 'n_clicks'), (self.id_modal_close, 'n_clicks')]
        states = [(self.mod_cache.get(self.mod_cache.id_cache), 'data')]

        @self.callback(outputs, inputs, states)
        def modal_handler(*raw_args):
            a_in, a_state = map_args(raw_args, inputs, states)
            data = a_state[self.mod_cache.get(self.mod_cache.id_cache)]['data']
            if data is None:
                data = {}
            data['username'] = 'username'  # FIXME: Get username from input (pt. 2)

            # Return False (close) only if the close button was clicked
            button_id = get_triggered_id()
            return [button_id != self.ids[self.id_modal_close], data]
