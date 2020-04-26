"""General Exploratory Dashboard Interface."""
# PLANNED: Generalize and move to Dash_Charts

import re
import time
from datetime import datetime
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dataset
import numpy as np
import pandas as pd
import plotly.express as px
from dash.exceptions import PreventUpdate
from dash_charts.components import dropdown_group, opts_dd
from dash_charts.modules_datatable import ModuleFilteredTable
from dash_charts.utils_app_modules import DataCache
from dash_charts.utils_app_with_navigation import AppWithTabs
from dash_charts.utils_callbacks import map_args, map_outputs
from icecream import ic

from .app_helpers import parse_uploaded_df
from .app_tabs import InstructionsTab, TabIris, TabTip
from .cache_helpers import CACHE_DIR, DBConnect

# add popup module with datatable vertically so that all data fits (add column that says "more" with button that will open and populate the modal)

# Create Data Module
#  > See dbc form: https://dash-bootstrap-components.opensource.faculty.ai/docs/components/input/
# (*) [1/2-storage] Create single SQLite DB file to hold upload dataframes
#     > Show error if failed to parse data source
#     > For each upload file, create table with filename and dump user uploaded data (use dataset for SQL management and to check if tables exists already - may need pandas to load CSV/JSON data first before dumping into SQL with dataset)
#     > Create main table that stores meta information on each table - date added, source filename (with full path?), (last accessed?), etc.
#     > Add dcc.Input to select SQL table and table to show raw data (use dash_charts table class)

# ( ) [2/2-storage] Create user-specific SQLite DB file f'{username}.db'. Have user enter username, which could be stored in URL or in dcc.Store(). This defines which SQLite database is loaded

# ( ) Update static tab with example data_table of tidy data and links to more explanation
#     dash_table.DataTable(
#         data=df_example_tidy.to_dict('records'),
#         columns=[{'name': i, 'id': i} for i in df_example_tidy.columns]
#     ),

# ( ) Edge Cases
#     > Allow user to clear data (either specific tables or all database)
#     > show table of raw data (handle really wide tables - clip columns?)
#     > If uploading a file with the same name - offer to clear already uploaded data or if a new name should be entered (prompt user for input suggesting "-1"/"-2"/etc)

# ( ) Allow selecting of the datatable from SQL, then update the inputs so that the selected data can be charted in the px charts (like the demo px.Tips data is shown now) - need to get column names, update dataframe in tab, etc.


# ( ) Visualization
#     > Create Dash_Charts table to filter by streaming platform, category, and rating
#     > Create custom views. Could be good to see distribution of scores for an anime and where my score falls

# Other notes
# > PLANNED: Make sure the tab navigation fits within the boundary - currently blocks any rows above/below the tabs if not the only thing in the app
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


def show_toast(message, header, icon='warning', style=None):
    """Create toast notification.

    Args:
        message: string body text
        header: string notification header
        icon: string name in `(primary,secondary,success,warning,danger,info,light,dark)`. Default is warning
        style: style dictionary. Default is the top right

    Returns:
        dbc.Toast: toast notification from Dash Bootstrap Components library

    """
    if style is None:
        # Position in the top right (note: will occlude the tabs when open, could be moved elsewhere)
        style = {'position': 'fixed', 'top': 10, 'right': 10, 'width': 350, 'zIndex': 1900}
    return dbc.Toast(message, header=header, icon=icon, style=style, dismissable=True, duration=1000 * 5)


def drop_to_upload(**upload_kwargs):
    """Create drop to upload element. Dashed box of the active area or a clickable link to use the file dialog.

    Based on dash documentation from: https://dash.plotly.com/dash-core-components/upload

    Args:
        upload_kwargs: keyword arguments for th dcc.Upload element. Children and style are reserved

    Returns:
        dcc.Upload: Dash upload element

    """
    return dcc.Upload(
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
        **upload_kwargs,
    )


def get_safe_df_name(df_name):
    """Guard against dataframes names that would conflict with required dataframes.

    Args:
        df_name: name used to store the dataframe

    Returns:
        str: dataframe name

    """
    # TODO: replace any spaces or other characters that aren't allowed in SQL table
    ic(df_name)
    if df_name in ['users', 'inventory']:
        df_name += '-safe'
    return df_name  # f'{username}_{df_name}'


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

    # default_data = px.data.tips()
    # """Default data set used to initialize database. Can be overwritten to simplify testing."""

    def initialization(self):
        """Initialize ids with `self.register_uniq_ids([...])` and other one-time actions."""
        super().initialization()
        self.register_uniq_ids([self.id_upload, self.id_upload_output, self.id_modal, self.id_modal_close,
                                self.id_wip_button])

        # Register modules
        self.modules = [self.mod_table, self.mod_cache]

        self.initialize_database()

    def initialize_database(self):
        """Create data members `self.database` and `self.user_table`."""
        self.database = DBConnect(CACHE_DIR / '_placeholder_app_v3.db')
        self.user_table = self.database.db.create_table(
            'users', primary_id='username', primary_type=self.database.db.types.text)
        self.inventory_table = self.database.db.create_table(
            'inventory', primary_id='df_name', primary_type=self.database.db.types.text)

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
        df_name = get_safe_df_name(df_name)
        now = time.time()
        if df_name not in self.database.db.tables:
            # FIXME: Is upsert not working? This line may be throwing the "UNIQUE" error on `placeholder-1.id`
            self.inventory_table.upsert({'df_name': df_name, 'username': username, 'creation': now}, ['df_name'])

            table = self.database.db.create_table(df_name)
            records = df_upload.to_dict(orient='records')
            table.insert_many(records)

    def list_stored_tables(self, username):
        """Return list of all dataframes stored for the given user.

        Args:
            username: string username

        Returns:
            list: list of table names for stored data

        """
        return [row['df_name'] for row in self.inventory_table.find(username=username)]

    def get_data(self, df_name):
        """Retrieve stored data for specified dataframe name.

        Args:
            df_name: name of the stored dataframe

        Returns:
            pd.DataFrame: pandas dataframe retrieved from the database

        """
        df_name = get_safe_df_name(df_name)
        table = self.database.db.load_table(df_name)
        return pd.DataFrame.from_records(table.all())

    def delete_data(self, df_name):
        """Remove specified data from the database.

        Args:
            df_name: name of the stored dataframe

        """
        self.database.db.load_table(get_safe_df_name(df_name)).drop()

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
            ])], style={'margin': 0, 'padding': 0}),
            html.Hr(),
            dbc.Row([dbc.Col([
                dbc.Button('Primary', color='primary', className='mr-1', id=self.ids[self.id_wip_button]),
                drop_to_upload(id=self.ids[self.id_upload]),
                dcc.Loading(html.Div(id=self.ids[self.id_upload_output]), type='circle'),
                # self.mod_table.return_layout(self.ids, px.data.gapminder()),
                self.mod_cache.return_layout(self.ids),
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
        self.register_upload_handler()

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

    def show_data(self, username):
        """TODO."""
        children = []
        for df_name in self.list_stored_tables(username):
            df_upload = self.get_data(df_name)
            children.extend([
                html.H5(df_name),
                dash_table.DataTable(
                    data=df_upload[:25].to_dict('records'),
                    columns=[{'name': i, 'id': i} for i in df_upload.columns[:10]],
                    style_cell={
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis',
                        'maxWidth': 0,
                    },
                ),
            ])
        return html.Div(children)

    def register_upload_handler(self):
        """Register the upload_handler callbacks."""  # noqa: DAR401
        outputs = [(self.id_upload_output, 'children')]
        inputs = [(self.id_upload, 'contents')]
        states = [(self.id_upload, 'filename'), (self.id_upload, 'last_modified')]

        @self.callback(outputs, inputs, states)
        def upload_handler(*raw_args):
            a_in, a_state = map_args(raw_args, inputs, states)
            b64_file = a_in[self.id_upload]['contents']
            filename = a_state[self.id_upload]['filename']
            timestamp = a_state[self.id_upload]['last_modified']
            username = 'username'  # TODO: IMPLEMENT

            if b64_file is None:
                raise PreventUpdate  # FIXME: TEMPORARY
                df_upload = pd.read_csv(CACHE_DIR / '_database_kitsu.csv')  # , na_values='0')
                filename = 'placeholder-1'
                timestamp = time.time()
            else:
                df_upload = parse_uploaded_df(b64_file, filename, timestamp)

            # df_upload = df_upload.fillna('0')
            df_upload = df_upload.dropna(axis='columns')
            ic(username, filename, df_upload[:1])

            self.add_user(username)
            self.upload_data(username, filename, df_upload)

            return [self.show_data(username)]
