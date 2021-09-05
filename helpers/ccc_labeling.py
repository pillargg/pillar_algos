import pandas as pd
from helpers import exceptions as e

def load_ccc_data(loc: str = '../data') -> pd.DataFrame:
    '''
    Loads the ccc data that Steve sent me
    
    input
    -----
    loc: location of `collated_clip_dataset.txt`
    '''
    file = open(f'{loc}','r')
    lines = file.readlines()
    dontwork = []
    work = []
    for i in range(len(lines)):
        line = lines[i]
        try:
            line = eval(line)
            work.append(line)
        except:
            dontwork.append(line)

    dataframe = pd.json_normalize(work)
    dataframe = dataframe.rename({
        'id':'clip_id'
    }, axis=1)

    dataframe['num_tags'] = dataframe['game_metadata.genre'].apply(lambda x: len(x))

    dataframe = dataframe.astype({
        'broadcaster_id':int,
        'creator_id':int,
        'video_id':str,
        'game_id':int,
        'duration':float,
        'game_metadata.id':int,
        'pillar-clipRange.startTime':float,
        'pillar-clipRange.endTime':float,
        'num_tags':int,
        'created_at':'datetime64[ns, UTC]'
    })
    
    if len(dontwork) > 0:
        print(f"NOTE: {len(dontwork)} IDs did not load")

    return dataframe


class cccLabeler():
    def __init__(self, first_stamp, brain_df: pd.DataFrame, ccc_df_loc:str):
        '''
        Makes sure the vid_id exists in ccc database, converts timestamps to floats
        
        HOW TO: 
            c = cccLabeler(first_stamp, brain_df)
            labeled_df = c.run()
        '''
        ccc_df = load_ccc_data(loc = ccc_df_loc)
        vid_id = brain_df['vid_id'].unique()[0]
        ccc_clip = ccc_df[ccc_df['video_id'] == str(vid_id)]

        if ccc_clip.empty:
            # check if any vid_id is associated
            raise e.VidIdNotFound(vid_id=vid_id)
        else:
            # rename to be more friendly
            ccc_clip = ccc_clip.rename({
                'pillar-clipRange.startTime':'pillar_start',
                'pillar-clipRange.endTime':'pillar_end'
            }, axis=1)
            
            # get times in seconds from first stamp
            brain_df = brain_df.astype({'start':'datetime64', 'end':'datetime64'})
            brain_df['start_sec'] = self.sec_since_first(brain_df['start'], first_stamp)
            brain_df['end_sec'] = self.sec_since_first(brain_df['end'], first_stamp)
            
            self.vid_id = vid_id
            self.brain_df = brain_df
            self.ccc_clip = ccc_clip


    def run(self) -> pd.DataFrame:
        '''
        Iterates through the brain_df start/end columns to see if
        any of the ccc timestamps overlap
        '''
        ccc_overlap = []
        for idx, row in self.brain_df.iterrows():
            res = self.check_ccc(row['start_sec'], row['end_sec'])
            ccc_overlap.append(res)
        
        self.brain_df['ccc_overlap'] = pd.Series(ccc_overlap)
        return self.brain_df

    def check_ccc(self, start: float, end: float) -> str:
        '''
        Checks whether each of the ccc start/ends are within the
        given start/end range
        '''
        # create a list of all numbers between start and end
        clip_range = range(round(start), round(end)+1,1)

        # see if ccc fits in that range
        for idx, row in self.ccc_clip.iterrows():
            ccc_start = row['pillar_start']
            ccc_end = row['pillar_end']
            if (ccc_start in clip_range) | (ccc_end in clip_range):
                return True # if ccc is in the range, then range overlaps
        return False # otherwise no overlap
    
    def label_popularity(self, is_overlap):
        '''
        Label by popularity threshold
        '''
        ...
    
    def sec_since_first(self, my_series: pd.Series, first_timestamp) -> float:
        '''
        Finds how long each row is from the first timestamp of the stream
        '''
        res = my_series - first_timestamp
        return res.apply(lambda x: x.total_seconds())