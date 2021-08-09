"""
This script finds the top 10 active users, timestamps where they participated,
filtered by at least `min_words` number of words sent by the user per stamp

HOW TO
    algo3_0.run(data, min_=2, limit=10, min_words=5, save_json = False)
"""
import pandas as pd
from .helpers import data_handler as dh

class featureFinder():
    def __init__(self, data: list, limit: int, min_words: int, sort_by: str):
        """
        Runs algo3_0 to extract only those chunks where the top 10 users participated.
        - Top users are defined as "sent the most words in the entire twitch stream".
        - Once top users are identified, only those chunks are returned where top users
            sent at least `min_words` number of words.

        input
        ------
        data: list
            List of dictionaries of data from Twitch chat
        limit: int or None
            Number of rows/dictionaries/timestamps to return
        min_words:int or None
            When filtering chunks to top users, at least how many words the top user should send
        sort_by: str
            Outcome variable of interest. One of 'num_words_emoji', 'num_emoji', 'only_words','weight'
            'weight' represents the percent of 'only_words' an individual wrote compared to the top individual

        output
        ------
        json_results: list
            List of dictionaries in json format, ordered from predicted best to worst candidates.
                Ex: [{start:TIMESTAMP_INT, end:TIMESTAMP_INT}]
        """
        self.big_df = data[0]
        self.first_stamp = data[1]
        self.chunk_list = data[2]
        self.vid_id = data[3]
        
        self.limit = limit
        self.min_words = min_words
        self.sort_by = 'num_top_user_appears'

    def run(self):
        '''
        Coordinates the other functions in this algo and data_helper. Separate from 
        `run()` for sanity purposes.
        '''
        id_words = self.id_words_counter(self.big_df)
        chunks = self.new_chunk_list(id_words, self.chunk_list)
        time_results = self.results_formatter(chunks)
        results = self.finalizer(time_results) # sorted by top sort_by

        return results

    def id_words_counter(self, big_df):
        """
        Returns a dataframe with all user IDs and the number of words/emojis/combined
        they each sent, sorted by top senders
        """
        id_words = pd.DataFrame(columns=["_id", "num_words_emoji", "num_emoji"])

        for _id in big_df["_id"].unique():
            temp_df = big_df[big_df["_id"] == _id]
            words = temp_df["body"].str.split(" ")
            if 'emoticons' in temp_df.columns:
                emoji = temp_df["emoticons"].apply(lambda x: 0 if type(x) == float else len(x))
                num_emoji = emoji.sum()
            else:
                num_emoji = 0.0
            num_words = words.apply(lambda x: len(x))

            sum_words = num_words.sum()
            id_words = id_words.append(
                {"_id": _id, "num_words_emoji": sum_words, "num_emoji": num_emoji},
                ignore_index=True,
            )
        id_words = id_words.astype({"_id": int, "num_words_emoji": int, "num_emoji": int})
        id_words["only_words"] = id_words["num_words_emoji"] - id_words["num_emoji"]
        id_words = (
            id_words.sort_values("only_words", ascending=False)
            .reset_index(drop=True)
            .reset_index()
        )
        id_words = id_words.rename({"index": "rank"}, axis=1)
        # Weight = "num words / num words of biggest spammer"
        id_words["weight"] = id_words["only_words"] / id_words["only_words"].max()

        return id_words
    
    def new_chunk_list(self, id_words, chunk_list):
        """
        Creates a new list of chunks, containing only chunks where top
        users sent more than `min_words` words
        """
        user_dict = {}  # store chunks of the top 10 users
        for user in id_words.head(10)["_id"]:
            user_dict[user] = []
        for user in user_dict.keys():
            for chunk in chunk_list:
                chunk["_id"] = chunk["_id"].astype(int)
                if type(self.min_words) == int:
                    if sum(chunk["_id"] == user) > min_words:
                        user_dict[user].append(chunk)
                else:
                    user_dict[user].append(chunk)
        top_chunks = []
        for user, value in user_dict.items():
            for chunk in value:
                chunk["num_top_user_appears"] = chunk["_id"] == user
                top_chunks.append(chunk)
        return top_chunks

    def results_formatter(self, list_chunk):
        """
        Creates a new df `results` that contains the total number of words in the dataframe, the time
        the time the dataframe started and ended
        input
        -----
        list_chunk: list
            List of pd.DataFrame
        sort_by: str
            Col name that has calculated results (ex: num_words_emoji, chat_rate, etc.)
        output
        ------
        results: pd.DataFrame
            Dataframe with `start`, `end`, `num_words_emoji` columns
        """
        time_start_list = []
        time_end_list = []
        sort_by_list = []

        for chunk in list_chunk:
            self.test = chunk
            time_start_list.append(chunk.iloc[0, 0])  # assume created_at col is first
            time_end_list.append(chunk.iloc[-1, 0])  # assume created_at col is first
            sort_by_list.append(chunk[self.sort_by].sum())

        results = pd.DataFrame(
            {"start": time_start_list, "end": time_end_list, self.sort_by: sort_by_list}
        )
        results = results.sort_values(self.sort_by, ascending=False).drop_duplicates()
        return results

    def finalizer(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        '''
        Sorts and clips final dataframe as requested
        '''
        dataframe['vid_id'] = self.vid_id
        dataframe = dataframe.sort_values(self.sort_by, ascending=False)
        if type(self.limit) == int:
            dataframe = dataframe.head(self.limit)
            return dataframe
        else:
            return dataframe
