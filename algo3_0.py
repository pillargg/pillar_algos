########
# This script finds the number of words/emojis/both depending on `goal` variable,
# isolates to each `min_` timestamp, and sorts the resulting df by largest number
########
import pandas as pd
from helpers import data_handler as dh

def thalamus(big_df, min_, goal, min_words):
    
    id_words = id_words_counter(big_df)
    first_stamp, chunk_list = dh.get_chunks(big_df)
    top_chunks = new_chunk_list(id_words, chunk_list, min_words = 5)
    results = results_formatter(top_chunks, goal='num_top_user_appears')
    
    return results, first_stamp
    
def results_formatter(list_chunk, goal):
    '''
    Creates a new df `results` that contains the total number of words in the dataframe, the time
    the time the dataframe started and ended
    input
    -----
    list_chunk: list
        List of pd.DataFrame
    goal: str
        Col name that has calculated results (ex: num_words, chat_rate, etc.)
    output
    ------
    results: pd.DataFrame
        Dataframe with `start`, `end`, `num_words` columns
    '''
    chunk_list = []
    time_start_list = []
    time_end_list = []
    goal_list = []
    
    for chunk in list_chunk:
        time_start_list.append(chunk.iloc[0, 0])  # assume created_at col is first
        time_end_list.append(chunk.iloc[-1, 0])  # assume created_at col is first
        goal_list.append(chunk[goal].sum())

    results = pd.DataFrame({
        'start':time_start_list,
        'end':time_end_list,
        goal:goal_list
    })
    results = results.sort_values(goal, ascending=False).drop_duplicates()
    return results
    
def new_chunk_list(id_words, chunk_list, min_words):
    '''
    Creates a new list of chunks, containing only chunks where top
    users sent more than `min_words` words
    '''
    user_dict = {} # store chunks of the top 10 users
    for user in id_words.head(10)['_id']:
        user_dict[user] = []
    for user in user_dict.keys():
        for chunk in chunk_list:
            chunk['_id'] = chunk['_id'].astype(int)
            if sum(chunk['_id'] == user) > min_words:
                user_dict[user].append(chunk)
    top_chunks = []
    for user, value in user_dict.items():
        if len(value) > 0:
            for chunk in value:
                chunk['num_top_user_appears'] = chunk['_id']==user
                top_chunks.append(chunk)
    return top_chunks

def id_words_counter(big_df):
    '''
    Returns a dataframe with all user IDs and the number of words/emojis/combined
    they each sent, sorted by top senders
    '''
    id_words = pd.DataFrame(columns = ['display_name','_id','num_words', 'num_emoji'])
    
    for _id in big_df['_id'].unique():
        temp_df = big_df[big_df['_id'] == _id]
        words = temp_df['body'].str.split(' ')
        emoji = temp_df['emoticons'].apply(lambda x: 0 if type(x) == float else len(x))
        num_emoji = emoji.sum()
        num_words = words.apply(lambda x: len(x))

        sum_words = num_words.sum()
        id_words = id_words.append({
            'display_name':temp_df['display_name'].iloc[0],
            '_id':_id,
            'num_words':sum_words,
            'num_emoji':num_emoji
        }, ignore_index=True)
    id_words = id_words.astype({'_id':int,'num_words':int,'num_emoji':int})
    id_words['only_words'] = id_words['num_words'] - id_words['num_emoji']
    id_words = id_words.sort_values('only_words',ascending=False).reset_index(drop=True).reset_index()
    id_words = id_words.rename({'index':'rank'},axis=1)
    # Weight = "num words / num words of biggest spammer"
    id_words['weight'] = id_words['only_words'] / id_words['only_words'].max()
    
    return id_words
    
def run(data, min_, min_words):
    data = pd.DataFrame.from_records(data)
    big_df = dh.organize_twitch_chat(data) # fetch appropriate data
    results, first_stamp = thalamus(big_df, min_, min_words = 5, goal='num_top_user_appears') 
    
    json_results = dh.results_jsonified(results, first_stamp, results_col='num_top_user_appears')
    dh.save_json(json_results, f"algo3.0_top_user_appears")
    
    return json_results