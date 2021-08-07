'''
This file contains a series of classes and functions to help with loading and splitting twitch chat data
also json_saver() that converts given variable into string, saves into .json file
'''
import pandas as pd
import numpy as np
import datetime as dt

# remove the .loc warning. bc I dont acre about writes making it back
# to og dataframe https://stackoverflow.com/a/20627316/9866659
pd.options.mode.chained_assignment = None  # default='warn'

def rename_columns(col_string):
    """
    Renames columns to be more presentable
    """
    if (col_string == "created_at_id") | (col_string == "updated_at_id"):
        col_string = col_string.replace("_id", "")
        return "id_" + col_string
    elif (col_string == "created_at_mess") | (col_string == "updated_at_mess"):
        col_string = col_string.replace("_mess", "")
        return col_string
    else:
        return col_string.replace("_mess", "", 1).replace("_id", "", 1)


def select_columns(dataframe, keep_user_vars=False):
    """
    Removes unneeded columns
    """
    if keep_user_vars:
        # If true, include user columns
        bad_cols = ["display_name_id", "name_id", "user_notice_params_mess"]
    else:
        # If false, not analyzing the users
        bad_cols = [
            "display_name_id",
            "name_id",
            "user_notice_params_mess",
            # these aren't used by the simpler fctns
            "bio_id",
            "created_at_id",
            "updated_at_id",
            "logo_id",
        ]
    dataframe = dataframe.drop(bad_cols, axis=1)
    cols = dataframe.columns
    cols = list(pd.Series(cols).apply(rename_columns))
    dataframe.columns = cols
    return dataframe


def organize_twitch_chat(data, keep_user_vars=False):
    """
    Turns json into dataframe. Expands lists of lists into own columns.

    input
    -----
    data: list
        list of dictionaries in json format, loaded with the `open` context manager.

    output
    ------
    df: pd.DataFrame
        Dataframe with the following columns:
            ['created_at', 'updated_at', 'display_name', '_id', 'name', 'type',
             'bio', 'logo', 'body', 'is_action', 'user_badges', 'emoticons']
    """
    if len(data) > 0:
        data = pd.DataFrame.from_records(data)  # convert to df
        df = data[["created_at", "updated_at", "commenter", "message"]].add_suffix("_mess")

        h = dictExtractor(df["message_mess"], label="_mess")
        messages = h.result
        g = dictExtractor(df["commenter_mess"], label="_id")
        users = g.result

        df = df.drop(["message_mess", "commenter_mess"], axis=1)  # duplicate info
        df = pd.concat([df, users, messages], axis=1)
        # all vars were loaded as str. Change type to datetime/int/bool
        df = df.astype(
            {
                "_id_id": int,
                "bio_id": "category",
                "created_at_id": "datetime64[ns]",
                "created_at_mess": "datetime64[ns]",
                "updated_at_id": "datetime64[ns]",
                "updated_at_mess": "datetime64[ns]",
                "is_action_mess": bool,
                "type_id": "category",
            }
        )
        df = select_columns(df, keep_user_vars)
        return df
    else:
        return np.array([])


class dictExtractor:
    def __init__(self, my_series, label=""):
        """
        Extracts dictionaries from series into a new dict using the
        longest dictionary's keys. Converts new dict into df, stored
        as `self.result`. Because not every dict had same number of keys.

        input
        -----
        my_series: pd.Series
            A column from twitch dataframe where each row is a dict
        label: str
            What will be appended to the end of each col
        """
        # find max length of dicts
        length = my_series.apply(lambda x: len(x))
        y = 0
        for x in length:
            if x > y:
                y = x
        # find index of max keys dict
        ind = length[length == y].index[0]
        max_d = my_series.iloc[ind].keys()
        self.max_d = max_d
        # initiate new dict
        self.new_dict = {}
        for k in max_d:
            self.new_dict[k] = []
        # extract dict values into new dict
        my_series.apply(lambda x: self.keys_iterator(x))
        # store as df
        self.result = pd.DataFrame.from_dict(self.new_dict)
        # df.add_suffix() is actually 0.25 seconds slower
        self.result.columns = [col + label for col in self.result.columns]

    def keys_iterator(self, my_dict):
        """
        Checks that all of the `max_d` are in the given dictionary. If not,
        appends np.nan. Otherwise appends the value.
        """
        for k in self.max_d:
            if k not in my_dict.keys():
                self.new_dict[k].append(np.nan)
            else:
                self.new_dict[k].append(my_dict[k])


class dfSplitter:
    def __init__(self, dataframe):
        """
        Splits dataframe into multiple dataframes, each 1 hour long

        output:
        ------
        my_list: list
            List of dataframes
        """
        # init function finds the first split
        dataframe = dataframe.sort_values("created_at")
        first = dataframe[
            dataframe["created_at"]
            <= dataframe.loc[0, "created_at"] + pd.Timedelta(hours=1)
        ]
        self.last_i = first.index.max()
        self.dataframe = dataframe
        self.result = []  # list to append starting timestamp + datasets to
        self.result.append(
            dataframe.iloc[0, 0]
        )  # NOTE: assumes first col is always "created_at" col
        self.result.append(first)

    def find_rest(self):
        """
        Uses last index of first split to find the others
        """
        dataframe = self.dataframe
        last_i = self.last_i
        if last_i + 1 != len(dataframe):
            new_df = dataframe.loc[last_i + 1 :, :]  # clip df to start at last_i
            newest = new_df[
                new_df["created_at"]
                <= new_df.loc[last_i + 1, "created_at"] + pd.Timedelta(hours=1)
            ]  # filter by hour
            self.result.append(newest)  # store in list
            self.last_i = newest.index.max()

            self.find_rest()  # repeat
        else:
            return dataframe  # never actually used


class xminChats:
    def __init__(self, dataframe, big_unique, min_=2):
        """
        Finds the percent unique chatters that chatted every min_ minutes

        input
        -----
        dataframe: pd.DataFrame
            Twitch chat dataframe organized and split by dfSplitter
        big_unique: int
            Total number of unique chatters for the entire Twitch stream
        min_: int
            Minute range to find timestamps for. Ex: Find 2 min long timestamps.
        """

        # init function finds the first split
        dataframe = dataframe.sort_values("created_at")
        first = dataframe[
            dataframe["created_at"] <= dataframe.iloc[0, 0] + pd.Timedelta(minutes=min_)
        ]

        self.min_ = min_
        self.total_uniques = len(dataframe["_id"].unique())
        self.big_unique = big_unique

        self.last_i = first.index.max()
        self.dataframe = dataframe

        self.result = []
        self.result.append(first)

    def find_rest(self):
        """
        Uses last index of first split to find the others
        """
        dataframe = self.dataframe
        last_i = self.last_i
        if (
            last_i + 1 < dataframe.index.max()
        ):  # NOT len(dataframe), that bugs out and i dont wanna explain why
            new_df = dataframe.loc[
                last_i + 1 :, :
            ]  # clip df to start new min_ min calc at last_i+1
            newest = new_df[
                new_df["created_at"]
                <= new_df.loc[last_i + 1, "created_at"]
                + pd.Timedelta(value=self.min_, unit="minutes")
            ]  # filter by minute
            self.result.append(newest)  # store in list

            self.last_i = newest.index.max()
            self.find_rest()  # repeat
        else:
            x = ""


def get_chunks(dataframe, min_=2):
    """
    Iterates through the data_helper classes to divide dataframe into chunks

    input
    -----
    dataframe: pd.DataFrame
        The entire twitch stream chat df
    min_: int
        The min_ value to pass into xminChats()

    output
    ------
    first_stamp: datetime
        The very first timestamp of dataframe
    chunk_list:
        List of `min_` long dataframes
    """
    dhs = dfSplitter(dataframe)
    dhs.find_rest()
    hour_list = dhs.result

    first_stamp = hour_list[0]
    del hour_list[0]

    chunk_list = []
    for i in range(len(hour_list)):
        hour = hour_list[i]

        dhx = xminChats(hour, dataframe["_id"].unique(), min_=min_)
        dhx.find_rest()
        chunks = dhx.result

        for x in range(len(chunks)):
            chunk = chunks[x]
            chunk["hour"] = i
            chunk["chunk"] = x
            chunk_list.append(chunk)
    return first_stamp, chunk_list


def results_jsonified(results, first_sec, results_col):
    """
    Converts timestamps to seconds, extracts results and makes the whole thing machine readable

    input
    -----
    results: pd.DataFrame
        DataFrame with at least the start (datetime) and end (datetime) columns, and a column to sort by.
    first_sec: datetime
        The very first timestamp in the entire twitch chat log. Used to calculate elapsed time in seconds.
    results_col: str
        Column(s) to sort values by (ascending=False)

    output
    ------
    json_results: list
        List of dictionaries with startTime and endTime keys, sorted by best results at top
    """
    results["first_sec"] = first_sec  # to calculate elapsed time from first sec, in seconds
    results = results.sort_values(
        results_col, ascending=False
    )  # so json format is returned with top result being the most relevant
    json_results = []
    for i, row in results.iterrows():
        og = row["first_sec"]
        start = row["start"]
        end = row["end"]

        start_sec = dt.timedelta.total_seconds(
            start - og
        )  # find difference between first sec and given timestamp, convert that to seconds
        end_sec = dt.timedelta.total_seconds(end - og)

        dict_ = {"startTime": start_sec, "endTime": end_sec}
        json_results.append(dict_)

    return json_results


def save_json(json_results, name):
    """
    Converts list of dict to pure str, then saves as a json file.

    input
    -----
    json_results: list
        List of dictionaries containing results
    name: str
        Filename (with optional directory) to save as. Ex: name.json or exports/name.json
    """
    str_ = "["
    for dict_ in json_results:
        str_ += str(dict_) + ", \n "
    str_ += "]"

    with open(f"{name}.json", "w") as f:
        f.write(str_)
    print(f"Saved to {name}.json")
