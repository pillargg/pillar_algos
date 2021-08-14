"""
Sorts the final results by `perc_rel_unique`. Calculated as "number of chatters
at timestamp"/"number of chatters in that one hour"

HOW TO
    algo1.run(data, clip_length=2, limit=10, sort_by='rel', save_json = False)
"""

import pandas as pd
from .helpers import data_handler as d
from icecream import ic

class featureFinder():
    def __init__(self, data, clip_length:int, limit:int, sort_by:str) -> list:
        """
        Runs algo1 to sort timestamps by the relative percentage of chatters by default.

        input:
        ------
        data: list
            List of dictionaries of data from Twitch chat
        clip_length: int
            Approximate number of minutes each clip should be
        limit: int or None
            Number of rows/dictionaries/timestamps to return
        sort_by: str
            'perc_rel_unique': "number of chatters at timestamp"/"number of chatters at that hour"
            'perc_abs_unique': "number of chatters at timestamp"/"total number of chatters in stream"
        save_json: bool
            True if want to save results as json to exports folder
        """
        self.big_df = data[0]  # fetch appropriate data
        self.first_stamp = data[1]
        self.chunks_list = data[2]
        self.vid_id = data[3]
        
        self.clip_length = clip_length
        self.limit = limit
        self.sort_by = sort_by

    def run(self):
        results = self.hour_iterator()

        return results

    def perc_uniques(self, chunk_list, clip_length, total_uniques, big_unique):
        """
        Finds the percent unique chatters for each dataframe in the list. Dataframes
        assumed to be split using xminChats.find_rest.
        """

        perc_unique = {
            f"{clip_length}min_chunk": [],
            "start": [],
            "end": [],
            "num_unique": [],
            "perc_rel_unique": [],
            "perc_abs_unique": [],
        }
        for i in range(len(chunk_list)):
            # calcuate
            chunk = chunk_list[i]
            unique = len(chunk["_id"].unique())
            timestamp = [
                chunk["created_at"].min(),
                chunk["created_at"].max(),
            ]
            # this is the total uniques in THAT DATAFRAME, ie the hourly cut
            perc_rel = (unique / total_uniques)
            # this is the total uniques in the entire twitch session
            perc_abs = (unique / big_unique)
            # store
            perc_unique[f"{clip_length}min_chunk"].append(chunk)
            perc_unique["start"].append(timestamp[0])
            perc_unique["end"].append(timestamp[1])
            perc_unique["num_unique"].append(unique)
            perc_unique["perc_rel_unique"].append(perc_rel)
            perc_unique["perc_abs_unique"].append(perc_abs)

        df_unique = pd.DataFrame(perc_unique)
        df_unique["elapsed"] = df_unique["end"] - df_unique["start"]
        return df_unique

    def hour_iterator(self):
        """
        Pushes all dfs in a list through the xminChats function, returns a dataframe of results

        input
        -----
        big_df: pd.DataFrame
            Df of the entire twitch session. This is the one that was split by dfSplitter class
        clip_length: int
            How long a timestamp range should be
        sort_by: str
            Whether to sort values by `absolute` or `relative` unique chatters.
        """
        ds = d.dfSplitter(self.big_df)  # initiate
        ds.find_rest()  # split big_df into 1 hour long separate dfs
        # result stored in class var. NOTE: index 0 is always the 
        # very first timestamp of big_df
        hour_list = (ds.result)
        hour_list = hour_list[1:]

        # initiate empty results df
        results = pd.DataFrame(
            columns=[
                "hour",
                f"{self.clip_length}min_chunk",
                "start",
                "end",
                "num_unique",
                "perc_rel_unique",
                "perc_abs_unique",
            ]
        )
        max_uniques = len(
            self.big_df["_id"].unique()
        )  # the total number of unique chatters for the entire twitch session

        # iterate all sections through the class
        for i in range(len(hour_list)):
            hour_df = hour_list[i]
            fm = d.xminChats(hour_df, max_uniques, min_=self.clip_length)
            chunk_list = fm.result  # get back list of dfs, each 2 minutes long

            hr_uniques = self.perc_uniques(chunk_list, self.clip_length,
                                           total_uniques=fm.total_uniques,
                                           big_unique=fm.big_unique)
            hr_uniques["hour"] = i + 1
            self.df_unique = hr_uniques
            results = results.append(hr_uniques)
        ic(len(results))
        results = self.finalizer(results)

        return results # results sorted by percent unique

    def finalizer(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        '''
        Sorts and clips final dataframe as requested
        '''
        from icecream import ic
        dataframe['vid_id'] = self.vid_id
        dataframe = dataframe.sort_values(self.sort_by, ascending=False)
        if type(self.limit) == int:
            dataframe = dataframe.head(self.limit)
        return dataframe