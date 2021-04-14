"""
Contains one class `emoticonExtractor` that returns a df of top emoticons used,
including the video's ID, and the emoticon's id, name, number of uses. Plus a blank
"label" column to be filled out by little label-monkeys.

"Top emoticons used" is defined as `emoticon count in dataset` >= `mean emoticon count in dataset`

HOW TO:
    ee = emoticonExtractor(data, limit='mean')
    vid_emos_df = ee.run()
"""
from pillaralgos.helpers import data_handler as dh

import pandas as pd
import json
from pillaralgos.helpers import data_handler as dh


class emoticonExtractor:
    def __init__(self, data, min_use="mean", limit=None):
        """
        Gets data ready for emo extraction. Initializes dicts, lists, etc.

        input
        -----
        data: list
            List of dictionaries, a json file opened with json.load(open(file))
        min_use: str, int, None
            'mean': Return only those emoticons who's count is > the mean occurrance
            int: Return only those emoticons who's count is > X. Use 0 to not filter.
        limit: int, None
            int: Return only the top X emoticons (using df.head(X))
            None: Return all emoticons
        """

        big_df = dh.organize_twitch_chat(data)
        print(big_df.iloc[-1, 0] - big_df.iloc[0, 0])
        self.vid_id = data[0]["content_id"]
        self.big_df = big_df
        self.all_emos = (
            []
        )  # all unique emo_ids, later used to pd.Series(self.all_emos).value_counts()
        self.limit = limit
        self.min_use = min_use

    def run(self):
        """
        Coordinates all functions to return a dataset of top emojis used
        """
        import pandas as pd

        body_has_emo = self.big_df[~self.big_df["emoticons"].isna()].reset_index(
            drop=True
        )

        body_has_emo["emo_id_list"] = body_has_emo["emoticons"].apply(
            lambda my_list: self.emo_extractor(my_list)
        )

        body_has_emo["emo_id_list"].apply(lambda my_list: self.emo_saver(my_list))
        body_has_emo["emo_loc"] = body_has_emo["emoticons"].apply(
            lambda my_list: self.loc_extractor(my_list)
        )

        emo_data = body_has_emo[["emo_id_list", "emo_loc", "body"]]
        self.emo_data = emo_data

        num_used = pd.Series(
            self.all_emos
        ).value_counts()  # count how many times each unique emo was used

        num_used = num_used.reset_index()  # turn series to df, rename cols
        num_used.columns = ["emoji_id", "occurrance"]

        emo_dict = self.emo_id_matcher(
            emo_data
        )  # create a dictionary of emo_id:emo_name
        num_used["emoji_name"] = num_used["emoji_id"].map(emo_dict)
        num_used["label"] = ""

        if type(self.min_use) == str:
            # grab everything greater than mean count
            top_emoticons = num_used[
                num_used["occurrance"] > num_used["occurrance"].mean()
            ]
        elif type(self.min_use) == int:
            # grab everything greater than X
            top_emoticons = num_used[num_used["occurrance"] > self.min_use]
        else:
            # otherwise return all results
            top_emoticons = num_used

        if type(self.limit) == int:
            # grab only the top X most used
            top_emoticons = top_emoticons.head(limit)
        else:
            # return all results
            top_emoticons = top_emoticons

        top_emoticons["vid_id"] = self.vid_id
        # reorganize columns
        top_emoticons = top_emoticons[
            ["vid_id", "emoji_id", "occurrance", "emoji_name", "label"]
        ]

        return top_emoticons

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

    def emo_saver(self, my_list):
        """
        Helper function to extract all emo_ids from the list and append to self.all_emos
        """
        for emo in my_list:
            self.all_emos.append(emo)

    def emo_id_matcher(self, emo_data):
        """
        Matches the emoticon id to it's twitch-defined emoticon text
        """
        emo_dict = {}
        for i, row in emo_data.iterrows():
            for x in range(len(row["emo_loc"])):
                loc = row["emo_loc"][x]  # grab location
                begin = loc[0]
                end = loc[1] + 1
                emoji_name = row["body"][begin:end]  # extract emoji text
                emoji_id = row["emo_id_list"][x]

                if emoji_id not in emo_dict.keys():
                    emo_dict[emoji_id] = emoji_name
        return emo_dict
