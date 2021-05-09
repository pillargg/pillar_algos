"""
This script finds the number of words/emojis/both depending on `goal` variable,
isolates to each `min_` timestamp, and sorts the resulting df by largest number

HOW TO
    algo3_5.run(data, min_=2, limit=10, goal='num_words_emo', save_json = False)
"""
import pandas as pd
from .helpers import data_handler as d


def thalamus(big_df, min_, goal="num_words"):
    """
    Calculates num_words/emoji/both then runs through functions to
    split big_df, format for saving, and save as json

    input
    -----
    big_df: pd.DataFrame
        twitch stream chat dataframe
    min_: int
        number of minutes each chunk should be
    goal: str
        one of `num_words`, `num_emo`, or `num_words_emo`
    """
    # cut
    big_df = algorithm(big_df)
    first_stamp, chunk_list = d.get_chunks(big_df, min_=min_)
    chunk_df = pd.DataFrame(columns=chunk_list[0].columns)
    for chunk in chunk_list:
        chunk_df = chunk_df.append(chunk)

    results = results_formatter(chunk_df, goal=goal) # sorted by top goal
    return results, first_stamp


def algorithm(big_df):
    # find number of words+emojis
    big_df = num_words_in_chat(big_df)
    if 'emoticons' in big_df.columns:
        
        # find number of emojis
        big_df["num_emo"] = big_df["emoticons"].apply(
            lambda x: len(x) if type(x) == list else 0
        )

    else: 
        big_df["num_emo"] = 0
    # find number of words only
    big_df["num_words"] = big_df["num_words_emo"] - big_df["num_emo"]
    return big_df



def results_formatter(dataframe, goal):
    """
    Creates a new df `results` that contains the total number of words in the dataframe, the time
    the time the dataframe started and ended
    input
    -----
    dataframe: pd.DataFrame
        Dataframe with all the hours and chunks labeled, and num_words calculated
    goal: str
        Col name that has calculated results (ex: num_words, chat_rate, etc.)
    output
    ------
    results: pd.DataFrame
        Dataframe with `hour`, `chunk`, `start`, `end`, `num_words` columns
    """
    hour_list = []
    chunk_list = []
    time_start_list = []
    time_end_list = []
    goal_list = []

    dataframe = dataframe.sort_values("created_at")
    # label each chunk with unique ID
    dataframe["category"] = dataframe["hour"].astype(str) + dataframe["chunk"].astype(
        str
    )

    for cat in dataframe["category"].unique():
        temp_df = dataframe[dataframe["category"] == cat]
        hour_list.append(temp_df.iloc[0, -3])  # assumes hour col is 3 from end
        chunk_list.append(temp_df.iloc[0, -2])  # assumes hunk col is 2 from end
        time_start_list.append(temp_df.iloc[0, 0])  # assume created_at col is first
        time_end_list.append(temp_df.iloc[-1, 0])  # assume created_at col is first
        goal_list.append(temp_df[goal].sum())

    results = pd.DataFrame(
        {
            "hour": hour_list,
            "chunk": chunk_list,
            "start": time_start_list,
            "end": time_end_list,
            goal: goal_list,
        }
    )
    results = results.reset_index(drop=True).sort_values(goal, ascending = False) 
    
    return results


def num_words_in_chat(dataframe):
    """
    Creates a new col `num_words_emo` that contains the number of words in each message
    """
    word_bag = []
    body_split = dataframe["body"].str.split(" ")  # split each string at the whitespace
    for row in body_split:
        num_words = len(row)
        word_bag.append(num_words)

    dataframe["num_words_emo"] = word_bag
    return dataframe


def run(data, min_=2, limit=10, goal="num_words_emo", save_json=False):
    """
    Runs algo3_5 to sort timestamps by the number of words+emojis by default.

    input
    ------
    data: list
        List of dictionaries of data from Twitch chat
    min_: int
        Approximate number of minutes each clip should be
    limit: int
        Number of rows/dictionaries/timestamps to return
    goal: str
        'num_words': sum of the number of words in each chat message
        'num_emo': sum of the number of emoticons in each chat message
        'num_words_emo': sum of the number of words + emoticons in each chat message
    save_json: bool
        True if want to save results as json to exports folder

    output
    ------
    json_results: list
        List of dictionaries in json format, ordered from predicted best to worst candidates.
            Ex: [{start:TIMESTAMP_INT, end:TIMESTAMP_INT}]
    """
    data = pd.DataFrame.from_records(data)
    big_df = d.organize_twitch_chat(data)  # fetch appropriate data
    if type(big_df) == pd.DataFrame:
        results, first_stamp = thalamus(big_df, min_, goal=goal)
        results = results.head(limit)
        
        # results_jsonified sorts by top calc
        json_results = d.results_jsonified(results, first_stamp, goal)
        if save_json:
            d.save_json(json_results, f"algo3.5_{goal}")

        return json_results
    else:
        return big_df # this is an empty numpy array if it is not a DF.