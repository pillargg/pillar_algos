"""
This script finds the mean chat_rate per unique user per `clip_length` min chunk,
isolates to each `clip_length` timestamp, and sorts the resulting df by largest number

HOW TO
    algo2.run(data)
"""
import pandas as pd
from helpers import exceptions as e
from abstracts import abstractAlgos


class featureFinder(abstractAlgos):
    def __init__(self, data: tuple) -> pd.DataFrame:
        """
        Runs algo2 to find the chat_rate per unique user per chunk, takes the means for each chunk.
        "Chat rate" is defined as "number of chats sent per minute" using the equation:
            (number of messages sent by the user)
            -------------------------------------    * 60
            (length of chunk in seconds)

        input
        ------
        data: tuple where the index 1 contains chunk_df

        output
        ------
        results: dataframe
            Dataframe with feature columns of:
                'mean_chat_rate_per_minute'
        """
        self.first_stamp = data[0]
        self.chunk_data = data[1]
        self.vid_id = data[2]

    def run(self):
        """
        Coordinates finding chat rate
        """
        # find specifically how long (in seconds) each chunk is
        self.chunk_data["elapsed"] = self.chunk_data["end"] - self.chunk_data["start"]
        self.chunk_data["seconds_elapsed"] = self.chunk_data["elapsed"].apply(
            lambda x: x.total_seconds()
        )

        # if a chunk has 1 chat, will use the mean to calculate chat rate
        self.mean_total_seconds = self.chunk_data["seconds_elapsed"].mean()

        chat_rates = pd.DataFrame()
        for start_time in self.chunk_data["start"].unique():
            chunk = self.chunk_data[self.chunk_data["start"] == start_time]
            # find the chat rate for each user
            chat_rates = chat_rates.append(self.rate_finder(chunk))

        results = self.clean_dataframe(chat_rates)

        return results

    def rate_finder(self, dataframe: pd.DataFrame):
        """
        Finds the rate of messages sent per minute for each user in the dataframe (assumed to be a chunk).

        NOTE: if seconds_elapsed is < 1,
        """
        chatters = dataframe["_id"].unique()  # id unique chatters for this chunk
        seconds_elapsed_list = dataframe["seconds_elapsed"].unique()
        num_unique_elapsed = len(seconds_elapsed_list)
        if num_unique_elapsed == 1:
            seconds_elapsed = seconds_elapsed_list[0]  # chunks are one length
        else:
            raise e.ExpectedOneValueError(num_unique_elapsed)

        if len(dataframe) == 1:
            # sometimes a chunk only has 1 chat in it. In this case the seconds_elapsed will be 0
            seconds_elapsed = self.mean_total_seconds

        chat_rate = {}
        for user in dataframe["_id"].unique():
            num_chats = len(dataframe[dataframe["_id"] == user])
            chat_rate[user] = (num_chats / seconds_elapsed) * 60
        dataframe["chats_sent_per_minute"] = dataframe["_id"].map(chat_rate)
        return dataframe

    def clean_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Groups dataframe by start/end and then sums each column to only include 1 stat per chunk
        """
        # find the mean chat rate per chunk
        dataframe = dataframe.groupby(["start", "end"]).mean().reset_index()
        dataframe = dataframe.rename(
            {"chats_sent_per_minute": "mean_chat_rate_per_minute"}, axis=1
        )
        dataframe = dataframe[["start", "end", "mean_chat_rate_per_minute"]]
        return dataframe
