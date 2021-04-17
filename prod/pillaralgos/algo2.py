"""
This script finds the mean chat_rate per unique user per `min_` min chunk,
isolates to each `min_` timestamp, and sorts the resulting df by largest number

HOW TO
    algo2.run(data, min_=2, limit=10, save_json = False)
"""
import pandas as pd
import datetime as dt
from .helpers import data_handler as d


def thalamus(dataframe, min_):
    """
    Formats data for rate_finder(), gets chunk_list to pass through rate_finder
    """
    # split into hours
    first_stamp, chunk_list = d.get_chunks(dataframe, min_=min_)
    
    chat_rates = pd.DataFrame(
        columns=["hour", "chunk", "start", "end", "_id", "num_chats", f"chats_per_{min_}min"]
    )
    # for each 2 min chunk
    for chunk in chunk_list:
        # find the chat rate for each user
        chat_rates = chat_rates.append(rate_finder(dataframe=chunk, x = min_))

    chat_rates = chat_rates.reset_index(drop=True)
    chat_rates_mean = chat_rates.groupby(['start','end']).mean().reset_index()
    chat_rates_mean = chat_rates_mean.sort_values(f"chats_per_{min_}min", ascending=False) # sorted by top mean chat rates
    

    return chat_rates_mean, first_stamp


def rate_finder(dataframe, x=2):
    """
    Finds the rate of messages sent per X minutes for each user in the dataframe (assumed to be a chunk).

    NOTE: if only 1 timestamp in chunk dataframe, assumes the chunk is exactly X minutes before the next chunk in the entire twitch chat stream
    """
    # Initiate new df
    id_results_all = pd.DataFrame(
        columns=[
            "_id",
            "num_chats",
            f"chats_per_{x}min",
        ]
    )
    chatters = dataframe["_id"].unique()  # id unique chatters for this chunk
    hour = dataframe['hour'].unique()[0] # each hour is the same 
    chunk = dataframe['chunk'].unique()[0] # each chunk is the same
    time_start = dataframe.iloc[0, 0] 
    time_end = dataframe.iloc[-1, 0]
    time_d = dt.timedelta.total_seconds(time_end - time_start)
    for i in range(len(chatters)):
        temp_df = dataframe[dataframe["_id"] == chatters[i]]  # isolate chatter's data

        _id = chatters[i]
        num_chats = len(temp_df["body"])  # count how many chats were sent by them

        if time_d > 0:
            chat_rate = (
                (num_chats / time_d) * 60 * x
            )  # use time_d to calculate chat/sec, then multiply to get user requested rate
        elif time_d == 0:
            # if there is only 1 message in the chunk, there will be only 1 timestamp
            # in that case assume that time_d = X
            time_d = x
            chat_rate = (num_chats / time_d) * 60 * x  # convert to chat/X minutes
        else:
            chat_rate = (
                -100
            )  # if number is negative, math is wrong somewhere and needs to be looked into

        # gather results
        id_results = pd.DataFrame(
            {
                "_id": [_id],
                "num_chats": [num_chats],
                f"chats_per_{x}min": [chat_rate],
            }
        )
        id_results_all = id_results_all.append(id_results)  # store in df
    
    chat_rate_df = id_results_all.copy()
    chat_rate_df['hour'] = hour
    chat_rate_df['chunk'] = chunk
    chat_rate_df['start'] = time_start
    chat_rate_df['end'] = time_end
    return chat_rate_df.reset_index(drop=True)


def run(data, min_=2, limit=10, save_json=False):
    """
    Runs algo2 to find the mean chat_rate per unique user per `min_` chunk,
    takes the means for each chunk, and then sorts by the highest mean rate.

    input
    ------
    data: list
        List of dictionaries of data from Twitch chat
    min_: int
        Approximate number of minutes each clip should be
    limit: int
        Number of rows/dictionaries/timestamps to return
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
        results, first_stamp = thalamus(big_df, min_)
        results = results.head(limit)
        # results_jsonified sorts by top calc
        json_results = d.results_jsonified(results, first_stamp, f"chats_per_{min_}min")

        if save_json:
            d.save_json(json_results, f"algo2_mean_rate_per_{min_}min")

        return json_results
    else:
        return big_df # this is an empty numpy array if it is not a DF.