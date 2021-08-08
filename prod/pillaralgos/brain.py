'''
Coordinates all 4 algorithms, then compares across results to see if any timestamps are shared between them
'''
import pandas as pd
from pillaralgos import algo1, algo2, algo3_0, algo3_5, algo3_6, algo4
from .helpers import data_handler as dh
import json
import numpy as np


### Functions in common across all algos ###
def load_data(data, clip_length):
    '''
    Loads and splits data into appropriate chunks
    '''
    big_df = dh.organize_twitch_chat(data)  # organize
    if type(big_df) == pd.DataFrame:
        first_stamp, chunks_list = dh.get_chunks(big_df, min_=clip_length)
        vid_id = data[0]["content_id"]
        return (big_df, first_stamp, chunks_list, vid_id)
    else:
        return np.array([])


def format_results(results, first_stamp, sort_by):
    dh.results_jsonified(results, first_stamp, sort_by)

### Run selected algos ###
def run(data, clip_length, common_timestamps=2, algos_to_compare = ["algo1","algo2","algo3_0","algo3_5"], limit=None, save_json=False):
    '''
    Coordinates all 4 algorithms, then compares across results to see if any timestamps are shared between them. Runs all algos on default param settings.
    
    input
    -----
    data: list
        List of dictionaries, like a json file in the format [{'startTime':float, 'endTime':float}]
    common_timestamps: int
        Cutoff for how many algos should have a timestamp for it to be included in the results
    algos_to_compare: list
        List of one of: "algo1","algo2","algo3_0","algo3_5"
    limit: int or None
        How many results should be returned. If None, all results surviving the X filter will be returned.
    
    output
    ------
    new_json: list
        List of dictionaries, [{'startTime':float, 'endTime':float}]
        Or 
    '''
    # load and format data the way each algo expects it
    important_data = load_data(data, clip_length)
    if type(important_data) != list:
        # empty array signifies bad dataset. Russell requested to return empty array in that case
        return {"error": "dataset was empty"}
    
    if len(algos_to_compare) < 1:
        return "algos_to_compare cannot be empty"
    # comply with user input
    compare_us = []
    if "algo1" in algos_to_compare:
        compare_us.append(algo1)
    if "algo2" in algos_to_compare:
        compare_us.append(algo2)
    if "algo3_0" in algos_to_compare:
        compare_us.append(algo3_0)
    if "algo3_5" in algos_to_compare:
        compare_us.append(algo3_5)
    if "algo3_6" in algos_to_compare:
        compare_us.append(algo3_6)
    if "algo4" in algos_to_compare:
        compare_us.append(algo4)
    results = []
    # gather results from algos
    for algo in compare_us:
        result = algo.run(data, min_=clip_length)
        results.append(result)

    # turn results into df
    results_df = pd.DataFrame(columns=['startTime','endTime'])
    for i in range(len(results)):
        result = results[i]
        result = pd.DataFrame(result)
        results_df = results_df.append(result)

    # get valuecounts as a list, filter out timestamps that only occur once
    common = list(results_df['startTime'].value_counts()[results_df['startTime'].value_counts(sort=True) >= common_timestamps].index)

    common_results = pd.DataFrame(columns=['startTime','endTime'])

    for i, row in results_df.iterrows():
        if row['startTime'] in common:
            common_results = common_results.append(row)

    if len(common_results) < 1:
        return np.array()
    
    common_results = common_results.drop_duplicates()
    
    new_json = []
    for i, row in common_results.iterrows():
        new_json.append({'startTime':row['startTime'], 'endTime':row['endTime']})
        
    if save_json:
        dh.save_json(new_json, f"brain")
    if limit:
        return new_json[:limit]
    else:
        return new_json
