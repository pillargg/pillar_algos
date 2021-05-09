'''
Runs sample_med.json through all algorithms to make sure they are working properly.

Does not test all possible variables (yet)

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
from pillaralgos import algo1, algo2, algo3_0, algo3_5 # from pillaralgos folder

###############################################################################


@pytest.fixture()
def med_file():
    "load raw med sized file"
    data = json.load(open(f"{data_folder}/sample_med.json"))
    return data


def check_length(answer, min_):
    '''
    Checks the length of timestamps is less than min_
    
    answer: list
        List of dictionaries (json format)
    min_: int
        Length of timestamp
    '''
    lengths = []
    for ans in answer:
        time_diff = ans['endTime'] - ans['startTime']
        num_sec = min_*60 
        result = time_diff <= num_sec
        lengths.append(result)
    return all(lengths)

def test_algo1(med_file):
    min_=0.5
    limit = 10
    calc_result = algo1.run(
        data = med_file,
        min_ = min_,
        limit = limit,
        sort_by = 'rel',
        save_json = False
    )
    answer = [{'startTime': 26008.706, 'endTime': 26037.915},
              {'startTime': 25683.19, 'endTime': 25712.694},
              {'startTime': 25978.645, 'endTime': 26005.689},
              {'startTime': 25906.807, 'endTime': 25934.694},
              {'startTime': 21204.676, 'endTime': 21233.315},
              {'startTime': 12215.271, 'endTime': 12244.861},
              {'startTime': 25747.017, 'endTime': 25774.105},
              {'startTime': 25474.293, 'endTime': 25503.543},
              {'startTime': 25874.858, 'endTime': 25904.018},
              {'startTime': 19827.532, 'endTime': 19857.415}]
    
    time_check = check_length(calc_result, min_=min_)
    assert time_check # check the length of clips is <= clip_length
    assert calc_result == answer

def test_algo2(med_file):
    min_=0.5
    limit=5
    calc_result = algo2.run(
        data=med_file,
        min_=min_,
        limit=limit,
        save_json=False
    )

    answer = [{'startTime': 14840.294, 'endTime': 14840.294},
              {'startTime': 696.512, 'endTime': 696.512},
              {'startTime': 6441.765, 'endTime': 6441.765},
              {'startTime': 8194.165, 'endTime': 8194.165},
              {'startTime': 8381.339, 'endTime': 8381.339}]
    time_check = check_length(calc_result, min_=min_)
    assert time_check # check the length of clips is <= clip_length
    assert calc_result == answer
    

def test_algo3_0(med_file):
    min_=0.5
    limit=6
    
    calc_result = algo3_0.run(
        data=med_file,
        min_=min_,
        limit=limit,
        min_words=10,
        save_json=False
    )
    answer = [{'startTime': 19827.532, 'endTime': 19857.415},
              {'startTime': 12184.113, 'endTime': 12212.453},
              {'startTime': 17847.854, 'endTime': 17877.303},
              {'startTime': 5611.102, 'endTime': 5632.707},
              {'startTime': 5919.616, 'endTime': 5949.445},
              {'startTime': 6656.985, 'endTime': 6680.851}]
    time_check = check_length(calc_result, min_=min_)
    assert time_check # check the length of clips is <= clip_length
    assert calc_result == answer

def test_algo3_5(med_file):
    min_=0.5
    limit=3
    calc_result = algo3_5.run(
        data=med_file,
        min_=min_,
        limit=limit,
        goal='num_emo',
        save_json=False
    )
    answer = [{'startTime': 21204.676, 'endTime': 21233.315},
              {'startTime': 12215.271, 'endTime': 12244.861},
              {'startTime': 19757.217, 'endTime': 19785.986}]
    time_check = check_length(calc_result, min_=min_)
    assert time_check # check the length of clips is <= clip_length
    assert calc_result == answer
    
def test_algo1_diffs(med_file):
    '''
    Test different values for min_ result in different answers.
    Does NOT check for correctness of those answers
    '''
    all_results = []
    for time in [0.5, 3, 1, 2]:
        result = algo1.run(
            data = med_file,
            min_ = time,
            limit = 10,
            sort_by = 'rel',
            save_json = False)
        all_results.append(result)
        
    assert all_results[0] != all_results[1] != all_results[2] != all_results[3]
    
def test_algo2_diffs(med_file):
    all_results = []
    for time in [0.5, 3, 1, 2]:
        result = algo2.run(
            data=med_file,
            min_=time,
            limit=10,
            save_json=False)
        all_results.append(result)
        
    assert all_results[0] != all_results[1] != all_results[2] != all_results[3]
    
def test_algo30_diffs(med_file):
    all_results = []
    for time in [0.5, 3, 1, 2]:
        result = algo3_0.run(
            med_file, 
            min_=time, 
            limit=10, 
            min_words=10, 
            save_json=False)
        all_results.append(result)
        
    assert all_results[0] != all_results[1] != all_results[2] != all_results[3]
    
def test_algo35_diffs(med_file):
    all_results = []
    for time in [0.5, 3, 1, 2]:
        result = algo3_5.run(
            data=med_file,
            min_=time,
            limit=10,
            goal='num_emo',
            save_json=False)
        
        all_results.append(result)
        
    assert all_results[0] != all_results[1] != all_results[2] != all_results[3]