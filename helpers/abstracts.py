'''
Abstract classes to standardize code
'''

from abc import ABC, abstractmethod

class abstractAlgos(ABC):
    @abstractmethod
    def __init__(self):
        '''
        Use to import organzied data, assign to class variables
        '''
        ...
    @abstractmethod
    def run(self):
        '''
        Required of all algos to run
        '''
        ...
    @abstractmethod
    def clean_dataframe(self):
        '''
        Required to standardize algo output. Must include start/end columns,
        with only 1 clip range per row
        '''
        ...
