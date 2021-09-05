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
clip_length = 0.75 # this is also param for check_length

#### Append Algos Dir to Sys.path ####
sys.path.append(algos_path)  # append the path to sys.path

#### Testing Area ####
from pillaralgos import brain # from pillaralgos folder

###############################################################################
import pytest

@pytest.fixture(scope='module')
def med_file_calc():
    'run brain once, then use results to test'
    calc_result = brain.run(chat_loc=f"{data_folder}/sample_med.json",
                            clip_length=clip_length,
                            dev_mode = False)
    return calc_result.sample(n=10, random_state=69)

def test_brain(med_file_calc):
    clip_length = 0.75 # this is also param for check_length
    answer = pd.read_pickle(f"{data_folder}/med_brain_answer.pkl")
    
    assert med_file_calc.equals(answer) # check answer is correct


def test_length(med_file_calc):
    '''
    Checks the length of timestamps is less than min_
    
    answer: list
        List of dictionaries (json format)
    '''    
    time_diff = med_file_calc['end'] - med_file_calc['start']
    time_diff = time_diff.apply(lambda x: x.total_seconds())
    num_sec = clip_length*60 
    result = time_diff <= num_sec # to get bools

    assert sum(result) == 10 # passes if all time lengths <= clip_length