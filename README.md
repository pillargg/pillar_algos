# Table of Contents
1. [Background](#background)
   1. [Algorithms](#algorithms)
   2. [Datasets](#datasets)
3. [Current Goal](#current-goal)
4. [Metaflow](#metaflow)
   1. [Parameters](#parameters)
   2. [Steps](#steps)
   3. [How to](#how-to)
# Background
Pillar is creating an innovative way to automatically select and splice clips from Twitch videos for streamers. This repo is focusing on the algorithm aspect. Three main algorithms are being tested.

## Algorithms

All algorithms had a complete rewrite as of Aug 17, 2021. They now return features for each chunk and do not sort the dataset. Features include:

__Algo1__:

- `stream_unique_users`: number of unique users in the stream
- `hour_unique_users`: number of unique users that hour
- `chunk_unique_users`: number of unique users that chunk
- `chunk_to_stream_unique_users`: ratio of chunk:stream unique users
- `chunk_to_hour_unique_users`: ratio of chunk:hour unique users

__Algo2__:

- `mean_chat_rate_per_minute`:  number of chats sent per minute found using the equation: $\frac{(number of messages sent by the user)}{(length of chunk in seconds)}*60$

__Algo3_0__:

- `num_chats_by_top_emoji_users`: the number of messages sent by top 5 emoji users at each chunk
- `num_chats_by_top_words_users`: the number of messages sent by top 5 words users at each chunk
- `num_chats_by_top_words_emoji_users`: the number of messages sent by top 5 words and emoji users at each chunk

__Algo3_5__:

- `num_words`: number of words at that chunk
- `num_emo`: number of emoticons at that chunk
- `num_words_emo`: number words + emoticons at that chunk

__Algo3_6__:

- `num_emo`: the number of emoticons used in the chunk
- `chunk_unique_users`: the number of users in the chunk
- `perc_emoji_of_stream`: ratio of emojis in chunk / total emojis in stream
- `emoji_user_ratio`: ratio of 'emojis in chunk' / 'number of unique chatters in chunk'

__Algo4__:

- `positive` - strength of positive sentiment
- `negative` - strength of negative sentiment
- `neutral` - strength of neutral sentiment
- `compound` - overall sentiment where > 0.05 is positive,
    < -0.05 is negative, in between is neutral
- `abs_overall` - absolute value of "compound", resulting in a
    mixture of positive and negative (but not neutral) chat timescripts
- `mostly` - indicating whether the overall sentiment is mostly
    positive, neutral, or negative. Calculated using self.cat_compound()

## Datasets:

Three datasets are in progress.

1. CCC dataset - containing timestamps and other features for each CCC that @gatesyp downloaded
2. CCC stream dataset - containing the entire twitch stream chat log for each CCC
3. Featureset - created with `brain`, contains results of feature engineering with algos

# Current Goal

To label each timestamp as CCC or not CCC, then use categorical supervised ML algorithm to predict future CCC clips based on twitch chat featureset.

# Metaflow

Brain is set up to work with metaflow is ease of deployment and debugging. The flow is explained here.

## Parameters

Only two parameters, `vid_id` and `data_` are required to run brain, the rest have defaults selected.

* `vid_id`: ID of the twitch video that has chat log. This is used to confirm that the ID exists in our CCC database
* `data_`: Location of the chat log as a json file
* `clip_length`: How long each clip range should be, in minutes. 
   * Default: `0.5`, this is half a minute (30 seconds)
* `chosen_algos: A list of algorithms to run. By default all algorithms are selected
   * Default: `['algo1','algo2','algo3_0','algo3_5','algo3_6','algo4']`
* `select_features`: Select the features to get from each algorithm, in dictionary form. See example below. 
   * Default: `'all'`, to return all calculated features. See feature descriptions above for more info.
   * _NOTE_: duplicate variables will be merged prior to returning the feature set

```
# this example will return all features for demonstration purposes. It's enough to pass the string 'all' to select_features, same result.
select_features = {
   'algo1':['stream_unique_users', 'hour_unique_users', 'chunk_unique_users', 'chunk_to_stream_unique_users', 'chunk_to_hour_unique_users'],
   'algo2':['mean_chat_rate_per_minute'],
   'algo3_0':['num_chats_by_top_emoji_users','num_chats_by_top_words_users','num_chats_by_top_words_emoji_users'],
   'algo3_5':['num_words', 'num_emo', 'num_words_emo'],
   'algo3_6':['num_emo','chunk_unique_users','perc_emoji_of_stream','emoji_user_ratio'],
   'algo4':['positive','negative','neutral','compound','abs_overall','mostly']
}
```

* `dev_mode`: Whether or not to run in dev mode. This mode will load the data using `json.load(open())` instead of `StringIO`, provides a progress bar for jupyter notebooks, and labels each feature with the algo that made it.
   * Default: `False`
* `ccc_df_loc`: Location of the CCC database
   * Default: `datasets/collated_clip_dataset.txt`

## Steps

<img src = "https://github.com/pillargg/pillar_algos/raw/new_brain/graph.png" >

1. Start
   1. Load the data and organize into clips of `clip_length` length using the `load_data()` function and assign relevant variables to class variables
2. Organize algorithms
   1. Loops through each user provided algorithm and runs them using `run_algos()` function, then merges the results into one dataframe
   2. If `dev_mode = True` will show a progress bar for jupyter notebook
3. Organize dataframe
   1. Reorganizes the feature set so columns are in a standard order
4. Label timestamps
   1. Runs the `cccLabeler()` class to label each timestamp range in the feature set as overlapping the CCC timestamps in the CCC dataset. True if overlapped, False if not.
5. End
   1. Returns the feature set

## How To

To run brain locally in conda:

`CONDA_CHANNELS=conda-forge python brain.py --environment=conda run --data_=datasets/1073841789.json --vid_id=1073841789`

To create a graph of the flow first install graphviz `sudo apt install graphviz` and then run the command below:

`python brain.py --environment=conda output-dot | dot -Tpng -o graph.png`
