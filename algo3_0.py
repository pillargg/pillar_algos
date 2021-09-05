"""
This script counts how many times the top {5} users participated at each chunk

HOW TO
    algo3_0.run(data)
"""
import pandas as pd
from helpers.abstracts import abstractAlgos


class featureFinder(abstractAlgos):
    def __init__(self, data: tuple) -> pd.DataFrame:
        """
        Runs algo3_0 to find:
        - num_chats_by_top_emoji_users: the number of messages sent by top 5 emoji users at each chunk
        - num_chats_by_top_words_users: the number of messages sent by top 5 words users at each chunk
        - num_chats_by_top_words_emoji_users: the number of messages sent by top 5 words and emoji users at each chunk

        input
        ------
        data: tuple where the index 1 contains chunk_df

        output
        ------
        results: dataframe
            Dataframe with feature columns of:
                'num_chats_by_top_emoji_users'
                'num_chats_by_top_words_users'
                'num_chats_by_top_words_emoji_users'
        """
        self.chunk_df = data[1]

    def run(self):
        """
        Coordinates the other functions in this algo.
        """
        # count the number of words/emojis/both sent per id at each chunk
        id_words = self.id_words_counter(self.chunk_df)
        results = self.clean_dataframe(id_words)

        return results

    def id_words_counter(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Returns a dataframe with all user IDs and the number of words/emojis/combined
        they each sent, sorted by top senders

        my_list: list of chunks
        """
        dataframe["mean_words_emoji_sent"] = (
            dataframe["body"].str.split(" ").apply(lambda x: len(x))
        )
        if "emoticons" in dataframe.columns:
            dataframe["mean_emoji_sent"] = dataframe["emoticons"].apply(
                lambda x: 0 if type(x) == float else len(x)
            )
        else:
            dataframe["mean_emoji_sent"] = 0.0
        dataframe["mean_words_sent"] = (
            dataframe["mean_words_emoji_sent"] - dataframe["mean_emoji_sent"]
        )

        dataframe = dataframe.astype(
            {
                "_id": str,
                "mean_words_emoji_sent": int,
                "mean_emoji_sent": int,
                "mean_words_sent": int,
            }
        )

        # find the top X users who sent the most number of words/emoji/both
        ids_sum_spam = dataframe.groupby("_id").sum()

        self.top_id_words_emoji = self.id_categorizer(
            ids_sum_spam, "mean_words_emoji_sent", top=5
        )
        self.top_id_emoji = self.id_categorizer(ids_sum_spam, "mean_emoji_sent", top=5)
        self.top_id_words = self.id_categorizer(ids_sum_spam, "mean_words_sent", top=5)

        # check whether each row's user is in the list of top_id_X
        dataframe["num_chats_by_top_emoji_users"] = dataframe["_id"].apply(
            lambda x: True if x in self.top_id_emoji else False
        )
        dataframe["num_chats_by_top_words_users"] = dataframe["_id"].apply(
            lambda x: True if x in self.top_id_words else False
        )
        dataframe["num_chats_by_top_words_emoji_users"] = dataframe["_id"].apply(
            lambda x: True if x in self.top_id_words_emoji else False
        )

        dataframe = dataframe.rename({"index": "spam_rank"}, axis=1)
        dataframe = dataframe.sort_values("created_at").reset_index(drop=True)
        return dataframe

    def id_categorizer(self, dataframe: pd.DataFrame, col: str, top: int) -> str:
        """
        Finds the users that sent the most number of words/emoji/both.

        User ID assumed to be in the index
        """
        dataframe = dataframe.sort_values(col, ascending=False)
        top_df = dataframe.head(top)
        top_users = list(top_df.index)
        return top_users

    def clean_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Groups dataframe by start/end and then sums each column to only include 1 stat per chunk
        """
        dataframe = dataframe.groupby(["start", "end"]).sum().reset_index()
        dataframe = dataframe[
            [
                "start",
                "end",
                "num_chats_by_top_emoji_users",
                "num_chats_by_top_words_users",
                "num_chats_by_top_words_emoji_users",
            ]
        ]
        return dataframe
