"""Exploratory Dashboard Interface."""

import base64
import io
from collections import OrderedDict
from datetime import datetime
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
# import dash_table
import pandas as pd
import plotly.express as px
from dash.exceptions import PreventUpdate
from dash_charts.components import dropdown_group, opts_dd
from dash_charts.utils_app import AppBase
from dash_charts.utils_app_with_navigation import AppWithTabs
from dash_charts.utils_callbacks import map_args, map_outputs
from dash_charts.utils_fig import min_graph
from icecream import ic

#   Require user to submit "Tidy" data with non-value headers
#   > Update static tab with example data_table of tidy data and links to more explanation
#     dash_table.DataTable(
#         data=df_example_tidy.to_dict('records'),
#         columns=[{'name': i, 'id': i} for i in df_example_tidy.columns]
#     ),

# Elements to build:
# - html.Hr() (useful for separating the upload/review data/px chart)
# - dcc.Upload()
# - How to make user promopts?
# - dcc.Input to select SQL table and table to show raw data (use dash_charts table class)

# (X) Add lower section that appears on all tabs. Has file selection or drop {Could use a little more cleanup}
#     > if SQLite (maps tables - maybe second pop-up?) / JSON / CSV - shows error if not panda-ble
#     > https://dash.plotly.com/dash-core-components/upload
#     > https://docs.faculty.ai/user-guide/apps/examples/dash_file_upload_download.html
#     > https://github.com/plotly/dash-recipes/blob/master/dash-upload-simple.py
# ( ) [1/2-storage] Create single SQLite DB file to hold upload dataframes
# ( ) [1/2-class] AppSettings/AppSession class to store Dict with data sources - {“source_name”: {“type”: “sql”/“JSON”/etc, “value”: dataframe or path}}
#     > For each upload file, create table with filename and dump user uploaded data (use datasete for SQL management and to check if tables exists already - may need pandas to load CSV/JSON data first before dumping into SQL with datasete)
#     > Allow user to clear data (either specific tables or all database)
#     > Maybe have warning that data automatically deletes after 30 days of inactivity?
#     > If uploading a file with the same name - offer to clear already uploaded data or if a new name should be entered (prompt user for input suggesting "-1"/"-2"/etc)
#     > Create main table that stores meta information on each table - date added, source filename (with full path?), (last accessed?), etc.

# ( ) !!Ability to remove datasets?
# ( ) [2/2-storage] Create user-specific SQLite DB file f'{username}.db'. Have user enter username, which could be stored in URL or in dcc.Store(). This defines which SQLite database is loaded
#  > !!Move App Settings to the SQLite database!!

# ( ) show error if failed to parse data source
# ( ) show table of raw data (handle really wide tables - clip columns?)
# ( ) Allow for charting the data - need to get column names, update dataframe in tab, etc.

# ( ) Create Dash_Charts table to filter by streaming platform, category, and rating
# ( ) Create custom views. Could be good to see distribution of scores for an anime and where my score falls

# Other notes
# > PLANNED: Make the tabs and chart compact as well when the compact argument is set to True
# > PLANNED: select chart types from type and generate multiple charts on same page?
#   > Need way to store state of charts when switching tabs...
# > methods for conerting to and from `dcc.Store`: df_to_store() // store_to_df()
#
# > ex_px variation - notes:
#   > Along bottom of screen - file select - give keyword name to select from dropdowns for each px app/tab
#     > This way multiple data sets can be loaded in PD DataFrames
#   > In dropdown option of default or loaded data
#   > Data should be tidy, then regular dropdown can be used
#   > Should show table with data below input
# > Pdoc3 search? {May not work for local docs, but checkout how pdoc does it's pdoc: https://github.com/pdoc3/pdoc/blob/master/doc/pdoc_template/}

# ======================================================================================================================
# Create Tab with User Instructions


class StaticTab(AppBase):
    """Simple App without charts or callbacks."""

    basic_style = {
        'marginLeft': 'auto',
        'marginRight': 'auto',
        'maxWidth': '1000px',
        'paddingTop': '10px',
    }

    def initialization(self):
        """Initialize ids with `self.register_uniq_ids([...])` and other one-time actions."""
        super().initialization()
        self.register_uniq_ids(['N/A'])

    def create_elements(self):
        """Initialize the charts, tables, and other Dash elements.."""
        pass

    def create_callbacks(self):
        """Register callbacks necessary for this tab."""
        pass


class InstructionsTab(StaticTab):
    """Instructions Tab."""

    name = 'Information'

    summary = """
# Data Exploration App Instructions

This application is meant for generally exploring static datasets, such as SQLite (.db) files, JSON, or CSV. The data
must be in the `tidy` format. See [this guide on tidy data](https://plotly.com/python/px-arguments/).

## Loading Data

Enter a name for the dataset then drag and drop the file into the upload input. If the parsing of the file fails, you
should see an error right away. If not, the new data can be selected in any tab and can be shown in a datatable below

### PLANNED: Add more explanation here
"""

    def return_layout(self):
        """Return Dash application layout.

        Returns:
            dict: Dash HTML object

        """
        return html.Div(children=dcc.Markdown(self.summary), style=self.basic_style)


# ======================================================================================================================
# Create classes to manage tabs state. Easy to scale up or down
# >> Demo uses sample data. User could replace with data loaded from a static CSV file, TinyDB, SQLite, etc.


class TabBase(AppBase):  # noqa: H601
    """Base tab class with helper methods."""

    external_stylesheets = [dbc.themes.FLATLY]

    # ID Elements for UI
    id_chart: str = 'chart'
    id_func: str = 'func'
    id_template: str = 'template'  # PLANNED: template should be able to be None

    takes_args: bool = True
    """If True, will pass arguments from UI to function."""

    templates: list = ['ggplot2', 'seaborn', 'simple_white', 'plotly',
                       'plotly_white', 'plotly_dark', 'presentation', 'xgridoff',
                       'ygridoff', 'gridon', 'none']
    """List of templates from: `import plotly.io as pio; pio.templates`"""

    # Must override in child class
    name: str = None
    """Unique tab component name. Must be overridden in child class."""
    data: pd.DataFrame = None
    """Dataframe. Must be overridden in child class."""
    func_map: OrderedDict = None
    """Map of functions to keywords. Must be overridden in child class."""

    # PLANNED: below items should be able to be None
    dims: tuple = ()
    """Keyword from function for dropdowns with column names as options. Must be overridden in child class."""
    dims_dict: OrderedDict = OrderedDict([])
    """OrderedDict of keyword from function to allowed values. Must be overridden in child class."""

    def initialization(self):
        """Initialize ids with `self.register_uniq_ids([...])` and other one-time actions."""
        super().initialization()

        # Register the the unique element IDs
        self.input_ids = [self.id_func, self.id_template] + [*self.dims] + [*self.dims_dict.keys()]
        self.register_uniq_ids([self.id_chart] + self.input_ids)

        # Configure the options for the various dropdowns
        self.col_opts = [] if self.data is None else tuple(opts_dd(_c, _c) for _c in self.data.columns)
        self.func_opts = tuple(opts_dd(lbl, lbl) for lbl in self.func_map.keys())
        self.t_opts = tuple(opts_dd(template, template) for template in self.templates)

    def create_elements(self):
        """Initialize the charts, tables, and other Dash elements."""
        pass

    def verify_types_for_layout(self):
        """Verify data types of data members necessary for the layout of this tab.

        Raises:
            RuntimeError: if any relevant data members are of the wrong type

        """
        errors = []
        if not isinstance(self.name, str):
            errors.append(f'Expected self.name="{self.name}" to be str')
        if not isinstance(self.dims, tuple):
            errors.append(f'Expected self.dims="{self.dims}" to be tuple')
        if not isinstance(self.dims_dict, OrderedDict):
            errors.append(f'Expected self.dims_dict="{self.dims_dict}" to be OrderedDict')
        if len(errors):
            formatted_errors = '\n' + '\n'.join(errors)
            raise RuntimeError(f'Found errors in data members:{formatted_errors}')

    def verify_types_for_callbacks(self):
        """Verify data types of data members necessary for the callbacks of this tab.

        Raises:
            RuntimeError: if any relevant data members are of the wrong type

        """
        errors = []
        if not isinstance(self.takes_args, bool):
            errors.append(f'Expected self.takes_args="{self.takes_args}" to be bool')
        if not (isinstance(self.data, pd.DataFrame) or self.data is None):
            errors.append(f'Expected self.data="{self.data}" to be pd.DataFrame or None')
        if not isinstance(self.func_map, OrderedDict):
            errors.append(f'Expected self.func_map="{self.func_map}" to be OrderedDict')
        if len(errors):
            formatted_errors = '\n' + '\n'.join(errors)
            raise RuntimeError(f'Found errors in data members:{formatted_errors}')

    def return_layout(self):
        """Return Dash application layout.

        Returns:
            dict: Dash HTML object

        """
        self.verify_types_for_layout()

        return html.Div([
            html.Div([
                dropdown_group('Plot Type:', self.ids[self.id_func], self.func_opts, value=self.func_opts[0]['label']),
                dropdown_group('Template:', self.ids[self.id_template], self.t_opts, value=self.t_opts[0]['label']),
            ] + [
                dropdown_group(f'{dim}:', self.ids[dim], self.col_opts)
                for dim in self.dims
            ] + [
                dropdown_group(f'{dim}:', self.ids[dim], [opts_dd(item, item) for item in items])
                for dim, items in self.dims_dict.items()
            ], style={'width': '25%', 'float': 'left'}),
            min_graph(id=self.ids[self.id_chart], style={'width': '75%', 'display': 'inline-block'}),
        ], style={'padding': '15px'})

    def create_callbacks(self):
        """Register callbacks necessary for this tab."""
        self.verify_types_for_callbacks()

        self.register_update_chart()

    def register_update_chart(self):
        """Register the update_chart callback."""
        outputs = [(self.id_chart, 'figure')]
        inputs = [(_id, 'value') for _id in self.input_ids]
        states = ()
        @self.callback(outputs, inputs, states)
        def update_chart(*raw_args):
            a_in, _a_states = map_args(raw_args, inputs, states)
            name_func = a_in[self.id_func]['value']

            properties = [trigger['prop_id'] for trigger in dash.callback_context.triggered]
            new_chart = {}
            # If event is not a tab change, return the updated chart
            if 'tabs-select.value' not in properties:  # FIXME: replace tabs-select with actual keyname (?)
                if self.takes_args:
                    # Parse the arguments to generate a new plot
                    kwargs = {key: a_in[key]['value'] for key in self.input_ids[1:]}
                    new_chart = self.func_map[name_func](self.data, height=650, **kwargs)
                else:
                    new_chart = self.func_map[name_func]()
            # Example Mapping Output. Alternatively, just: `return [new_chart]`
            return map_outputs(outputs, [(self.id_chart, 'figure', new_chart)])


class TabTip(TabBase):  # noqa: H601
    """TabTip properties."""

    name = 'Tip Data'
    data = px.data.tips()
    func_map = OrderedDict([
        ('scatter', px.scatter),
        ('density_contour', px.density_contour),
    ])
    dims = ('x', 'y', 'color', 'facet_row', 'facet_col')
    dims_dict = OrderedDict([
        ('marginal_x', ('histogram', 'rag', 'violin', 'box')),
        ('marginal_y', ('histogram', 'rag', 'violin', 'box')),
        ('trendline', ('ols', 'lowess')),
    ])


class TabIris(TabBase):  # noqa: H601
    """TabIris properties."""

    name = 'Iris Data'
    data = px.data.iris()
    func_map = OrderedDict([
        ('histogram', px.histogram),
        ('density_contour', px.density_contour),
        ('strip', px.strip),
        ('box', px.box),
        ('violin', px.violin),
        ('scatter', px.scatter),
    ])
    dims = ('x', 'y', 'color', 'facet_col', 'facet_row')


# ======================================================================================================================
# Create class for application to control manage variable scopes


def parse_upload(b64_file, filename, timestamp):
    """Identify file type and parse the uploaded content into a dataframe.


    """
    _content_type, content_string = b64_file.split(',')
    decoded = base64.b64decode(content_string)
    try:
        suffix = Path(filename).suffix.lower()
        if suffix == '.csv':
            df_upload = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif suffix.startswith('.xl'):
            df_upload = pd.read_excel(io.BytesIO(decoded))
        elif suffix == '.json':
            pass  # PLANNED: Expected in records format?
        elif suffix == '.other?':
            pass  # PLANNED: Any other supported formats?
    except Exception as error:
        ic(error)
        return html.Div([f'There was an error processing this file: {error}'])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.fromtimestamp(date)),

        # dash_table.DataTable(
        #     data=df_upload.to_dict('records'),
        #     columns=[{'name': i, 'id': i} for i in df_upload.columns]
        # ),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all',
        })
    ])


# ======================================================================================================================
# Create class for application to control manage variable scopes


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
    """Unique name for the main chart."""

    id_upload_output = 'upload-output'
    """Unique name for the main chart."""

    def initialization(self):
        """Initialize ids with `self.register_uniq_ids([...])` and other one-time actions."""
        super().initialization()
        self.register_uniq_ids([self.id_upload, self.id_upload_output])

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
                ),
                html.Div(id=self.ids[self.id_upload_output]),
            ])]),
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
            return [parse_upload(b64_file, filename, timestamp)]
