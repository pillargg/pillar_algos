# Table of Contents
1. [Background](#background)
   1. [Algorithms](#algorithms)
   2. [Datasets](#datasets)
3. [Current Goal](#current-goal)
4. [Metaflow](#metaflow)
   1. [Steps](#steps)
   2. [How to](#how-to)
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

Brain is set up to work with metaflow is ease of deployment and debugging. The current flow is below:

<img src = "https://github.com/pillargg/pillar_algos/raw/new_brain/graph.png" >

## Steps

1. Start

## How To

To run brain locally in conda:

`CONDA_CHANNELS=conda-forge python brain.py --environment=conda run --data_=datasets/1073841789.json --vid_id=1073841789`

To create a graph of the flow first install graphviz `sudo apt install graphviz` and then run the command below:

`python brain.py --environment=conda output-dot | dot -Tpng -o graph.png`
