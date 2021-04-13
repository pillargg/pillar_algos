'''
Runs tests on the `data_handler` script, but first navigates to correct dirs
# [Source](https://towardsdatascience.com/pytest-for-data-scientists-2990319e55e6)
'''
import os.path  # get dir path
import sys  # append dir path to sys.path
import json  # load sample data
import pytest  # test
import numpy as np
import pandas as pd

#### Grab Directory Locations ####
cd = os.path.pardir # go back one dir
current_dir = os.path.dirname(__file__) # get dir of current filename
prod_dir = os.path.join(current_dir, cd) # join it with cd to go to parent
pill_dir = os.path.join(prod_dir, 'pillaralgos') # join parent with pillaralgos folder
algos_path = os.path.abspath(pill_dir)  # get the absolute path

base_dir = os.path.join(prod_dir, cd, cd)
data_folder = f'{base_dir}/data' # location of sample data

#### Append Algos Dir to Sys.path ####
sys.path.append(algos_path)  # append the path to sys.path

#### Testing Area ####
from helpers import data_handler as dh # from pillaralgos folder

@pytest.fixture()
def empty_file():
    data = json.load(open(f'{data_folder}/sample_nan.json'))
    return data

@pytest.fixture()
def med_file():
    data = json.load(open(f'{data_folder}/sample_med.json'))
    return data

def test_organize_twitch_chat_empty(empty_file):
    'Checks the organizer gets right output'
    data = dh.organize_twitch_chat(empty_file)
    assert data.size == 0

    
def test_organize_twitch_chat_lg(med_file):
    'Checks the organizer gets right output'
    data = dh.organize_twitch_chat(med_file)
    assert type(data) == pd.DataFrame


def test_organize_twitch_chat_cols(med_file):
    'Checks basic cols are in the returned df'
    data = dh.organize_twitch_chat(med_file)
    needed_cols = ['created_at','updated_at','body','emoticons','is_action','type']
    assert all(col in data.columns for col in needed_cols)
    

import pandas.api.types as ptypes

def test_organize_twitch_chat_dtypes(med_file):
    'Checks the basic cols are right dtype'
    data = dh.organize_twitch_chat(med_file)
    time_cols = ['created_at','updated_at']
    obj_cols = ['body', 'emoticons']
    
    assert all(ptypes.is_datetime64_any_dtype(data[col]) for col in time_cols)
    assert ptypes.is_bool_dtype(data['is_action'])
    assert ptypes.is_integer_dtype(data['_id'])
    assert all(ptypes.is_object_dtype(data[col]) for col in obj_cols)
    