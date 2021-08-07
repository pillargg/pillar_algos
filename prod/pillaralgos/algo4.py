"""
Contains one class `sentimentRanker()` that returns a json of timestamps ranked by
a user chosen metric. Sentiment score is compouted using nltk.sentiment.vader.SentimentIntensityAnalyzer()

HOW TO:
    sr = sentimentRanker(data, sort_by='abs_overall', limit=10, chunk_length=2, save_json=False)
    results = sr.run()
"""
import pandas as pd
from .helpers import data_handler as dh


class sentimentRanker():
    def __init__(self, data, sort_by='abs_overall', limit=10, chunk_length=2, save_json=False):
        """
        Gets data ready for sentiment analysis. Initializes dicts, lists, etc.

        input
        -----
        data: list
            List of dictionaries, a json file opened with json.load(open(file))
        sort_by: str
            Options:
                "positive" - strength of positive sentiment
                "negative" - strength of negative sentiment
                "neutral" - strength of neutral sentiment
                "compound" - overall sentiment where > 0.05 is positive, < -0.05 is negative, in between is neutral
                "abs_overall" - sort by the absolute value of "compound", resulting in a mixture of positive and negative (but not neutral) chat timescripts
            Return timestamps with the highest `sort_by` value
        limit: int, None
            int: Return only the top X timestamps (using df.head(X))
            None: Return all timestamps
        
        chunk_length: int
            How long timestamps returned should be, in minutes.
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
        import numpy as np
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
        chunk_data = pd.DataFrame()

        for chunk in self.chunks_list:
            start = chunk.sort_values('created_at').iloc[0,0]
            end = chunk.sort_values('created_at').iloc[-1,0]
            messages = ''
            chunk_results = pd.DataFrame()
            for idx, row in chunk.iterrows():
                messages += f" {row['body']}"
                cell = row['body']
                res = self.sent_analysis(cell, expand=True)
                chunk_results = chunk_results.append(res)
                
            means_dict = chunk_results.mean().to_dict()
            chunk_means = pd.DataFrame(means_dict,index=[chunk_results.index.values[-1]])
            chunk_means['start'] = start
            chunk_means['end'] = end
            chunk_means['messages'] = messages
            chunk_means['overall'] = chunk_means['compound'].apply(self.cat_compound)
            chunk_means['abs_overall'] = abs(chunk_means['compound'])
            chunk_data = chunk_data.append(chunk_means)

        result = self.finalizer(chunk_data)
        return result
        
    def finalizer(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        
        dataframe['vid_id'] = self.vid_id
        return dataframe
        
    def sent_analysis(self, cell: str, expand = True) -> pd.DataFrame:
        '''
        Gives sentiment scores to strings
        '''
        from nltk.sentiment import SentimentIntensityAnalyzer
        sia = SentimentIntensityAnalyzer()
        result = sia.polarity_scores(cell)

        if expand:
            result = pd.DataFrame.from_dict(result,orient='index').T
            result['body'] = cell

        return result
    
    def cat_compound(self, score:float) -> str:
        '''
        Helper function that categorizes each compound score as neg,pos,neutral

        Compound score represents the overall sentiment of a sentence
        '''
        # decide sentiment as positive, negative and neutral
        if score >= 0.05:
            return "Positive"

        elif score <= - 0.05:
            return "Negative"

        else:
            return "Neutral"