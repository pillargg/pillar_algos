# this file contains a series of classes and functions to help with loading and splitting twitch chat data
# also json_saver() that converts given variable into string, saves into .json file

import pandas as pd
import numpy as np

import datetime as dt
import json

def organize_twitch_chat(data):
    '''
    Turns json into dataframe. Expands lists of lists into own columns. Selects only relevant columns.
    
    input
    -----
    data: list
        list of dictionaries in json format, loaded with the `open` context manager.
        
    output
    ------
    df: pd.DataFrame
        Dataframe with the following columns: 
            ['created_at', 'updated_at', 'display_name', '_id', 'name', 'type',
             'bio', 'logo', 'body', 'is_action', 'user_badges', 'emoticons']
    '''
    data = pd.DataFrame.from_records(data) # convert to df
    # all vars were loaded as str. Change type to datetime/int/bool
    data['created_at'] = pd.to_datetime(data['created_at'])
    data['updated_at'] = pd.to_datetime(data['updated_at'])
    
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
        
class xminChats():
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
            
def results_jsonified(results, first_sec, results_col):
    '''
    Converts timestamps to seconds, extracts results and makes the whole thing machine readable
    
    input
    -----
    results: pd.DataFrame
        DataFrame with at least the start (datetime) and end (datetime) columns, and a column to sort by.
    first_sec: datetime
        The very first timestamp in the entire twitch chat log. Used to calculate elapsed time in seconds.        
    results_col: str
        Column to sort values by (ascending=False)
        
    output
    ------
    json_results: list
        List of dictionaries with startTime and endTime keys, sorted by best results at top
    '''
    results['first_sec'] = first_sec # to calculate elapsed time from first sec, in seconds
    results = results.sort_values(results_col, ascending=False) # so json format is returned with top result being the most relevant
    json_results = []
    for i, row in results.iterrows():
        og = row['first_sec']
        start = row['start']
        end = row['end']
        
        start_sec = dt.timedelta.total_seconds(start-og) # find difference between first sec and given timestamp, convert that to seconds
        end_sec = dt.timedelta.total_seconds(end-og)
        
        dict_ = {"startTime":start_sec,
                 "endTime":end_sec}
        json_results.append(dict_)
        
    return json_results

def save_json(json_results, name):
    '''
    Converts list of dict to pure str, then saves as a json file.
    
    input
    -----
    json_results: list
        List of dictionaries containing results
    name: str
        Filename to save as. Ex: name.json
    '''
    str_  = '['
    for dict_ in json_results:
        str_ += str(dict_) + ', \n '
    str_ += ']'
    
    with open(f"exports/{name}.json",'w') as f:
        f.write(str_)
    print(f"Saved to data/{name}.json")