# Table of Contents
1. [Background](#background)
   1. [Algorithms](#algorithms)
   2. [Datasets](#datasets)
3. [Current Goal](#current-goal)
4. [Long Term Goal](#long-term-goal)

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
1. Preliminary data `prelim_df`: 545 rows representing one 3 hour 35 minute 26 second twitch stream chat of [Hearthstone by LiiHS](https://www.twitch.tv/videos/963184458)
    * Used to create initial json import and resulting df clean/merge function `organize_twitch_chat`
2. Big data `big_df`: 2409 rows representing one 7 hour 37 minute, 0 second twitch stream chat of [Hearthstone by LiiHS](https://www.twitch.tv/videos/955629991)
    * Used to create all algorithms

# Current Goal

To create one overarching algorithm that will find the most "interesting" clips in a twitch VOD. This will be created through the following steps:
1. Creation of various algorithms that isolate `min_` (2 by default) minute chunks. The basic workflow:
   1. Create variable (ex: `num_words`, for number of words in the body of a chat message)
   1. Group df by `min_` chunks, then average/sum/etc `num_words` for each `min_` chunks
   1. Sort new df by `num_words`, from highest "value" to lowest "value"
   1. Return this new df as json ([example](https://github.com/pomkos/twitch_chat_analysis/blob/main/exports/algo1_results.json))
1. Users rate clips provided by each algorithm
2. Useless algorithms thrown away
3. Rest of the algorithms merged into one overarching algorithm, with weights distributed based on user ratings

# Long Term Goal

* __New objective measure__: community created clips (`ccc`) for a given VOD id with start/end timestamps for each clip
* __Assumption__: `ccc` are interesting and can be used to create a narrative for each VOD. We can test this by cross referencing with posts to /r/livestreamfails upvotes/comments
* __Hypothesis__: if we can predict where `ccc` would be created, those are potentially good clips to show the user
   * *Short term test*: Create a model to predict where ccc would be created using variables such as word count, chat rate, emoji usage, chat semantic analysis. We can do this by finding timestamps of ccc and correlating them with chat stats
   * *Medium term test*: Use top 100 streamers as training data. What similarities do their ccc and reddit most upvoted of that VOD share? (chat rate etc)
      1. Get the transcript for these top 100
      2. Get the top 100's YT posted 15-30min story content for the 8 hour VOD
      3. Get the transcript for that story content
      4. Semantic analysis and correlations, etc.
   * *Long term test*: what percentage of clips do our streamers actually end up using
