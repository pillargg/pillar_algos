########
# This script finds the number of words/emojis/both depending on `goal` variable,
# isolates to each `min_` timestamp, and sorts the resulting df by largest number
########
import pandas as pd
from helpers import data_handler as d


def thalamus(big_df, min_, goal='num_words'):
    '''
    Calculates num_words/emoji/both then runs through functions to 
    split big_df, format for saving, and save as json
    
    input
    -----
    big_df: pd.DataFrame
        twitch stream chat dataframe
    min_: int
        number of minutes each chunk should be
    goal: str
        one of `num_words`, `num_emo`, or `num_words_emo`
    '''
    big_df = algorithm(big_df)
    chunk_df, first_stamp = chunker(big_df, min_)
    
    results = results_formatter(chunk_df, goal=goal)
    return results, first_stamp
    
def algorithm(big_df):
    # find number of words+emojis
    big_df = num_words_in_chat(big_df)
    # find number of emojis
    big_df['num_emo'] = big_df['emoticons'].apply(lambda x: len(x) if type(x) == list else 0)
    # find number of words only
    big_df['num_words'] = big_df['num_words_emo'] - big_df['num_emo']
    
    return big_df
    
def chunker(big_df, min_):
    '''
    Runs big_df through classes and functions to split it into hours/chunks
    
    output
    ------
    chunk_df: pd.DataFrame
        Dataframe with each hour/chunk labeled
    first_stamp: datetime
        The very first timestamp in the dataframe
    '''
    # split into hours
    dfs = d.dfSplitter(big_df)
    dfs.find_rest()

    hour_list = dfs.result
    first_stamp = hour_list[0]
    del hour_list[0]
    
    big_unique = big_df['_id'].unique()
    
    # split into minutes
    chunk_list = []
    for i in range(len(hour_list)):
        hour = hour_list[i]
        xmc = d.xminChats(hour, big_unique, min_=min_)
        xmc.find_rest()
        for chunk_num in range(len(xmc.result)):
            chunk = xmc.result[chunk_num]
            chunk['hour'] = i
            chunk['chunk'] = chunk_num
            chunk_list.append(chunk)
            
    chunk_list_expanded = []

    for chunk in chunk_list:
        chunk_list_expanded.append(num_words_in_chat(chunk))

    chunk_df = pd.DataFrame(columns = ['created_at', 'updated_at', 'display_name', '_id', 'name', 'type',
           'bio', 'logo', 'body', 'is_action', 'user_badges', 'emoticons', 'hour',
           'chunk', 'num_words_emo', 'num_emo', 'num_words'])

    for chunk in chunk_list_expanded:
        chunk_df = chunk_df.append(chunk)

    chunk_df = chunk_df.astype({
                                'is_action':bool,
                                'hour':int,
                                'chunk':int,
                                'num_words_emo':float,
                                'num_emo':float,
                                'num_words':float
                             })
    return chunk_df, first_stamp

def results_formatter(dataframe, goal):
    '''
    Creates a new df `results` that contains the total number of words in the dataframe, the time
    the time the dataframe started and ended
    input
    -----
    dataframe: pd.DataFrame
        Dataframe with all the hours and chunks labeled, and num_words calculated
    goal: str
        Col name that has calculated results (ex: num_words, chat_rate, etc.)
    output
    ------
    results: pd.DataFrame
        Dataframe with `hour`, `chunk`, `start`, `end`, `num_words` columns
    '''
    hour_list = []
    chunk_list = []
    time_start_list = []
    time_end_list = []
    goal_list = []
    
    dataframe = dataframe.sort_values('created_at')
    # label each chunk with unique ID
    dataframe['category'] = dataframe['hour'].astype(str) + dataframe['chunk'].astype(str)
    
    for cat in dataframe['category'].unique():
        temp_df = dataframe[dataframe['category'] == cat] 
        hour_list.append(temp_df.iloc[0, -3])  # assumes hour col is 3 from end
        chunk_list.append(temp_df.iloc[0, -2])  # assumes hunk col is 2 from end
        time_start_list.append(temp_df.iloc[0, 0])  # assume created_at col is first
        time_end_list.append(temp_df.iloc[-1, 0])  # assume created_at col is first
        goal_list.append(temp_df[goal].sum())

    results = pd.DataFrame({
        'hour':hour_list,
        'chunk':chunk_list,
        'start':time_start_list,
        'end':time_end_list,
        goal:goal_list
    })
    return results

def num_words_in_chat(dataframe):
    '''
    Creates a new col `num_words_emo` that contains the number of words in each message
    '''
    word_bag = []
    body_split = dataframe['body'].str.split(' ')  # split each string at the whitespace
    for row in body_split:
        num_words = len(row)
        word_bag.append(num_words)
    
    dataframe['num_words_emo'] = word_bag
    return dataframe

def run(data, min_, goal):
    data = pd.DataFrame.from_records(data)
    big_df = d.organize_twitch_chat(data) # fetch appropriate data
    results, first_stamp = thalamus(big_df, min_, goal=goal) 
    
    json_results = d.results_jsonified(results,first_stamp, goal)
    d.save_json(json_results, f"algo3.5_{goal}")
    
    return json_results