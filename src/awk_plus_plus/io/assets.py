import glob
import json
import mimetypes
import os
import re
from pathlib import Path
import warnings

warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

import magic
import pandas as pd


def raw(*subpath):
    return Path(os.path.join(os.environ['RAW_DATA_DIR'], *subpath))


def processed(*subpath):
    return Path(os.path.join(os.environ['PROCESSED_DATA_DIR'], *subpath))


def external(*subpath):
    return Path(os.path.join(os.environ['EXTERNAL_DATA_DIR'], *subpath))


def data(*subpath):
    return Path(os.path.join(os.environ['DATA_DIR'], *subpath))


def model(*subpath):
    return Path(os.path.join(os.environ['MODELS_DIR'], *subpath))


def guess_type(path):
    mime = magic.Magic(mime=True)
    file_type = mime.from_file(path)
    if re.match('text', file_type):
        return mimetypes.guess_type(path)[0]
    return file_type


def read_from(path):
    file_type = guess_type(path)
    path_str = str(path)
    try:
        if 'text/csv' in file_type or 'application/csv' in file_type:
            return pd.read_csv(path_str, dtype_backend='pyarrow')
        elif 'application/json' in file_type:
            return pd.read_json(path_str, dtype_backend='pyarrow')
        elif 'application/vnd.ms-excel' in file_type or 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in file_type:
            return pd.read_excel(path_str, dtype_backend='pyarrow', dtype='str')
        elif 'application/octet-stream' in file_type:
            if path_str.endswith('.parquet'):
                return pd.read_parquet(path_str, engine='pyarrow')
            elif path_str.endswith('.feather'):
                return pd.read_feather(path_str)
        elif 'text/html' in file_type:
            return pd.read_html(path_str)
        elif 'application/x-hdf' in file_type or 'application/x-hdf5' in file_type:
            return pd.read_hdf(path_str)
        elif 'application/python-pickle' in file_type or path_str.endswith('.pkl'):
            return pd.read_pickle(path_str)
        elif 'inode/x-empty' in file_type:
            return pd.DataFrame()
        else:
            return pd.DataFrame()
    except Exception as e:
        print(e)
        return pd.DataFrame()


def read_glob(path):
    df_list = []
    for file in glob.glob(path):
        df = read_from(file)
        df['source_file'] = file.name
        df_list.append(df)
    return pd.concat(df_list, ignore_index=True)


def load_file_into_json(path):
    with open(path) as f:
        return json.load(f)


def patch():
    pd.read_from = read_from
    pd.read_glob = read_glob
    json.load_file = load_file_into_json


patch()

APP_PATH = str(Path(__file__).parent.resolve())
ROOT_PATH = os.environ.get('ROOT_PATH', APP_PATH)
