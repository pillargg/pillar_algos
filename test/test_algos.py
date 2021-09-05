'''
Runs sample_med.json through all algorithms to make sure they are working properly.

Does not test all possible variables (yet)

[Navigation source](https://towardsdatascience.com/pytest-for-data-scientists-2990319e55e6)
'''
import os.path  # get dir path
import sys  # append dir path to sys.path
import json  # load sample data
import pytest  # test
import pytest_check as check # for multiple assertions
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
clip_length = 0.5

#### Append Algos Dir to Sys.path ####
sys.path.append(algos_path)  # append the path to sys.path

#### Testing Area ####
from pillaralgos import algo1, algo2, algo3_0, algo3_5, algo3_6, algo4 # from pillaralgos folder
###############################################################################


@pytest.fixture()
def med_file(clip_length=0.5):
    "load raw med sized file"
    from pillaralgos.brain import load_data
    
    data = json.load(open(f"{data_folder}/sample_med.json"))

    all_data = load_data(data, clip_length)
    return all_data


def check_length(answer, clip_length):
    '''
    Checks the length of timestamps is less than clip_length
    
    answer: dataframe
        dataframe from algos
    clip_length: int
        Length of timestamp
    '''
    time_diff = (answer['end'] - answer['start']).apply(lambda x: x.total_seconds())
    num_sec = clip_length*60 
    result = time_diff <= num_sec
    return all(result)

def test_algo1(med_file):
    'check algo1 results'
    a = algo1.featureFinder(med_file)
    calc_result = a.run().sample(n=10, random_state=69)
    
    answer = pd.read_pickle(f'{data_folder}/med_algo1_answer.pkl')
    time_check = check_length(calc_result, clip_length=clip_length)
    check.is_true(time_check) # check the length of clips is <= clip_length
    check.is_true(len(answer) == len(calc_result))
    
    check.is_true(calc_result.equals(answer))

def test_algo2(med_file):
    'check algo2 results'
    a = algo2.featureFinder(med_file)
    calc_result = a.run().sample(n=10, random_state=69)
    
    answer = pd.read_pickle(f'{data_folder}/med_algo2_answer.pkl')
    time_check = check_length(calc_result, clip_length=clip_length)
    check.is_true(time_check) # check the length of clips is <= clip_length
    check.is_true(calc_result.equals(answer))
    

def test_algo3(med_file):
    'check algo3 results'
    a = algo3_0.featureFinder(med_file)
    calc_result = a.run().sample(n=10, random_state=69)
    
    answer = pd.read_pickle(f'{data_folder}/med_algo3_0_answer.pkl')
    time_check = check_length(calc_result, clip_length=clip_length)
    check.is_true(time_check) # check the length of clips is <= clip_length
    check.is_true(calc_result.equals(answer))

def test_algo3_5(med_file):
    'check algo3_5 results'
    a = algo3_5.featureFinder(med_file)
    calc_result = a.run().sample(n=10, random_state=69)
    
    answer = pd.read_pickle(f'{data_folder}/med_algo3_5_answer.pkl')
    time_check = check_length(calc_result, clip_length=clip_length)
    check.is_true(time_check) # check the length of clips is <= clip_length
    check.is_true(calc_result.equals(answer))
    
def test_algo3_6(med_file):
    'check algo3_6 results'
    a = algo3_6.featureFinder(med_file)
    calc_result = a.run().sample(n=10, random_state=69)
    
    answer = pd.read_pickle(f'{data_folder}/med_algo3_6_answer.pkl')
    time_check = check_length(calc_result, clip_length=clip_length)
    check.is_true(time_check) # check the length of clips is <= clip_length
    check.is_true(calc_result.equals(answer))
    
def test_algo4(med_file):
    'check algo4 results'
    a = algo4.featureFinder(med_file)
    calc_result = a.run().sample(n=10, random_state=69)
    
    answer = pd.read_pickle(f'{data_folder}/med_algo4_answer.pkl')
    time_check = check_length(calc_result, clip_length=clip_length)
    check.is_true(time_check) # check the length of clips is <= clip_length
    check.is_true(calc_result.equals(answer))
