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

def check_length(answer, min_):
    '''
    Checks the length of timestamps is less than min_
    
    answer: list
        List of dictionaries (json format)
    '''
    lengths = []
    for ans in answer:
        time_diff = ans['endTime'] - ans['startTime']
        num_sec = min_*60 
        result = time_diff <= num_sec
        lengths.append(result)
    return all(lengths)

def test_brain(med_file):
    clip_length = 2 # this is also param for check_length
    calc_result = brain.run(data=med_file,
                            clip_length=clip_length,
                            common_timestamps=2, 
                            algos_to_compare = ["algo1","algo2","algo3_0","algo3_5"],
                            limit=None)
    
    answer = [{'startTime': 765.512, 'endTime': 882.645},
              {'startTime': 1018.379, 'endTime': 1131.467},
              {'startTime': 0.0, 'endTime': 119.562},
              {'startTime': 891.677, 'endTime': 1008.99},
              {'startTime': 259.889, 'endTime': 375.413},
              {'startTime': 383.298, 'endTime': 495.599},
              {'startTime': 127.098, 'endTime': 234.249},
              {'startTime': 507.003, 'endTime': 626.884},
              {'startTime': 1138.629, 'endTime': 1256.19},
              {'startTime': 630.41, 'endTime': 741.233},
              {'startTime': 17734.164, 'endTime': 17853.51},
              {'startTime': 12177.737, 'endTime': 12293.058}]
    
    time_check = check_length(calc_result, min_=clip_length)
    assert calc_result == answer # check answer is correct
    assert time_check # check the length of clips is <= clip_length