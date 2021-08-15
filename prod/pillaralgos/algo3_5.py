"""
This script finds the number of words/emojis/both for each chunk

HOW TO
    algo3_5.run(data)
"""
import pandas as pd


class featureFinder:
    def __init__(self, data: tuple) -> pd.DataFrame:
        """
        Runs algo3_5 to get the number of words/emoji/both for each chunk:
            'num_words': number of words at that chunk
            'num_emo': number of emoticons at that chunk
            'num_words_emo': number words + emoticons at that chunk

        input
        ------
        data: tuple where the index 1 contains chunk_df

        output
        ------
        results: dataframe
            Dataframe with columns of:
                'num_words'
                'num_emo'
                'num_words_emo'
        """
        # unpack data tuple
        self.first_stamp = data[0]
        self.chunk_data = data[1]
        self.vid_id = data[2]

    def run(self):
        """
        Coordinates the other functions in this algo.
        """
        new_chunk_data = self.algorithm(self.chunk_data)
        results = self.clean_dataframe(new_chunk_data)
        return results

    def algorithm(self, dataframe):
        """
        Finds the number of emoticons and words
        """
        # find number of words+emojis
        dataframe = self.num_words_in_chat(dataframe)

        if "emoticons" in dataframe.columns:
            # find number of emojis
            dataframe["num_emo"] = dataframe["emoticons"].apply(
                lambda x: len(x) if type(x) == list else 0
            )

        else:
            dataframe["num_emo"] = 0
        # find number of words only
        dataframe["num_words"] = dataframe["num_words_emo"] - dataframe["num_emo"]
        return dataframe

    def num_words_in_chat(self, dataframe):
        """
        Creates a new col `num_words_emo` that contains the number of words and emoticons in each message
        """
        word_bag = []
        body_split = dataframe["body"].str.split(
            " "
        )  # split each string at the whitespace
        for row in body_split:
            num_words = len(row)
            word_bag.append(num_words)

        dataframe["num_words_emo"] = word_bag
        return dataframe

    def clean_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Groups dataframe by start/end and then sums each column to only include 1 stat per chunk
        """
        # add up the total number of words/emoji/both in each chunk
        dataframe = dataframe.groupby(["start", "end"]).sum().reset_index()
        dataframe = dataframe[["start", "end", "num_words", "num_emo", "num_words_emo"]]
        return dataframe
