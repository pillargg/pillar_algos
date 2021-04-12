"""
Tools for File management, graphing convenience
"""


class awsBucketAPI:
    def __init__(self):
        """
        Connects to AWS message bucket, retrieves list of objects, randomly selects `n`
        to save in "data/{object_name}.json"

        HOW TO:
            aws = awsBucketAPI()
            results = aws.get_top_file_sizes(save=False)
            names = aws.get_random_file_names(n=5)
            aws.save_files(names)
        NOTE:
            Must have AWS CLI installed and configured using `aws configure`
        """
        # connect to aws
        import boto3

        self.s3r = boto3.resource("s3")
        self.s3c = boto3.client("s3")

        self.test = True  # if false, something is wrong
        self.get_bucket_name()

    def get_bucket_name(self):
        """
        Grabs the twitch chat bucket name, as long as its the only one that contains
        "messagestore" in it. Returns False if more than one match.
        """
        # get list of buckets
        buckets = []
        for bucket in self.s3r.buckets.all():
            buckets.append(bucket.name)
        # bucket name and test
        chat_bucket = [x for x in buckets if "messagestore" in x]
        if len(chat_bucket) == 1:
            self.chat_bucket = chat_bucket[0]
        else:
            print(f"{len(chat_bucket)} buckets contained 'messagestore'")
            self.test = False

    def save_specific_file(self, filename, suffix="", prefix=""):
        """
        Downloads a specific file from aws bucket, saving to data/ folder as one of:
            - filename.json
            - prefix_filename.json
            - filename_suffix.json
            - prefix_filename_suffix.json
        """
        aws_file = filename
        if suffix:
            filesave = filename + "_" + suffix
        if prefix:
            filesave = prefix + "_" + filename
        if (not suffix) and (not prefix):
            filesave = filename

        self.s3c.download_file(self.chat_bucket, aws_file, f"data/{filesave}.json")

    def get_top_file_sizes(self, save=True):
        '''
        Retrieves 16 files: the top 5 smallest files, top 5 largest files, and
        3 files +/- 3 from the median size's index.

        input
        -----
        save: bool
            True if the files should be saved to data/*.json

        output
        ------
        results: dict
            Dictionary of small/medium/large_files:[list of filenames]
        '''
        import pandas as pd

        objects = self.s3c.list_objects(Bucket=self.chat_bucket)
        content = objects['Contents']
        df_objects = pd.DataFrame.from_records(content)[['Key','LastModified','Size']]
        df_objects = df_objects.sort_values('Size').reset_index(drop=True)
        
        # get 5 of the SMALL values
        small_size = list(df_objects.head(5)['Key'].values)
        # get 5 of the LARGE values
        large_size = list(df_objects.tail(5)['Key'].values)

        ## find MEDIAN size: ##
        median_size = df_objects['Size'].median()
        # get the index of all objects of that size
        med_results = df_objects[df_objects['Size'] == median_size]
        median_indices = med_results.index
        # if more than 1 index, find middle index
        size = len(median_indices)
        if size > 1:
            middle = (size % 2) + (round(size / 2) - 1)
            mid_index = med_results.iloc[middle:middle+1,:].index[0]
            mid_size = df_objects.iloc[mid_index-3:mid_index+3, :]['Key'].values
        else:
            # otherwise just use the middle index
            mid_size = df_objects.iloc[median_indices[0]-3:median_indices[0]+3, :]['Key'].values
            
        ## SAVE ##
        if save:
            for file in small_size:
                aws.save_specific_file(file, prefix='sm')

            for file in mid_size:
                aws.save_specific_file(file, prefix='med')

            for file in large_size:
                aws.save_specific_file(file, prefix='lg')
        results = {
            'small_files': small_size,
            'medium_files': mid_size,
            'large_files': large_size
        }
        return results

    def get_random_file_names(self, n):
        """
        Randomly select `n` files in the bucket, returns the filenames as an array
        """
        import pandas as pd

        if not self.chat_bucket:
            self.test = False
        else:

            # get the objects
            response = self.s3c.list_objects(Bucket=self.chat_bucket)
            content = response["Contents"]
            # format json
            content_info = pd.DataFrame.from_records(content)[
                ["Key", "LastModified", "Size"]
            ]
            # get 5 samples
            chosen_df = content_info.sample(n)
            chosen = chosen_df["Key"].values
            return chosen

    def save_files(self, chosen):
        """
        Downloads into data folder as file.json
        """
        # Download files
        for f in chosen:
            self.s3c.download_file(self.chat_bucket, f, f"data/{f}.json")


def plot_with_time(x, y, data, xformat="%H:%m"):
    """
    Plots a scatterplot with the xaxis neatly formatted

    input
    -----
    x: str
        Column name. Column must be datetime
    y: str
    data: pd.DataFrame
    xformat: str
        Format xaxis should be displayed in, using strftime syntax
    """
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import seaborn as sns

    fig, ax = plt.subplots()
    sns.scatterplot(x=x, y=y, data=data)

    myFmt = mdates.DateFormatter(xformat)
    ax.xaxis.set_major_formatter(myFmt)
