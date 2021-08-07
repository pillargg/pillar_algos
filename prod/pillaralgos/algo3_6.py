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
from .helpers import data_handler as dh


class emoticonExtractor:
    def __init__(
        self, data, sort_by="perc_then_ratio", limit=10, chunk_length=2, save_json=False
    ):
        """
        Gets data ready for emo extraction. Initializes dicts, lists, etc.

        input
        -----
        data: list
            List of dictionaries, a json file opened with json.load(open(file))
        sort_by: str
            Options:
                "perc_emoji_of_stream" - percent of emoticons from stream sent at timestamp
                "emoji_user_ratio" - number of unique users participating compared to number of emoticons sent
                "perc_then_ratio" - first sort with "perc_emoji_of_stream", then by "emoji_user_ratio"
                "ratio_then_perc" - first sort with "emoji_user_ratio", then by "perc_emoji_of_stream"

            Return timestamps with the highest `sort_by` value
        limit: int, None
            int: Return only the top X timestamps (using df.head(X))
            None: Return all timestamps
        """
        self.big_df = dh.organize_twitch_chat(data)  # organize
        self.first_stamp, self.chunks_list = dh.get_chunks(
            self.big_df, min_=chunk_length
        )  # first timestamp + list of X min chunks
        self.vid_id = data[0]["content_id"]

        self.sort_by = sort_by
        self.limit = limit
        self.save_json = save_json

    def run(self):
        if type(self.big_df) == pd.DataFrame:
            results = self.thalamus()
            self.results = results
            # results_jsonified sorts by top calc
            json_results = dh.results_jsonified(results, self.first_stamp, self.sort_by)
            if type(self.limit) == int:
                # grab only the top X most used
                json_results = json_results[: self.limit]

            if self.save_json:
                dh.save_json(json_results, f"algo3.6_{self.sort_by}")

            return json_results
        else:
            return np.array([])  # this is an empty numpy array if it is not a DF.

    def thalamus(self):
        """
        Coordinates all functions to return a dataset of top emojis used
        """
        import pandas as pd

        self.pd = pd

        big_emo = 0
        big_df_formatted = self.format_df_for_emo(self.big_df)
        # get a count total number of emojis in stream
        for idx, row in big_df_formatted.iterrows():
            num_emo = self.emo_counter(row)
            big_emo += num_emo

        # get count of total emoticon per chunk and number of users per chunk
        chunk_data = pd.DataFrame(
            columns=[
                "start",
                "end",
                "num_emoji",
            ]
        )
        for chunk in self.chunks_list:
            time_range = (chunk.iloc[0, 0], chunk.iloc[-1, 0])
            start = time_range[0]  # very first timestamp of chunk
            end = time_range[1]  # very last timestamp of chunk
            num_user = self.user_counter(chunk)

            chunk_emo = 0
            chunk_formatted = self.format_df_for_emo(chunk)
            try:
                if chunk_formatted.empty:
                    chunk_emo += 0
                else:
                    for idx, row in chunk_formatted.iterrows():
                        num_emo = self.emo_counter(row)
                        chunk_emo += num_emo
            except AttributeError as a:
                chunk_emo += 0

            chunk_data = chunk_data.append(
                {
                    "start": start,
                    "end": end,
                    "num_emoji": chunk_emo,
                    "num_user": num_user,
                },
                ignore_index=True,
            )
        chunk_data["perc_emoji_of_stream"] = chunk_data["num_emoji"] / big_emo
        chunk_data["emoji_user_ratio"] = (
            chunk_data["num_emoji"] / chunk_data["num_user"]
        )

        result = self.finalize(chunk_data)
        return result

    ### ACTUAL FUNCTIONS ###

    def format_df_for_emo(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Extracts emojis to make them accessible to counter
        """
        import pandas as pd

        # check whether dataframe has any emoticons
        body_has_emo = dataframe[~dataframe["emoticons"].isna()].reset_index(drop=True)
        if len(body_has_emo.index) == 0:
            return None

        # emoticons col contains _id, begin, end. Here we extract just the _id and
        # put it into a list
        body_has_emo["emo_id_list"] = body_has_emo["emoticons"].apply(
            lambda my_list: self.emo_extractor(my_list)
        )

        emo_data = body_has_emo[["emo_id_list", "body"]]

        return emo_data

    def finalize(self, dataframe: pd.DataFrame) -> list:
        """
        Sorts dataframe by given class parameter and jsonifies the result
        """
        if self.sort_by in ["perc_emoji_of_stream", "emoji_user_ratio"]:
            self.sort_by = self.sort_by
        elif self.sort_by == "perc_then_ratio":
            self.sort_by = ["perc_emoji_of_stream", "emoji_user_ratio"]
        elif self.sort_by == "ratio_then_perc":
            self.sort_by = ["emoji_user_ratio", "perc_emoji_of_stream"]
        else:
            self.sort_by = ["perc_emoji_of_stream", "emoji_user_ratio"]
            print("Invalid sort_by value, sorting by default value")

        dataframe["vid_id"] = self.vid_id
        return dataframe

    ### HELPER FUNCTIONS ###
    def emo_extractor(self, my_list):
        """
        Helper function to grab emoticon id
        """
        return [emo_dict["_id"] for emo_dict in my_list]

    def loc_extractor(self, my_list):
        """
        Helper function to grab index location of emoticon in the body
        """
        return [[emo_dict["begin"], emo_dict["end"]] for emo_dict in my_list]

    def user_counter(self, dataframe):
        """
        Counts the number of unique users in the dataframe
        """
        return len(dataframe["_id"].unique())

    def emo_counter(self, row):
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
