'''
Coordinates all 4 algorithms, then compares across results to see if any timestamps are shared between them
'''
import pandas as pd
from pillaralgos import algo1, algo2, algo3_0, algo3_5
import json
import numpy as np

def run(data, x, limit=None):
    '''
    Coordinates all 4 algorithms, then compares across results to see if any timestamps are shared between them. Runs all algos on default param settings.
    
    input
    -----
    data: list
        List of dictionaries, like a json file in the format [{'startTime':float, 'endTime':float}]
    x: int
        Cutoff for how many algos should have a timestamp for it to be included in the results
    limit: int or None
        How many results should be returned. If None, all results surviving the X filter will be returned.
    
    output
    ------
    new_json: list
        List of dictionaries, [{'startTime':float, 'endTime':float}]
    '''
    # gather results from algos
    results = []
    for algo in [algo1, algo2, algo3_0, algo3_5]:
        result = algo.run(data, min_=2)
        results.append(result)

    # turn results into df
    results_df = pd.DataFrame(columns=['startTime','endTime'])
    for i in range(len(results)):
        result = results[i]
        result = pd.DataFrame(result)
        results_df = results_df.append(result)

    # get valuecounts as a list, filter out timestamps that only occur once
    common = list(results_df['startTime'].value_counts()[results_df['startTime'].value_counts(sort=True) > x].index)

    common_results = pd.DataFrame(columns=['startTime','endTime'])

    for i, row in results_df.iterrows():
        if row['startTime'] in common:
            common_results = common_results.append(row)

    common_results = common_results.drop_duplicates()

    new_json = []
    for i, row in common_results.iterrows():
        new_json.append({'startTime':row['startTime'], 'endTime':row['endTime']})
        
    if not new_json:
        return np.array()

    if limit == None:
        return new_json
    else:
        return new_json[:limit]