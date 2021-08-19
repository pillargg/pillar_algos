'''
This script is responsible for running datasets through each algorithm, tying
the feature outputs into together into one dataset.

HOW TO: brain.run()
METAFLOW: CONDA_CHANNELS=conda-forge python brain.py --environment=conda run --data_=datasets/1073841789.json --vid_id=1073841789
'''
from metaflow import FlowSpec, Parameter, IncludeFile, step, conda, conda_base, retry
from io import StringIO
import pandas as pd
import numpy as np
import json

import algo1, algo2, algo3_0, algo3_5, algo3_6, algo4
from helpers import data_handler as d
from helpers import exceptions as e


def get_python_version():
    """
    A convenience function to get the python version.
    This ensures that the conda environment is created with an
    available version of python.
    """
    import platform
    versions = {'2': '2.7.15',
                '3': '3.7',
                '4': '3.9.5',
                '5': '3.8.8'}
    return versions[platform.python_version_tuple()[0]]


# Use the specified version of python for this flow.
@conda_base(libraries={'numpy':'1.20.2', 'pandas':'1.2.3','tqdm':'4.60.0', 'nltk':'3.6.2'}, python='3.8.8')
class brainFlow(FlowSpec):
    # allow for data input, default is the sample_med.json
    # python brain.py --environment=conda run --data_=/path/to/data 
    
    vid_id = Parameter('vid_id',
                       help='ID of stream video')
    data_ = IncludeFile('data_', 
                        help='Twitch stream chat log, json file')
    clip_length = Parameter('clip_length', 
                            default=0.5,
                            help="Length of recommended clips in minutes, default is 0.5 minutes")
    chosen_algos = Parameter('chosen_algos',
                             default=['algo1', 'algo2', 'algo3_0', 'algo3_5', 'algo3_6', 'algo4'],
                             help='''list of algos as str that should be run to create feature set''')
    select_features = Parameter('select_features',
                                default='all',
                                help='''either 'all' or a dictionary where keys are one of 'algo1', 'algo2', 
'algo3_0', 'algo3_5', 'algo3_6', 'algo4' and values a list of str representing features to return
NOTE: see algo docstring for feature options''')

    dev_mode = Parameter('dev_mode',
                         default=False,
                         help='''if True, opens file `vid_id` with json.load(open()), provides
a progress bar for jupyter notebook, and labels each feature with the algo that made it''')
    ccc_df_loc = Parameter('ccc_df_loc',
                         default='datasets/collated_clip_dataset.txt',
                         help='location of dataset of ccc clips and properties')

    @step
    def start(self):
        'this step loads the data and gets variables ready according to user input'
        import numpy as np
        data = json.load(StringIO(self.data_))
        if self.dev_mode:
            self.label_features = True
        else:
            self.label_features = False
        if len(data) == 0:
            print(f"{self.vid_id} is empty")
            return np.array([])
        self.important_data = self.load_data(data, self.clip_length)
        self.first_stamp = self.important_data[0]
        self.chunk_df = self.important_data[1]

        self.next(self.organize_algos)
        # load and organize data so that one row is one chunk


    @step
    def organize_dataframe(self):
        'this step reorganizes columns'
        df = self.df
        begin_cols = ['start','end', 'vid_id']
        other_cols = []
        for col in df.columns:
            if col not in begin_cols:
                other_cols.append(col)

        all_cols = begin_cols + other_cols
        self.df = df[all_cols]
        self.next(self.label_timestamps)


    @step
    def organize_algos(self):
        'this step loops through selected algos and pairs them with the appropriate algo'


        # run each chosen algo
        self.next(self.run_algo, foreach='chosen_algos')


    @step
    def run_algo(self):
        '''
        Runs the algorithm, formats resulting dataset

        input
        -----
        algo: loaded algorithm class
        data: twitch data preformatted and chunkified
        select: "all" or dictionary of lists with columns to select from algo output
        algo_str: name of algorithm
        vid_id: video ID of twitch stream
        label_features: whether or not to label each feature with the algo that made it
        '''
        # self.input is created by metaflow with the foreach parameter
        all_algos_dict = {
            'algo1':algo1,
            'algo2':algo2,
            'algo3_0':algo3_0,
            'algo3_5':algo3_5,
            'algo3_6':algo3_6,
            'algo4':algo4
        }
        algo_str = self.input
        algo = all_algos_dict[algo_str]
        data = self.important_data
        select = self.select_features
        vid_id = self.vid_id
        label_features = self.label_features
        
        a = algo.featureFinder(data)
        res = a.run()

        if (type(select) == dict) & (algo_str in select):
            selected_columns = select[algo_str]
        else:
            selected_columns = "all"

        if label_features:
            feature_label = algo_str
        else:
            feature_label = None
        formatted, bad_columns = d.data_finalizer(res, 
                                                  vid_id=vid_id, 
                                                  select=selected_columns, 
                                                  algo_label=feature_label)
        if len(bad_columns) > 1:
            # if there is something in this list, the user defined columns in 
            # selected_columns was not found
            print(f"{algo_str}: The following columns were not found: {bad_columns}")
        elif len(bad_columns) == 1:
            print(f"{algo_str}: Column not found: {bad_columns}")

        # check the dataset is proper
        if not self.test_results(data, formatted):
            print(f"{algo_str} failed the test!")

        self.algo_features = formatted
        self.next(self.join_features)


    @step
    def join_features(self, algo_step):
        'this step merges the results of each algorithm into one dataset'
        features = [output.algo_features for output in algo_step]
        df = features[0]
        for i in range(1,len(features)):
            df = df.merge(features[i])
        self.df = df
        self.next(self.organize_dataframe)


    @step
    def label_timestamps(self):
        'this step labels each timestamp range as ccc or not'
        from helpers.ccc_labeling import cccLabeler

        c = cccLabeler(first_stamp = self.first_stamp, brain_df = self.df, ccc_df_loc = self.ccc_df_loc)
        df = c.run()
        self.result = df
        self.next(self.end)


    @step
    def end(self):
        'this step just returns the result'
        return self.result

    def load_data(self, data: list, clip_length: float) -> tuple:
        """
        Loads and splits data into appropriate chunks 

        output
        ------
            first_stamp: timestamp of the first chat message
            chunk_df: dataframe of chunks, retaining all info from big_df
            vid_id: stream id of chat transcript
        """
        from helpers import data_handler as dh
        import pandas as pd

        big_df = dh.organize_twitch_chat(data)  # organize
        if type(big_df) == pd.DataFrame:
            first_stamp, chunks_list = dh.get_chunks(big_df, min_=clip_length)
            vid_id = data[0]["content_id"]
            chunk_df = pd.DataFrame()

            for dataframe in chunks_list:
                dataframe = dataframe.sort_values("created_at")
                dataframe["start"] = dataframe.iloc[0, 0]
                dataframe["end"] = dataframe.iloc[-1, 0]
                chunk_df = chunk_df.append(dataframe)

            chunk_df = chunk_df.reset_index(drop=True)
            return (first_stamp, chunk_df, vid_id, chunks_list)
        else:
            return np.array([])


    def test_results(self, data, dataframe):
        """
        Checks that we retained all chunks, and that chunks have start/end times
        """
        num_chunks = len(data[-1])
        num_results = len(dataframe)

        if (
            (num_chunks == num_results)
            & ("start" in dataframe.columns)
            & ("end" in dataframe.columns)
        ):
            return True
        else:
            print(num_results, num_chunks)
            print(dataframe.columns)
            return False

if __name__ == '__main__':
    brainFlow()