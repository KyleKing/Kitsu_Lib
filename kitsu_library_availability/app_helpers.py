"""Create helpers for managing file upload and download.

Some functions based on code from:
https://docs.faculty.ai/user-guide/apps/examples/dash_file_upload_download.html

"""
# PLANNED: Whole file should be moved to dash_charts

import base64
import io
import json
from pathlib import Path
from urllib.parse import quote as urlquote

import dash_html_components as html
import pandas as pd
from icecream import ic


def split_b64_file(b64_file):
    """Separate the data type and data content from a b64-encoded string.

    Args:
        b64_file: file encoded in base64

    Returns:
        tuple: of strings `(content_type, data)`

    """
    return b64_file.encode('utf8').split(b';base64,')


def save_file(dest_path, b64_file):
    """Decode and store a file uploaded with Plotly Dash.

    Args:
        dest_path: Path on server filesystem to save the file
        b64_file: file encoded in base64

    """
    data = split_b64_file(b64_file)[1]
    dest_path.write_text(base64.decodebytes(data))


def uploaded_files(upload_dir):
    """List the files in the upload directory.

    Args:
        upload_dir: directory where files are uploadedfolder

    Returns:
        list: Paths of uploaded files

    """
    return [*upload_dir.glob('*.*')]


def file_download_link(filename):
    """Create a Plotly Dash 'A' element that when clicked triggers a file downloaded.

    Args:
        filename: Path to local file to be available for user download

    Returns:
        html.A: clickable Dash link to trigger download

    """
    # PLANNED: Revisit. Should filename be a name or the full path?
    return html.A(filename, href=f'/download/{urlquote(filename)}')


def parse_uploaded_image(b64_file, filename, timestamp):
    """Create an HTML element to show an uploaded image.

    Args:
        b64_file: file encoded in base64
        filename: filename of upload file. Name only
        timestamp: upload timestamp

    Returns:
        html.Img: if image data type

    Raises:
        RuntimeError: if filetype is not a supported image type

    """
    content_type, data = split_b64_file(b64_file)
    if 'image' not in content_type:
        raise RuntimeError(f'Not image type. Found: {content_type}')
    return html.Img(src=b64_file)


def parse_uploaded_df(b64_file, filename, timestamp):
    """Identify file type and parse the uploaded content into a dataframe.

    Args:
        b64_file: file encoded in base64
        filename: filename of upload file. Name only
        timestamp: upload timestamp

    Returns:
        dataframe: uploaded dataframe parsed from source file

    Raises:
        RuntimeError: if datatype could not be parsed

    """
    content_type, data = split_b64_file(b64_file)
    decoded = base64.b64decode(data)
    try:
        suffix = Path(filename).suffix.lower()
        ic(content_type, suffix)
        if suffix == '.csv':
            df_upload = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

        elif suffix.startswith('.xl'):
            # xlsx will have 'spreadsheet' in `content_type` but xls will not have anything
            df_upload = pd.read_excel(io.BytesIO(decoded))

        elif suffix == '.json':
            raw_json = json.loads(io.StringIO(decoded.decode('utf-8')))
            keys = [*raw_json.keys()]
            if len(keys) != 1:
                raise RuntimeError('Expected JSON with format `{data: [...]}` where `data` could be any key.'
                                   f'However, more than one key was found: {keys}')
            df_upload = pd.read_json(raw_json[keys[0]])

    except Exception as error:
        raise RuntimeError(f'Could not parse {filename} ({content_type}). Error: {error}')

    return df_upload  # noqa: R504
