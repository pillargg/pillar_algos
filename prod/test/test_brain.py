'''
Tests to make sure brain gets the right results.

[Navigation source](https://towardsdatascience.com/pytest-for-data-scientists-2990319e55e6)
'''
import os.path  # get dir path
import sys  # append dir path to sys.path
import json  # load sample data
import pytest  # test
import pandas.api.types as ptypes  # to check dataframe dtypes assertions
import pandas as pd
import numpy as np


#### Grab Directory Locations ####
cd = os.path.pardir  # go back one dir
current_dir = os.path.dirname(__file__)  # get dir of current filename
prod_dir = os.path.join(current_dir, cd)  # join it with cd to go to parent

algos_path = os.path.abspath(prod_dir)  # get the absolute path

base_dir = os.path.join(prod_dir, cd, cd)
data_folder = "sample_data"  # location of sample data

#### Append Algos Dir to Sys.path ####
sys.path.append(algos_path)  # append the path to sys.path

#### Testing Area ####
from pillaralgos import brain # from pillaralgos folder

###############################################################################
import pytest

@pytest.fixture()
def med_file():
    data = json.load(open(f"{data_folder}/sample_med.json"))
    return data


def test_brain(med_file):
    clip_length = 0.75 # this is also param for check_length
    calc_result = brain.run(data=med_file,
                            clip_length=clip_length,
                            common_timestamps=2, 
                            algos_to_compare = ["algo1","algo2","algo3_0","algo3_5"],
                            limit=7)
    
    answer = [{'startTime': 21200.477, 'endTime': 21245.343},
              {'startTime': 12175.522, 'endTime': 12220.34},
              {'startTime': 19831.123, 'endTime': 19875.995},
              {'startTime': 15355.018, 'endTime': 15387.38},
              {'startTime': 17841.413, 'endTime': 17886.181},
              {'startTime': 5912.06, 'endTime': 5955.978},
              {'startTime': 5583.986, 'endTime': 5628.403}]
    assert calc_result == answer # check answer is correct


def test_length(med_file):
    '''
    Checks the length of timestamps is less than min_
    
    answer: list
        List of dictionaries (json format)
    '''
    clip_length = 0.75 # this is also param for check_length
    answer = brain.run(data=med_file,
                            clip_length=clip_length,
                            common_timestamps=2, 
                            algos_to_compare = ["algo1","algo2","algo3_0","algo3_5"],
                            limit=7)
    
    lengths = []
    for ans in answer:
        time_diff = ans['endTime'] - ans['startTime']
        num_sec = clip_length*60 
        result = time_diff <= num_sec # to get bools
        lengths.append(result)
    assert sum(lengths) == 7 # passes if all time lengths <= clip_length