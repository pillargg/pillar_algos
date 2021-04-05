import pandas as pd
import numpy as np

import datetime as dt
import json

def organize_twitch_chat(json_name):
    data = pd.read_json(json_name, orient='records')
    df = data[['created_at','updated_at','commenter','message']]
    messages = df['message'].apply(pd.Series).drop(['fragments','user_color','user_notice_params'],axis=1)
    users = df['commenter'].apply(pd.Series)
    
    df = df.drop(['message','commenter'], axis=1) # duplicate info
    df = pd.concat([df,users,messages],axis=1)
    df = df.iloc[:,[0,1,2,3,4,5,6,9,10,11,12,13]] # select cols that arent duplicates
    
    return df

class dfSplitter():
    def __init__(self, dataframe):
        '''
        Splits dataframe into multiple dataframes, each 1 hour long

        output:
        ------
        my_list: list
            List of dataframes
        '''
        # init function finds the first split
        dataframe = dataframe.sort_values("created_at")
        first = dataframe[dataframe['created_at'] <= dataframe.loc[0,'created_at'] + pd.Timedelta(hours = 1)]
        self.last_i = first.index.max()
        self.dataframe = dataframe
        self.result = [] # list to append starting timestamp + datasets to
        self.result.append(dataframe.iloc[0, 0]) # NOTE: assumes first col is always "created_at" col
        self.result.append(first)
        
    def find_rest(self):
        '''
        Uses last index of first split to find the others
        '''
        dataframe = self.dataframe
        last_i = self.last_i
        if last_i+1 != len(dataframe):
            new_df = dataframe.loc[last_i+1:,:] # clip df to start at last_i
            newest = new_df[new_df['created_at'] <= new_df.loc[last_i+1,'created_at'] + pd.Timedelta(hours=1)] # filter by hour
            self.result.append(newest) # store in list
            self.last_i = newest.index.max()
            
            self.find_rest() # repeat
        else:
            return dataframe # never actually used
        
class fminChats():
    def __init__(self,dataframe, big_unique, min_= 2):
        '''
        Finds the percent unique chatters that chatted every min_ minutes
        
        input
        -----
        dataframe: pd.DataFrame
            Twitch chat dataframe organized and split by dfSplitter
        big_unique: int
            Total number of unique chatters for the entire Twitch stream
        min_: int
            Minute range to find timestamps for. Ex: Find 2 min long timestamps.
        '''
        
        # init function finds the first split
        dataframe = dataframe.sort_values("created_at")
        first = dataframe[dataframe['created_at'] <= dataframe.iloc[0,0] + pd.Timedelta(minutes = min_)]
        
        self.min_ = min_
        self.total_uniques = len(dataframe['_id'].unique())
        self.big_unique = big_unique
        
        self.last_i = first.index.max()
        self.dataframe = dataframe
        
        self.result = []
        self.result.append(first)
        
    def find_rest(self):
        '''
        Uses last index of first split to find the others
        '''
        dataframe = self.dataframe
        last_i = self.last_i
        if last_i+1 < dataframe.index.max(): # NOT len(dataframe), that bugs out and i dont wanna explain why
            new_df = dataframe.loc[last_i+1:,:] # clip df to start new min_ min calc at last_i+1
            newest = new_df[new_df['created_at'] <= new_df.loc[last_i+1,'created_at'] + pd.Timedelta(value=self.min_, unit='minutes')] # filter by minute
            self.result.append(newest) # store in list
            
            self.last_i = newest.index.max()
            self.find_rest() # repeat
        else:
            x=''
    
    def perc_uniques(self, chunk_list):
        '''
        Finds the percent unique chatters for eachd dataframe in the list. Dataframes assumed to be split using self.find_rest.
        '''
        
        perc_unique = {
                f'{self.min_}min_chunk':[],
                'start':[],
                'end':[],
                'num_unique':[],
                'perc_rel_unique':[],
                'perc_abs_unique':[]
        }
        
        
        for i in range(len(chunk_list)):
            # calcuate
            chunk = i
            unique = len(chunk_list[i]['_id'].unique())
            timestamp = [chunk_list[i]['created_at'].min(), chunk_list[i]['created_at'].max()]
            perc_rel = unique/self.total_uniques # this is the total uniques in THAT DATAFRAME, ie the hourly cut
            perc_abs = unique/self.big_unique # this is the total uniques in the entire twitch session
            # store
            perc_unique[f'{self.min_}min_chunk'].append(chunk)
            perc_unique['start'].append(timestamp[0])
            perc_unique['end'].append(timestamp[1])
            perc_unique['num_unique'].append(unique)
            perc_unique['perc_rel_unique'].append(perc_rel)
            perc_unique['perc_abs_unique'].append(perc_abs)
            
        df_unique = pd.DataFrame(perc_unique)
        df_unique['elapsed'] = df_unique['end'] - df_unique['start']
        return df_unique
    
def results_jsonified(results, vid_id, first_sec):
    '''
    Extracts relevant results and makes them machine readable
    
    input
    -----
    results: pd.DataFrame
        DataFrame with at least start, end columns.
    vid_id: int
        Twitch id of video
    '''
    results['first_sec'] = first_sec # to calculate elapsed time from first sec, in seconds
    results = results.sort_values('perc_rel_unique', ascending=False) # so json format is returned with top result being the most relevant
    json_results = []
    for i, row in results.iterrows():
        og = row['first_sec']
        start = row['start']
        end = row['end']
        
        start_sec = dt.timedelta.total_seconds(start-og) # find difference between first sec and given timestamp, convert that to seconds
        end_sec = dt.timedelta.total_seconds(end-og)
        
        dict_ = {"startTime":start_sec,
                 "endTime":end_sec,
                 "videoId":vid_id}
        json_results.append(dict_)
        
    return json_results
        
def hour_iterator(big_df, vid_id, min_=2):
    '''
    Pushes all dfs in a list through the fminChats function, returns a dataframe of results
    
    input
    -----
    big_df: pd.DataFrame
        Df of the entire twitch session. This is the one that was split by dfSplitter class
    min_: int
        How long a timestamp range should be
    vid_id: int
        Twitch id of video. Needed for jsonify function
    '''
    ds = dfSplitter(big_df) # initiate
    ds.find_rest() # split big_df into 1 hour long separate dfs
    hour_list = ds.result # result stored in class var. NOTE: index 0 is always the very first timestamp of big_df
    first_sec = hour_list[0]
    hour_list = hour_list[1:]

    # initiate empty results df
    results = pd.DataFrame(columns=['hour', f'{min_}min_chunk', 'start', 'end', 'num_unique', 'perc_rel_unique', 'perc_abs_unique'])
    max_uniques = len(big_df['_id'].unique()) # the total number of unique chatters for the entire twitch session

    # iterate all sections through the class
    for i in range(len(hour_list)):
        fm = fminChats(hour_list[i], max_uniques)
        _n = fm.find_rest() # _n not needed
        chunk_list = fm.result # get back list of dfs, each 2 minutes long

        hr_uniques = fm.perc_uniques(chunk_list)
        hr_uniques['hour'] = i + 1
        results = results.append(hr_uniques)

    results['elapsed'] = results['end'] - results['start'] # to double check length
    pretty_results = results.reset_index(drop=True) # prettify
    
    json_results = results_jsonified(results, vid_id, first_sec) # ordered by top perc_rel_unique
    
    return pretty_results, json_results

def save_json(json_results, name):
    '''
    Saves json_results in txt file.
    '''
    str_  = '['
    for dict_ in json_results:
        str_ += str(dict_) + ', \n '
    str_ += ']'
    
    with open(f"{name}.txt",'w') as f:
        f.write(str_)

big_df = organize_twitch_chat("big_data.json") # fetch appropriate data
results, json_results = hour_iterator(big_df, vid_id=955629991)
save_json(json_results, "algo1_results")