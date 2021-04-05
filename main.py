"""
This is used to call the different algorithms. This mocks the method that clipmaker will be calling
each of the algorithms.
"""
from algo1 import run as algo1Runner
import json

data = json.load(open('sample_data.json'))

# function that extracts vid_id from request goes here
vid_id = 955629991

print(algo1Runner(data, vid_id))