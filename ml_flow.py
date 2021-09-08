'''
Uses metaflow to run datasets through the appropriate machine learning
algorithm.

HOW TO: CONDA_CHANNELS=conda-forge python ml_flow.py --environment=conda run --data_=datasets/1073841789.pkl --vid_id=1073841789
'''

from metaflow import FlowSpec, Parameter, IncludeFile, step, conda_base
from io import BytesIO


@conda_base(
    libraries={"pandas": "1.2.3"},
    python="3.8.8",
)
class mlFlow(FlowSpec):
    data_ = IncludeFile(
        "data_", 
        help="Labeled and processed twitch stream chat log, pickle file",
        is_text=False
    )
    vid_id = Parameter(
        "vid_id", 
        help="ID of stream video",
        default="1073841789"
    )
    select_features = Parameter(
        "select_features",
        default="all",
        help="either 'all' or a list of columns to provide ML algorithm"
    )

    @step
    def start(self):
        '''
        Loads user provided parameters
        '''
        import pandas as pd
        self.data = pd.read_pickle(BytesIO(self.data_))
        
        self.next(self.me)
    @step
    def me(self):
        print('step 1')
        self.next(self.end)
        
    @step
    def end(self):
        print(self.data.head())
        print('reached the end')



if __name__ == "__main__":
    mlFlow()
