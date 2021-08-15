"""
Finds the number of users per stream, hour, chunk and some ratios of them

HOW TO
    algo1.run(data)
"""
import pandas as pd


class featureFinder:
    def __init__(self, data: tuple) -> pd.DataFrame:
        """
        Runs algo1 to find the number of unique users per stream, hour, and chunk.

        input:
        ------
        data: tuple where the index 1 contains chunk_df

        output
        ------
        results: dataframe
            Dataframe with columns of:
                'stream_unique_users': number of unique users in the stream
                'hour_unique_users': number of unique users that hour
                'chunk_unique_users': number of unique users that chunk
                'chunk_to_stream_unique_users': ratio of chunk:stream unique users
                'chunk_to_hour_unique_users': ratio of chunk:hour unique users

        """
        self.first_stamp = data[0]
        self.chunk_data = data[1]
        self.vid_id = data[2]

    def run(self):
        unique_users = self.perc_unique_users(self.chunk_data)
        results = self.clean_dataframe(unique_users)
        return results

    def perc_unique_users(self, dataframe):
        """
        Finds the percent unique chatters for each chunk
        """
        total_unique_users = len(dataframe["_id"].unique())
        self.total_unique_users = total_unique_users
        hour_unique_users = self.num_unique_users(dataframe, "hour")
        chunk_unique_users = self.num_unique_users(dataframe, "start")

        # number of unique users to dataframe
        dataframe["hour_unique_users"] = dataframe["hour"].map(hour_unique_users)
        dataframe["chunk_unique_users"] = dataframe["start"].map(chunk_unique_users)

        # get ratio of chunk:stream unique users
        dataframe["chunk_to_stream_unique_users"] = (
            dataframe["chunk_unique_users"] / total_unique_users
        )
        # get ratio of chunk:hour unique users
        dataframe["chunk_to_hour_unique_users"] = (
            dataframe["chunk_unique_users"] / dataframe["hour_unique_users"]
        )

        return dataframe

    def num_unique_users(self, dataframe: pd.DataFrame, filter_col: str) -> dict:
        """
        Counts the number of users after filtering dataframe by filter_col
        """
        num_users_dict = {}
        for prop in dataframe[filter_col].unique():
            temp_df = dataframe[dataframe[filter_col] == prop]
            num_users = len(temp_df["_id"].unique())
            num_users_dict[prop] = num_users

        return num_users_dict

    def clean_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Groups dataframe by start/end and then sums each column to only include 1 stat per chunk
        """
        # take the mean, since each row in the unique_users columns have the same number
        # for each chunk
        dataframe = dataframe.groupby(["start", "end"]).mean().reset_index()
        dataframe = dataframe[
            [
                "start",
                "end",
                "hour_unique_users",
                "chunk_unique_users",
                "chunk_to_stream_unique_users",
                "chunk_to_hour_unique_users",
            ]
        ]
        dataframe["stream_unique_users"] = self.total_unique_users
        return dataframe
