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


def test_algo1(med_file):
    calc_result = algo1.run(
        data = med_file,
        min_ = 0.5,
        limit = 10,
        sort_by = 'rel',
        save_json = False
    )
    answer = [{'startTime': 105.78, 'endTime': 135.449},
              {'startTime': 183.68, 'endTime': 200.871},
              {'startTime': 266.303, 'endTime': 284.56},
              {'startTime': 375.218, 'endTime': 399.649},
              {'startTime': 74.219, 'endTime': 102.902},
              {'startTime': 0.0, 'endTime': 10.329},
              {'startTime': 308.506, 'endTime': 334.573},
              {'startTime': 338.925, 'endTime': 349.935},
              {'startTime': 135.939, 'endTime': 163.39},
              {'startTime': 234.249, 'endTime': 259.889}]
    assert calc_result == answer
    
def test_algo2(med_file):
    calc_result = algo2.run(
        data=med_file,
        min_=0.5,
        limit=10,
        save_json=False
    )
    
    answer = [{'startTime': 14840.294, 'endTime': 14840.294},
              {'startTime': 696.512, 'endTime': 696.512},
              {'startTime': 6441.765, 'endTime': 6441.765},
              {'startTime': 8194.165, 'endTime': 8194.165},
              {'startTime': 8381.339, 'endTime': 8381.339},
              {'startTime': 14140.362, 'endTime': 14140.362},
              {'startTime': 22983.785, 'endTime': 22983.785},
              {'startTime': 14428.961, 'endTime': 14428.961},
              {'startTime': 15187.424, 'endTime': 15187.424},
              {'startTime': 7199.836, 'endTime': 7201.808}]
    
    assert calc_result == answer
    
def test_algo3_0(med_file):
    calc_result = algo3_0.run(
        data=med_file,
        min_=0.5,
        limit=10,
        min_words=10,
        save_json=False
    )
    answer = [{'startTime': 12177.737, 'endTime': 12293.058},
              {'startTime': 5856.98, 'endTime': 5974.813},
              {'startTime': 5608.555, 'endTime': 5726.127},
              {'startTime': 17734.164, 'endTime': 17853.51},
              {'startTime': 6612.054, 'endTime': 6729.235},
              {'startTime': 17117.536, 'endTime': 17237.341},
              {'startTime': 21114.107, 'endTime': 21233.315},
              {'startTime': 10677.524, 'endTime': 10786.595},
              {'startTime': 16380.996, 'endTime': 16499.338},
              {'startTime': 10823.715, 'endTime': 10943.506}]
    assert calc_result == answer
    
def test_algo3_5(med_file):
    calc_result = algo3_5.run(
        data=med_file,
        min_=0.5,
        limit=10,
        goal='num_emo',
        save_json=False
    )
    answer = [{'startTime': 0.0, 'endTime': 119.562},
              {'startTime': 765.512, 'endTime': 882.645},
              {'startTime': 891.677, 'endTime': 1008.99},
              {'startTime': 259.889, 'endTime': 375.413},
              {'startTime': 127.098, 'endTime': 234.249},
              {'startTime': 383.298, 'endTime': 495.599},
              {'startTime': 630.41, 'endTime': 741.233},
              {'startTime': 1018.379, 'endTime': 1131.467},
              {'startTime': 507.003, 'endTime': 626.884},
              {'startTime': 1138.629, 'endTime': 1256.19}]
    assert calc_result == answer