"""
This script calculates the mean sentiment score of each chunk 
using nltk.sentiment.vader.SentimentIntensityAnalyzer()

HOW TO:
    sr = sentimentRanker(data)
    results = sr.run()
"""
import pandas as pd


class featureFinder:
    def __init__(self, data: list):
        """
        Gets data ready for sentiment analysis. Initializes dicts, lists, etc.

        input
        -----
        data: list
            List of dictionaries, a json file opened with json.load(open(file))
        """
        self.first_stamp = data[0]
        self.chunk_df = data[1]
        self.vid_id = data[2]

    def run(self) -> pd.DataFrame:
        """
        Runs the functions of this algorithm

        output
        ------
        results: dataframe with feature columns that represent the mean sentiment value of
                 chats sent during each chunk:
                    "positive" - strength of positive sentiment
                    "negative" - strength of negative sentiment
                    "neutral" - strength of neutral sentiment
                    "compound" - overall sentiment where > 0.05 is positive,
                        < -0.05 is negative, in between is neutral
                    "abs_overall" - absolute value of "compound", resulting in a
                        mixture of positive and negative (but not neutral) chat timescripts
                    "mostly" - indicating whether the overall sentiment is mostly
                        positive, neutral, or negative. Calculated using self.cat_compound()
        """
        new_df = self.thalamus(self.chunk_df)
        results = self.clean_dataframe(new_df)
        return results

    def thalamus(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Coordinates getting sentiment values for chunks
        """

        sentiment_df = pd.DataFrame()

        for idx, row in dataframe.iterrows():
            res = self.sent_analysis(row["body"])
            row["positive"] = res["pos"]
            row["neutral"] = res["neu"]
            row["negative"] = res["neg"]
            row["compound"] = res["compound"]

            sentiment_df = sentiment_df.append(row)

        sentiment_df["abs_compound"] = abs(sentiment_df["compound"])
        return sentiment_df

    def sent_analysis(self, cell: str, expand=True) -> dict:
        """
        Gives sentiment scores to strings
        """
        from nltk.sentiment import SentimentIntensityAnalyzer

        sia = SentimentIntensityAnalyzer()
        result = sia.polarity_scores(cell)
        return result

    def cat_compound(self, score: float) -> str:
        """
        Helper function that categorizes each compound score as neg,pos,neutral

        Compound score represents the overall sentiment of a sentence
        """
        # decide sentiment as positive, negative and neutral
        if score >= 0.05:
            return "Positive"

        elif score <= -0.05:
            return "Negative"

        else:
            return "Neutral"

    def clean_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Groups dataframe by start/end and then means each column to only include 1 stat per chunk
        """
        dataframe = dataframe.groupby(["start", "end"]).mean().reset_index()
        dataframe = dataframe[
            [
                "start",
                "end",
                "positive",
                "neutral",
                "negative",
                "compound",
                "abs_compound",
            ]
        ]
        dataframe["mostly"] = dataframe["compound"].apply(self.cat_compound)
        return dataframe
