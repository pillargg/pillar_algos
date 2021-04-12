"""
This script finds the mean chat_rate per unique user per `min_` min chunk,
isolates to each `min_` timestamp, and sorts the resulting df by largest number

HOW TO
    algo2.run(data, min_=2, save_json = False)
"""
import pandas as pd
import datetime as dt
from .helpers import data_handler as d


def thalamus(dataframe, min_):
    """
    Formats data for rate_finder(), gets chunk_list to pass through rate_finder
    """
    # split into hours
    dfs = d.dfSplitter(dataframe)
    dfs.find_rest()
    hour_list = dfs.result
    first_stamp = hour_list[0]
    del hour_list[0]
    # label each dataset so we can tell what hour they came from
    for i in range(len(hour_list)):
        hour_list[i].loc[:, "hour"] = i

    # split hours into 2 minute chunks
    chunk_list = []
    for hour in hour_list:
        xmc = d.xminChats(
            hour, dataframe["_id"].unique(), min_=2
        )  # split into 2 min segments
        xmc.find_rest()

        for chunk in xmc.result:
            chunk_list.append(chunk)  # fmc.result gets returned as a list

    chat_rates = pd.DataFrame(
        columns=["hour", "chunk", "start", "end", "_id", "num_chats", "chats_per_2min"]
    )

    # for each 2 min chunk
    for chunk in chunk_list:
        hour = chunk.loc[:, "hour"].iloc[-1]
        # find the chat rate for each user
        chat_rates = chat_rates.append(rate_finder(dataframe=chunk, hour=hour, x=2))

    chat_rates = chat_rates.reset_index(drop=True)
    chat_rates.sort_values("chats_per_2min", ascending=False).head()

    return chat_rates, first_stamp


def rate_finder(dataframe, hour, x=2):
    """
    Finds the rate of messages sent per X minutes for each user in the dataframe.

    NOTE: if only 1 timestamp in chunk dataframe, assumes the chunk is exactly 2 minutes before the next chunk in the entire twitch chat stream
    """
    # Initiate new df
    chat_rate_df = pd.DataFrame(
        columns=[
            "hour",
            "chunk",
            "start",
            "end",
            "_id",
            "num_chats",
            f"chats_per_{x}min",
        ]
    )
    chatters = dataframe["_id"].unique()  # id unique chatters for this chunk

    for i in range(len(chatters)):
        temp_df = dataframe[dataframe["_id"] == chatters[i]]  # isolate chatter's data
        hour = hour
        chunk = i
        time_start = dataframe.iloc[0, 0]
        time_end = dataframe.iloc[-1, 0]
        _id = chatters[i]
        num_chats = len(temp_df["body"])  # count how many chats were sent by them
        time_d = dt.timedelta.total_seconds(
            dataframe.iloc[-1, 0] - dataframe.iloc[0, 0]
        )

        if time_d > 0:
            chat_rate = (
                (num_chats / time_d) * 60 * x
            )  # use time_d to calculate chat/sec, then multiply to get user requested rate
        elif time_d == 0:
            # if there is only 1 message in the chunk, there will be only 1 timestamp
            # in that case assume that time_d = 2
            time_d = 2
            chat_rate = (num_chats / time_d) * 60 * x  # convert to chat/X minutes
        else:
            chat_rate = (
                -100
            )  # if number is negative, math is wrong somewhere and needs to be looked into

        # gather results
        results = pd.DataFrame(
            {
                "hour": [hour],
                "chunk": [chunk],
                "start": [time_start],
                "end": [time_end],
                "_id": [_id],
                "num_chats": [num_chats],
                f"chats_per_{x}min": [chat_rate],
            }
        )

        chat_rate_df = chat_rate_df.append(results)  # store in df
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
    results, first_stamp = thalamus(big_df, min_)
    results = results.head(limit)
    json_results = d.results_jsonified(results, first_stamp, f"chats_per_{min_}min")

    if save_json:
        d.save_json(json_results, f"algo2_mean_rate_per_{min_}min")

    return json_results
