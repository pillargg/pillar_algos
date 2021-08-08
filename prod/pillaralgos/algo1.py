"""
Sorts the final results by `perc_rel_unique`. Calculated as "number of chatters
at timestamp"/"number of chatters in that one hour"

HOW TO
    algo1.run(data, min_=2, limit=10, sort_by='rel', save_json = False)
"""

import pandas as pd
from helpers import data_handler as d

class featureFinder():
    def __init__(self, data, min_:int, limit:int, sort_by:str) -> list:
        """
        Runs algo1 to sort timestamps by the relative percentage of chatters by default.

        input:
        ------
        data: list
            List of dictionaries of data from Twitch chat
        min_: int
            Approximate number of minutes each clip should be
        limit: int or None
            Number of rows/dictionaries/timestamps to return
        sort_by: str
            'rel': "number of chatters at timestamp"/"number of chatters at that hour"
            'abs': "number of chatters at timestamp"/"total number of chatters in stream"
        save_json: bool
            True if want to save results as json to exports folder
        """
        big_df = data[0]  # fetch appropriate data
        first_stamp = data[1]
        chunks_list = data[2]
        vid_id = data[3]
        self.limit = limit
        self.sort_by = sort_by
        results = self.hour_iterator(big_df, min_=min_)

        return results

    def perc_uniques(self, chunk_list, min_, total_uniques, big_unique):
        """
        Finds the percent unique chatters for each dataframe in the list. Dataframes
        assumed to be split using xminChats.find_rest.
        """

        perc_unique = {
            f"{min_}min_chunk": [],
            "start": [],
            "end": [],
            "num_unique": [],
            "perc_rel_unique": [],
            "perc_abs_unique": [],
        }

        for i in range(len(chunk_list)):
            # calcuate
            chunk = i
            unique = len(chunk_list[i]["_id"].unique())
            timestamp = [
                chunk_list[i]["created_at"].min(),
                chunk_list[i]["created_at"].max(),
            ]
            perc_rel = (
                unique / total_uniques
            )  # this is the total uniques in THAT DATAFRAME, ie the hourly cut
            perc_abs = (
                unique / big_unique
            )  # this is the total uniques in the entire twitch session
            # store
            perc_unique[f"{min_}min_chunk"].append(chunk)
            perc_unique["start"].append(timestamp[0])
            perc_unique["end"].append(timestamp[1])
            perc_unique["num_unique"].append(unique)
            perc_unique["perc_rel_unique"].append(perc_rel)
            perc_unique["perc_abs_unique"].append(perc_abs)

        df_unique = pd.DataFrame(perc_unique)
        df_unique["elapsed"] = df_unique["end"] - df_unique["start"]
        return df_unique


    def hour_iterator(self, big_df, min_):
        """
        Pushes all dfs in a list through the xminChats function, returns a dataframe of results

        input
        -----
        big_df: pd.DataFrame
            Df of the entire twitch session. This is the one that was split by dfSplitter class
        min_: int
            How long a timestamp range should be
        sort_by: str
            Whether to sort values by `abs` or `rel` unique chatters.
        """
        ds = d.dfSplitter(big_df)  # initiate
        ds.find_rest()  # split big_df into 1 hour long separate dfs
        hour_list = (
            ds.result
        )  # result stored in class var. NOTE: index 0 is always the very first timestamp of big_df
        first_sec = hour_list[0]
        hour_list = hour_list[1:]

        # initiate empty results df
        results = pd.DataFrame(
            columns=[
                "hour",
                f"{min_}min_chunk",
                "start",
                "end",
                "num_unique",
                "perc_rel_unique",
                "perc_abs_unique",
            ]
        )
        max_uniques = len(
            big_df["_id"].unique()
        )  # the total number of unique chatters for the entire twitch session

        # iterate all sections through the class
        for i in range(len(hour_list)):
            fm = d.xminChats(hour_list[i], max_uniques, min_=min_)
            chunk_list = fm.result  # get back list of dfs, each 2 minutes long

            hr_uniques = self.perc_uniques(
                chunk_list, min_, total_uniques=fm.total_uniques, big_unique=fm.big_unique
            )
            hr_uniques["hour"] = i + 1
            results = results.append(hr_uniques)

        results = self.finalizer(results)

        return results # results sorted by percent unique

    def finalizer(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        '''
        Sorts and clips final dataframe as requested
        '''
        dataframe['vid_id'] = self.vid_id
        dataframe = dataframe.sort_values(self.sort_by, ascending=False)
        if type(self.limit) == int:
            dataframe = dataframe.head(self.limit)

        return dataframe