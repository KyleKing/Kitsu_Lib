"""Create helpers for managing file upload and download."""
# PLANNED: Should be moved to dash_charts

import base64
import io
from datetime import datetime
from pathlib import Path
from urllib.parse import quote as urlquote

import dash_html_components as html
import pandas as pd
from icecream import ic

# Useful methods based on: https://docs.faculty.ai/user-guide/apps/examples/dash_file_upload_download.html


def save_file(dest_path, content):
    """Decode and store a file uploaded with Plotly Dash."""
    data = content.encode("utf8").split(b';base64,')[1]
    dest_path.write_text(base64.decodebytes(data))


def uploaded_files(upload_dir):
    """List the files in the upload directory."""
    return [*upload_dir.glob('*.*')]


def file_download_link(filename):
    """Create a Plotly Dash 'A' element that downloads a file from the app."""
    return html.A(filename, href=f'/download/{urlquote(filename)}')


# End methods from faculty.ai


def parse_uploaded_image(b64_file, filename, timestamp):

    content_type, data = b64_file.split(b';base64,')[1]

    if 'image' in content_type:
        return html.Img(src=b64_file)


def parse_uploaded_df(b64_file, filename, timestamp):
    """Identify file type and parse the uploaded content into a dataframe.


    """
    content_type, data = b64_file.split(b';base64,')
    decoded = base64.b64decode(data)
    try:
        suffix = Path(filename).suffix.lower()
        if suffix == '.csv':
            df_upload = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif suffix.startswith('.xl'):
            # FYI: xlsx will have 'spreadsheet' in `content_type` but xls will not have anything
            df_upload = pd.read_excel(io.BytesIO(decoded))
        elif suffix == '.json':
            pass  # PLANNED: Expected in records format?
        elif suffix == '.other?':
            pass  # PLANNED: Any other supported formats?
    except Exception as error:
        ic(error)
        return html.Div([f'Could not parse {filename} ({content_type}). Error: {error}'])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.fromtimestamp(content_type)),

        # dash_table.DataTable(
        #     data=df_upload.to_dict('records'),
        #     columns=[{'name': i, 'id': i} for i in df_upload.columns]
        # ),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(b64_file[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all',
        })
    ])
