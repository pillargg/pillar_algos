"""
Contains one class `emoticonExtractor` that returns a df of top emoticons used,
including the video's ID, and the emoticon's id, name, number of uses. Plus a blank
"label" column to be filled out by little label-monkeys.

"Top emoticons used" is defined as `emoticon count in dataset` >= `mean emoticon count in dataset`

HOW TO:
    ee = emoticonExtractor(data, limit='mean')
    results = ee.run()
"""
import pandas as pd

class featureFinder():
    def __init__(self, data: list):
        """
        input
        -----

        """
        self.first_stamp = data[0]
        self.chunks_df = data[1]
        self.vid_id = data[2]

    def run(self) -> pd.DataFrame:

        chunk_df_with_emo_count = self.thalamus()
        results = self.clean_dataframe(chunk_df_with_emo_count)
        return results

    def thalamus(self) -> pd.DataFrame:
        """
        Coordinates all functions to return a dataset of top emojis used
        """
        import pandas as pd

        big_emo = 0 # to count total emoticons per stream

        # get count of total emoticon per chunk and number of users per chunk
        new_chunk_data = pd.DataFrame()
        for start in self.chunks_df['start'].unique():
            chunk = self.chunks_df[self.chunks_df['start'] == start]
            num_user = len(chunk["_id"].unique())

            chunk_emo = 0
            chunk_formatted = self.format_df_for_emo(chunk)

            if chunk_formatted.empty:
                # if returned dataframe is empty, no emojis
                chunk_emo += 0
            else:
                for idx, row in chunk_formatted.iterrows():
                    num_emo = self.emo_counter(row)
                    chunk_emo += num_emo

            big_emo += chunk_emo # add number of emoticons in chunk to total
            chunk['num_emoji'] = chunk_emo
            chunk['num_user'] = num_user
            new_chunk_data = new_chunk_data.append(chunk)

        new_chunk_data["perc_emoji_of_stream"] = new_chunk_data["num_emoji"] / big_emo
        new_chunk_data["emoji_user_ratio"] = (
            new_chunk_data["num_emoji"] / new_chunk_data["num_user"]
        )

        return new_chunk_data

    ### ACTUAL FUNCTIONS ###

    def format_df_for_emo(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Extracts emojis to make them accessible to counter
        """
        # check whether dataframe has any emoticons
        if 'emoticons' not in dataframe.columns:
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
        '''
        Groups dataframe by start/end and then means each column to only include 1 stat per chunk
        '''
        dataframe = dataframe.groupby(['start','end']).mean().reset_index()
        dataframe = dataframe[['start','end','num_emoji','num_user','perc_emoji_of_stream','emoji_user_ratio']]
        return dataframe