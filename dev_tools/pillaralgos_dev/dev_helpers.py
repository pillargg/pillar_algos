"""
Tools for calling AWS, file management, graphing convenience.

HOW TO:
    aws = dev_help.awsBucketAPI()
    dev_help.plot_with_time(x, y, data, xformat="%H:%m")
"""


class awsBucketAPI:
    def __init__(self, choose_bucket=False):
        """
        Initializes connection to AWS bucket.

        NOTE:
            Must have AWS CLI installed and configured using `aws configure`
        HOW TO:
            aws = awsBucketAPI()
            results = aws.get_top_file_sizes(save=False)
            names = aws.get_random_file_names(n=5)
            aws.save_files(names)

        input
        -----
        choose_bucket: bool
            "False" to load default bucket (the one with full chat records)
            "True" to print out all buckets with "messagestore" in it, prompt user 
            to choose an id (also suggests 2 to choose from)
        """
        # connect to aws
        self.choose_bucket = choose_bucket
        import boto3

        self.s3r = boto3.resource("s3")
        self.s3c = boto3.client("s3")

        self.test = True  # if false, something is wrong
        self.get_bucket_name()

    def get_bucket_name(self):
        """
        Grabs the twitch chat bucket name. Returns False if 0 matches for "messagestore".
        """
        known_buckets = {
            'prod-prod-messagestore60e7afc8-z09kg03c2kxl':'Full chat records',
            'prod-timestamps-messagestore60e7afc8-dmylgjgqhcij':'CCC records'
        }
        # get list of buckets
        buckets = []
        for bucket in self.s3r.buckets.all():
            buckets.append(bucket.name)

        # bucket name and test
        chat_bucket = [x for x in buckets if "messagestore" in x]
        if len(chat_bucket) >= 0:
            if self.choose_bucket:
                print(chat_bucket)
                print('''
                Known buckets:
                    Full chat records [1]: prod-prod-messagestore60e7afc8-z09kg03c2kxl
                    CCC records [2]: prod-timestamps-messagestore60e7afc8-dmylgjgqhcij
                ''')
                chosen = input("Choose the bucket (ex: 1, 2, or a full id): ")
                # convenience, so user can choose 1 or 2
                if chosen == '1':
                    chosen = 'prod-prod-messagestore60e7afc8-z09kg03c2kxl'
                elif chosen == '2':
                    chosen = 'prod-timestamps-messagestore60e7afc8-dmylgjgqhcij'
                # select user chosen bucket
                self.chat_bucket = [buck for buck in chat_bucket if chosen in buck][0]
                # print appropriate message
                if chosen in known_buckets.keys():
                    print(f'Loaded {known_buckets[chosen]}')
                else:
                    print("Loaded user defined bucket")
            else:
                # select the default, full chat records
                self.chat_bucket = 'prod-prod-messagestore60e7afc8-z09kg03c2kxl'
                print("Loaded bucket with full chat records")
        else:
            print(f"{len(chat_bucket)} buckets contained 'messagestore'")
            self.test = False
    def get_all_filenames(self, save=False):
        '''
        Retrieves all filenames for user review

        input
        -----
        save: bool
            True if the files should be saved to data/*.json. Calls self.save_files.

        output
        ------
        results: list
            List of filenames, sorted by filesize
        '''
        import pandas as pd
        objects = self.s3c.list_objects(Bucket=self.chat_bucket)
        content = objects["Contents"]
        df_objects = pd.DataFrame.from_records(content)[["Key", "LastModified", "Size"]]
        df_objects = df_objects.sort_values("Size").reset_index(drop=True)
        
        if save:
            self.save_files(df_objects)
        else:
            return df_objects
        
    def get_top_filenames(self, save=False):
        """
        Retrieves 16 file names: the top 5 smallest files, top 5 largest files, and
        3 files +/- 3 from the median size's index.

        input
        -----
        save: bool
            True if the files should be saved to data/*.json. Calls self.save_files.

        output
        ------
        results: dict
            Dictionary of small/medium/large_files:[list of filenames]
        """
        import pandas as pd

        objects = self.s3c.list_objects(Bucket=self.chat_bucket)
        content = objects["Contents"]
        df_objects = pd.DataFrame.from_records(content)[["Key", "LastModified", "Size"]]
        df_objects = df_objects.sort_values("Size").reset_index(drop=True)

        # get 5 of the SMALL values
        small_size = df_objects.head(5)["Key"].values
        # get 5 of the LARGE values
        large_size = df_objects.tail(5)["Key"].values

        ## find MEDIAN size: ##
        median_size = df_objects["Size"].median()
        # get the index of all objects of that size
        med_results = df_objects[df_objects["Size"] == median_size]
        median_indices = med_results.index
        # if more than 1 index, find middle index
        size = len(median_indices)
        if size > 1:
            middle = (size % 2) + (round(size / 2) - 1)
            mid_index = med_results.iloc[middle : middle + 1, :].index[0]
            mid_size = df_objects.iloc[mid_index - 3 : mid_index + 3, :]["Key"].values
        else:
            # otherwise just use the middle index
            mid_size = df_objects.iloc[
                median_indices[0] - 3 : median_indices[0] + 3, :
            ]["Key"].values

        ## SAVE ##
        if save:
            self.save_files(small_size, prefix="sm")
            self.save_files(mid_size, prefix="med")
            self.save_files(large_size, prefix="lg")

        results = {
            "small_files": list(small_size),
            "medium_files": list(mid_size),
            "large_files": list(large_size),
        }
        return results

    def get_random_filenames(self, n, save=False):
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
            filename_array = chosen_df["Key"].values
            if save:
                self.save_files(filename_array)
            return filename_array

    def save_files(self, filename_list, prefix="", suffix=""):
        """
        Downloads into data folder as file.json

        input
        -----
        filename_list: list
            List of strings, where the string represents object name in aws
        prefix/suffix: str
            Adds prefix/suffix with "_" to the filename of each object in list
        """
        # Download files
        for filename in filename_list:
            aws_file = filename
            if suffix:
                filesave = filename + "_" + suffix
            if prefix:
                filesave = prefix + "_" + filename
            if (not suffix) and (not prefix):
                filesave = filename
            self.s3c.download_file(self.chat_bucket, aws_file, f"data/{filesave}.json")

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
