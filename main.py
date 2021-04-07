"""
This is used to call the different algorithms. This mocks the method that clipmaker will be calling
each of the algorithms.

input
-----
data: list
sort_by: str
    'rel': "number of chatters at timestamp"/"number of chatters at that hour"
    'abs': "number of chatters at timestamp"/"total number of chatters in stream"
min_: int
    Approximate number of minutes each clip should be
    
output
------
Print of algo1_results.json file
"""
from algo1 import run as algo1Runner
import json

data = json.load(open('sample_data.json'))

print(
    algo1Runner(data, sort_by='rel', min_=2)
)