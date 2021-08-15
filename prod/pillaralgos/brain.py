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


def format_feature_df(dataframe: pd.DataFrame, select: tuple) -> pd.DataFrame:
    """
    Helper function to create the feature set from which ML algorithm will be trained

    input
    -----
    select: tuple containing, in order, desired algo1, algo2, algo3,
            algo3_5, algo3_6, algo4 features
    """
    feature_df = dataframe[
        [
            "vid_id",
            "startTime",
            "endTime",
            "algo1_metric",
            "algo2_metric",
            "algo3_metric, algo3_5_metric",
            "algo3_6_metric",
            "algo4_metric",
            "ccc_label",
        ]
    ]
    return feature_df


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


def run(vid_id: str, clip_length: int, limit: int = None, select: str = "all"):
    # common settings

    data = json.load(open(f"pillaralgos/data/{vid_id}.json"))
    if len(data) == 0:
        ic(f"{vid_id} is empty")
        return f"{vid_id} is empty"
    important_data = load_data(data, clip_length)

    algo_results = {}
    all_algos = [algo1, algo2, algo3_0, algo3_5, algo3_6, algo4]
    ic("Running algorithms")
    for i in range(len(all_algos)):
        a = all_algos[i].featureFinder(important_data)
        res = a.run()
        formatted = d.data_finalizer(res, vid_id=vid_id)
        if test_results(important_data, formatted):
            algo_results[f"algo_{i}"] = formatted
        else:
            ic(f"algo_{i} failed the test!")
            algo_results[f"algo_{i}"] = formatted

    df = algo_results["algo_0"]
    ic("Merging featuresets")
    for key in algo_results.keys():
        if key != ["algo_0"]:
            df = df.merge(algo_results[key])
    return df