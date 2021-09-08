'''
Uses metaflow to run datasets through the appropriate machine learning
algorithm.

HOW TO: CONDA_CHANNELS=conda-forge python ml_flow.py --environment=conda run 
'''

from metaflow import FlowSpec, Parameter, IncludeFile, step, conda_base, batch
from helpers import exceptions as e
from io import BytesIO


@conda_base(
    libraries={"pandas": "1.2.3"},
    python="3.8.8",
)
class mlFlow(FlowSpec):
    data_loc = Parameter(
        "data_loc", 
        help="Location of labeled and processed twitch stream chat log, pickle file",
        default='output'
    )

    select_features = Parameter(
        "select_features",
        default="all",
        help="either 'all' or a list of columns to provide ML algorithm"
    )

    @step
    def start(self):
        '''
        Merges all datasets
        Loads user provided parameters
        '''
        import pandas as pd
        import os
        pickles = [self.data_loc + '/' + file for file in os.listdir(self.data_loc) if '.pkl' in file]
        if len(pickles) == 0:
            raise e.EmptyFolder(self.data_loc, '.pkl')

        data = pd.DataFrame()

        for file in pickles:
            pkl = pd.read_pickle(file)
            data = data.append(pkl)
        self.data = data.reset_index(drop=True)
        self.next(self.train)

    @step
    def train(self):
        print('step 1')
        self.next(self.validate)

    @step
    def validate(self):
        print('step 2')
        self.next(self.test)

    @step
    def test(self):
        print('step 2')
        self.next(self.end)

    @step
    def end(self):
        print(self.data.head())
        print('reached the end')


if __name__ == "__main__":
    mlFlow()
