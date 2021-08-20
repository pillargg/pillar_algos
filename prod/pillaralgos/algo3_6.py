"""
Algorithm to analyze emoticon usage in the stream

HOW TO:
    ee = featureFinder(data)
    results = ee.run()
"""
import pandas as pd


class featureFinder:
    def __init__(self, data: list):
        """
        Gets data ready for emoticon analysis. Initializes dicts, lists, etc.

        input
        -----
        data: list
            List where index 0 is the first timestamp, index 1 the chunks dataframe, and index 2 the stream ID
        """
        self.first_stamp = data[0]
        self.chunks_df = data[1]
        self.vid_id = data[2]

    def run(self) -> pd.DataFrame:
        """
        Runs algo3_6 to get some stats on emoticon usage. Emoticons are not counted uniquely, so one
        message with 100 of the same emoticon is recorded as 100 "uses".
            - 'num_emo': the number of emoticons used in the chunk
            - 'chunk_unique_users': the number of users in the chunk
            - 'perc_emoji_of_stream': ratio of emojis in chunk / total emojis in stream
            - 'emoji_user_ratio': ratio of 'emojis in chunk' / 'number of unique chatters in chunk'
        output
        ------
        results: dataframe
            Dataframe with feature columns including:
                - 'num_emo'
                - 'chunk_unique_users'
                - 'perc_emoji_of_stream'
                - 'emoji_user_ratio'
        """
        chunk_df_with_emo_count = self.thalamus()
        results = self.clean_dataframe(chunk_df_with_emo_count)
        return results

    def thalamus(self) -> pd.DataFrame:
        """
        Coordinates all functions to return a dataset of top emojis used
        """
        import pandas as pd

        big_emo = 0  # to count total emoticons per stream

        # get count of total emoticon per chunk and number of users per chunk
        new_chunk_data = pd.DataFrame()
        for start in self.chunks_df["start"].unique():
            chunk = self.chunks_df[self.chunks_df["start"] == start]
            chunk_unique_users = len(chunk["_id"].unique())

            chunk_emo = 0
            chunk_formatted = self.format_df_for_emo(chunk)

            if chunk_formatted.empty:
                # if returned dataframe is empty, no emojis
                chunk_emo += 0
            else:
                for idx, row in chunk_formatted.iterrows():
                    num_emo = self.emo_counter(row)
                    chunk_emo += num_emo

            big_emo += chunk_emo  # add number of emoticons in chunk to total
            chunk["num_emo"] = chunk_emo
            chunk["chunk_unique_users"] = chunk_unique_users
            new_chunk_data = new_chunk_data.append(chunk)

        new_chunk_data["perc_emoji_of_stream"] = new_chunk_data["num_emo"] / big_emo
        new_chunk_data["emoji_user_ratio"] = (
            new_chunk_data["num_emo"] / new_chunk_data["chunk_unique_users"]
        )

        return new_chunk_data

    ### ACTUAL FUNCTIONS ###

    def format_df_for_emo(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Extracts emojis to make them accessible to counter
        """
        # check whether dataframe has any emoticons
        if "emoticons" not in dataframe.columns:
            return pd.DataFrame()
        body_has_emo = dataframe[~dataframe["emoticons"].isna()].reset_index(drop=True)
        if len(body_has_emo.index) == 0:
            return pd.DataFrame()

        # emoticons col contains _id, begin, end. Here we extract just the _id,
        # and put it into a list
        body_has_emo["emo_id_list"] = body_has_emo["emoticons"].apply(
            lambda my_list: [emo_dict["_id"] for emo_dict in my_list]
        )

        return body_has_emo

    ### HELPER FUNCTIONS ###

    def emo_counter(self, row: pd.DataFrame) -> int:
        """
        Counts the number of times an emoticon occurs in the row

        This is a more accessible way of counting, vs making of emoji list and then
        counting the occurrances in there
        """
        # for each emoji_id in the list
        counter = 0
        for emoji_id in row["emo_id_list"]:
            counter += 1
        return counter

    def clean_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Groups dataframe by start/end and then means each column to only include 1 stat per chunk
        """
        dataframe = dataframe.groupby(["start", "end"]).mean().reset_index()
        dataframe = dataframe[
            [
                "start",
                "end",
                "num_emo",
                "chunk_unique_users",
                "perc_emoji_of_stream",
                "emoji_user_ratio",
            ]
        ]
        return dataframe
