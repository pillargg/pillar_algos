"""
This script finds the number of words/emojis/both depending on `select` variable,
isolates to each `clip_length` timestamp, and sorts the resulting df by largest number

HOW TO
    algo3_5.run(data, clip_length=2, limit=10, select='num_words_emo', save_json = False)
"""
import pandas as pd
from .helpers import data_handler as d

class featureFinder():
    def __init__(self, data:list, select:str) -> list:
        """
        Runs algo3_5 to sort timestamps by the number of words+emojis by default.

        input
        ------
        data: list
            List of dictionaries of data from Twitch chat
        clip_length: int
            Approximate number of minutes each clip should be
        limit: int or None
            Number of rows/dictionaries/timestamps to return
        select: str
            'num_words': sum of the number of words in each chat message
            'num_emo': sum of the number of emoticons in each chat message
            'num_words_emo': sum of the number of words + emoticons in each chat message
        save_json: bool
            True if want to save results as json to exports folder

        output
        ------
        json_results: list
            List of dictionaries in json format, ordered from predicted best to worst candidates.
                Ex: [{start:TIMESTAMP_INT, end:TIMESTAMP_INT}]
        """
        # unpack data tuple
        self.first_stamp = data[0]
        self.chunk_df = data[1]
        self.vid_id = data[2]
        
        self.select = select

    def run(self):
        """
        Calculates num_words/emoji/both then runs through functions to
        split big_df, format for saving, and save as json

        input
        -----
        big_df: pd.DataFrame
            twitch stream chat dataframe
        clip_length: int
            number of minutes each chunk should be
        select: str
            one of `num_words`, `num_emo`, or `num_words_emo`
        """
        new_chunk_df = self.algorithm(self.chunk_df)
        return results


    def algorithm(self, dataframe):
        # find number of words+emojis
        if 'emoticons' in dataframe.columns:
            # find number of emojis
            dataframe["num_emo"] = dataframe["emoticons"].apply(
                lambda x: len(x) if type(x) == list else 0)

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
        body_split = dataframe["body"].str.split(" ")  # split each string at the whitespace
        for row in body_split:
            num_words = len(row)
            word_bag.append(num_words)

        dataframe["num_words_emo"] = word_bag
        return dataframe

    ### This is never called, saved just in case
    def results_formatter(self, dataframe, select):
        """
        Creates a new df `results` that contains the total number of words in the dataframe, the time
        the time the dataframe started and ended
        input
        -----
        dataframe: pd.DataFrame
            Dataframe with all the hours and chunks labeled, and num_words calculated
        select: str
            Col name that has calculated results (ex: num_words, chat_rate, etc.)
        output
        ------
        results: pd.DataFrame
            Dataframe with `hour`, `chunk`, `start`, `end`, `num_words` columns
        """
        hour_list = []
        chunk_list = []
        time_start_list = []
        time_end_list = []
        select_list = []

        dataframe = dataframe.sort_values("created_at")
        # label each chunk with unique ID
        dataframe["category"] = dataframe["hour"].astype(str) + dataframe["chunk"].astype(
            str
        )

        for cat in dataframe["category"].unique():
            temp_df = dataframe[dataframe["category"] == cat]
            hour_list.append(temp_df.iloc[0, -3])  # assumes hour col is 3 from end
            chunk_list.append(temp_df.iloc[0, -2])  # assumes hunk col is 2 from end
            time_start_list.append(temp_df.iloc[0, 0])  # assume created_at col is first
            time_end_list.append(temp_df.iloc[-1, 0])  # assume created_at col is first
            select_list.append(temp_df[select].sum())

        results = pd.DataFrame(
            {
                "hour": hour_list,
                "chunk": chunk_list,
                "start": time_start_list,
                "end": time_end_list,
                select: select_list,
            }
        )
        results = results.reset_index(drop=True).sort_values(select, ascending = False) 
        
        return results
   