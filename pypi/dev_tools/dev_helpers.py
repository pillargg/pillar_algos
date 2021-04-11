'''
Functions and classes to help with development. Stuff that isn't required in 
prod for algos to work. Like downloading files from AWS, renaming files, 
graphing, and so on.
'''


class awsBucketAPI:
    def __init__(self):
        '''
        Connects to AWS message bucket, retrieves list of objects, randomly selects `n`
        to save in "data/{object_name}.json"

        HOW TO:
            aws = awsBucketAPI()
            names = aws.get_random_file_names(n=5)
            aws.save_files(names)
        NOTE:
            Must have AWS CLI installed and configured using `aws configure`
        '''
        # connect to aws
        import boto3
        self.s3r = boto3.resource('s3')
        self.s3c = boto3.client('s3')

        self.test = True  # if false, something is wrong
        self.get_bucket_name()
        
    def get_bucket_name(self):
        '''
        Grabs the twitch chat bucket name, as long as its the only one that contains
        "messagestore" in it. Returns False if more than one match.
        '''
        # get list of buckets
        buckets = []
        for bucket in self.s3r.buckets.all():
            buckets.append(bucket.name)
        # bucket name and test
        chat_bucket = [x for x in buckets if 'messagestore' in x]
        if len(chat_bucket) == 1:
            self.chat_bucket=chat_bucket[0]
        else:
            print(f"{len(chat_bucket)} buckets contained 'messagestore'")
            self.test = False

    def get_random_file_names(self, n):
        '''
        Randomly select `n` files in the bucket, returns the filenames as an array
        '''
        import pandas as pd
        if not self.chat_bucket:
            self.test = False
        else:

            # get the objects
            response = self.s3c.list_objects(Bucket=self.chat_bucket)
            content = response['Contents']
            # format json
            content_info = pd.DataFrame.from_records(content)[['Key','LastModified','Size']]
            # get 5 samples
            chosen_df = content_info.sample(n)
            chosen = chosen_df['Key'].values
            return chosen

    def save_files(self, chosen):
        '''
        Downloads into data folder as file.json
        '''
        # Download files
        for f in chosen:
            self.s3c.download_file(self.chat_bucket, f, f'data/{f}.json')
            
def plot_with_time(x,y,data, xformat='%H:%m'):
    '''
    Plots a scatterplot with the xaxis neatly formatted
    
    input
    -----
    x: str
        Column name. Column must be datetime
    y: str
    data: pd.DataFrame
    xformat: str
        Format xaxis should be displayed in, using strftime syntax
    '''
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import seaborn as sns
    
    fig, ax = plt.subplots()
    sns.scatterplot(x=x,y=y,data=data)
    
    myFmt = mdates.DateFormatter(xformat)
    ax.xaxis.set_major_formatter(myFmt)
