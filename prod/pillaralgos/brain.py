'''
This script is responsible for running datasets through each algorithm, tying
the feature outputs into together into one dataset.

HOW TO: brain.run()
'''
import pandas as pd
import numpy as np
import json

from pillaralgos import algo1, algo2, algo3_0, algo3_5, algo3_6, algo4, brain
from pillaralgos.helpers import data_handler as d
from pillaralgos.helpers import exceptions as e

from icecream import ic

### Functions in common across all algos ###
def load_data(data, clip_length):
    """
    Loads and splits data into appropriate chunks 

    output
    ------
        first_stamp: timestamp of the first chat message
        chunk_df: dataframe of chunks, retaining all info from big_df
        vid_id: stream id of chat transcript
    """
    from pillaralgos.helpers import data_handler as dh

    big_df = dh.organize_twitch_chat(data)  # organize
    if type(big_df) == pd.DataFrame:
        first_stamp, chunks_list = dh.get_chunks(big_df, min_=clip_length)
        vid_id = data[0]["content_id"]
        chunk_df = pd.DataFrame()

        for dataframe in chunks_list:
            dataframe = dataframe.sort_values("created_at")
            dataframe["start"] = dataframe.iloc[0, 0]
            dataframe["end"] = dataframe.iloc[-1, 0]
            chunk_df = chunk_df.append(dataframe)

        chunk_df = chunk_df.reset_index(drop=True)
        return (first_stamp, chunk_df, vid_id, chunks_list)
    else:
        return np.array([])


def format_json_results(results, first_stamp, sort_by):
    """
    At the very end, jsonify all results
    """
    from pillaralgos.helpers import data_handler as dh

    json_results = dh.results_jsonified(results, first_stamp, sort_by)

    return json_results


def test_results(data, dataframe):
    """
    Checks that we retained all chunks, and that chunks have start/end times
    """
    from icecream import ic

    num_chunks = len(data[-1])
    num_results = len(dataframe)

    if (
        (num_chunks == num_results)
        & ("start" in dataframe.columns)
        & ("end" in dataframe.columns)
    ):
        return True
    else:
        ic(num_results, num_chunks)
        ic(dataframe.columns)
        return False


def run_algo(algo, data: pd.DataFrame, select: dict, algo_str: str, vid_id: str, label_features: bool) -> pd.DataFrame:
    '''
    Runs the algorithm, formats resulting dataset
    
    input
    -----
    algo: loaded algorithm class
    data: twitch data preformatted and chunkified
    select: "all" or dictionary of lists with columns to select from algo output
    algo_str: name of algorithm
    vid_id: video ID of twitch stream
    label_features: whether or not to label each feature with the algo that made it
    '''
    a = algo.featureFinder(data)
    res = a.run()

    if (type(select) == dict) & (algo_str in select):
        selected_columns = select[algo_str]
    else:
        selected_columns = "all"

    if label_features:
        feature_label = algo_str
    else:
        feature_label = None
    formatted, bad_columns = d.data_finalizer(res, 
                                              vid_id=vid_id, 
                                              select=selected_columns, 
                                              algo_label=feature_label)
    if len(bad_columns) > 1:
        # if there is something in this list, the user defined columns in 
        # selected_columns was not found
        ic(f"{algo_str}: The following columns were not found: {bad_columns}")
    elif len(bad_columns) == 1:
        ic(f"{algo_str}: Column not found: {bad_columns}")

    # check the dataset is proper
    if not test_results(data, formatted):
        ic(f"{algo_str} failed the test!")

    return formatted


def run(vid_id: str, clip_length: float, select_features: dict = "all", dev_mode: bool = False):
    '''
    Formats raw json into dataframe, creates the chunk_df where
    each chunk is of size clip_length, then iterates through each algorithm 
    to get features for each clip.
    
    input
    -----
    vid_id: str
        id of the twitch stream to load
    clip_length: int or float
        length of each clip to be suggested to user
    select_features: str or dict
        either 'all' or a dictionary where keys are one of 'algo1', 'algo2', 
        'algo3_0', 'algo3_5', 'algo3_6', 'algo4' and values a list of str
        representing features to return
        NOTE: see algo docstring for feature options
    dev_mode: bool
        if True, will assume file `vid_id` is located in the data directory
        with a .json file extension, opens it with json.load(open()), provides
        a progress bar for jupyter notebook, and labels each feature with the algo that made it
    '''
    if dev_mode:
        data = json.load(open(f"data/{vid_id}.json"))
        label_features = True
    else:
        data = json.load(open(f"{vid_id}.json"))
        label_features = False
    if len(data) == 0:
        ic(f"{vid_id} is empty")
        return np.array([])
    # load and organize data so that one row is one chunk
    important_data = load_data(data, clip_length)

    # used for select_features parameter
    all_algos_str = ['algo1', 'algo2', 'algo3_0', 'algo3_5', 'algo3_6', 'algo4']
    # the algorithms
    all_algos = [algo1, algo2, algo3_0, algo3_5, algo3_6, algo4]
    ic("Running algorithms")
    algo_results = {}

    if dev_mode:
        # show progress bar in jupyter notebook
        from tqdm.notebook import tqdm
        for i in tqdm(range(len(all_algos))):
            algo_str = all_algos_str[i]
            algo = all_algos[i]

            result = run_algo(algo, important_data, select_features, algo_str, vid_id, label_features)
            algo_results[algo_str] = result
    else:
        # don't show progress bar
        for i in range(len(all_algos)):
            algo_str = all_algos_str[i]
            algo = all_algos[i]

            result = run_algo(algo, important_data, select_features, algo_str, vid_id, label_features)

    ic("Merging featuresets")
    df = algo_results[all_algos_str[0]]
    for key in algo_results.keys():
        if key != all_algos_str[0]:
            df = df.merge(algo_results[key])

    return df