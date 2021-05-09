'''
Coordinates all 4 algorithms, then compares across results to see if any timestamps are shared between them
'''
import pandas as pd
from pillaralgos import algo1, algo2, algo3_0, algo3_5
import json
import numpy as np

def run(data, clip_length, common_timestamps=2, algos_to_compare = ["algo1","algo2","algo3_0","algo3_5"], limit=None):
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
        
    if limit:
        return new_json[:limit]
    else:
        return new_json
