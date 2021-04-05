"""
This is used to call the different algorithms. This mocks the method that clipmaker will be calling
each of the algorithms.
"""
from algo1 import run as algo1Runner
import json

data = json.load(open('sample_data.json'))


print(algo1Runner(data))