"""
This is used to call the different algorithms. This mocks the method that clipmaker will be calling
each of the algorithms.
"""
from algo1 import run as algo1Runner
import json

data = json.load(open('sample_data.json'))

sort_by = 'rel'  # "number of chatters at timestamp"/"number of chatters at that hour"
# sort_by = 'abs'  # "number of chatters at timestamp"/"total number of chatters in stream"
print(algo1Runner(data, sort_by=sort_by))