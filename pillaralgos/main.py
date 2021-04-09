"""
This is used to call the different algorithms. This mocks the method that clipmaker will be calling
each of the algorithms.

input
-----
save_json: bool
    True if want to save results as json to exports folder
data: list
min_: int
    Approximate number of minutes each clip should be
sort_by: str
    For algo1 ONLY
    'rel': "number of chatters at timestamp"/"number of chatters at that hour"
    'abs': "number of chatters at timestamp"/"total number of chatters in stream"
goal: str
    For algo3_5 ONLY
    'num_words': sum of the number of words in each chat message
    'num_emo': sum of the number of emoticons in each chat message
    'num_words_emo': sum of the number of words + emoticons in each chat message
min_words:int
    For algo3_0 ONLY
    When filtering chunks to top users, at least how many words the top user should send
    
output
------
Print of algo1_results.json file
"""
from algo1 import run as algo1Runner # unique rate per timestamp
from algo2 import run as algo2Runner # chat send per user rate
from algo3_5 import run as algo3_5Runner # number of words/emojis/both in each message, summed per stamp
from algo3_0 import run as algo3_0Runner # stamps where the top active users participated
import json

data = json.load(open('data/sample_data.json'))

print(
    #algo1Runner(data, sort_by='rel', min_=2, save_json = False),
    #algo2Runner(data, min_=2, save_json = False)
    #algo3_5Runner(data,goal='num_words',min_=2, save_json = False)
    algo3_0Runner(data,min_=2, min_words=5, save_json = False)
)
