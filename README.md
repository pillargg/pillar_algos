# Background

__Description__:

Pillar is creating an innovative way to automatically select and splice clips from Twitch videos for streamers. This repo is focusing on the algorithm aspect. Three main algorithms are being tested.

1. [Algorithm 1](https://github.com/pomkos/twitch_chat_analysis/blob/reorganize_repo/algorithm_1.ipynb): Find the best moments in clips based on where the most users participated. Most is defined as the *ratio of unique users* during a 2 min section to unique users for the entire session.
1. [Algorithm 2](https://github.com/pomkos/twitch_chat_analysis/blob/reorganize_repo/algorithm_2.ipynb) Find the best moments in clips based on when rate of messages per user peaked. This involves answering the question "at which 2 min segment do the most users send the most messages?". If users X, Y, and Z all send 60% of their messages at timestamp range delta, then that timestamp might qualify as a "best moment"
   1. __NOTE__: Currently answers the question "at which 2 min segment do users send the most messages fastest"
1. [Algorithm 3 (WIP)](https://github.com/pomkos/twitch_chat_analysis/blob/reorganize_repo/algorithm_3.ipynb) Weigh each user by their chat rate, account age, etc. Heavier users predicted to chat more often at "best moment" timestamps 
   1. [Algorithm 3.5](https://github.com/pomkos/twitch_chat_analysis/blob/reorganize_repo/algorithm_3.5.ipynb) Finds the best moments in clips based on most number of words/emojis/both used in chat

__Datasets used__:
1. Preliminary data `prelim_df`: 545 rows representing one 3 hour 35 minute 26 second twitch stream chat of [Hearthstone by LiiHS](https://www.twitch.tv/videos/963184458)
    * Used to create initial json import and resulting df clean/merge function `organize_twitch_chat`
2. Big data `big_df`: 2409 rows representing one 7 hour 37 minute, 0 second twitch stream chat of [Hearthstone by LiiHS](https://www.twitch.tv/videos/955629991)
    * Used to create all algorithms
# Current Goal

To create one overarching algorithm that will find the most "interesting" clips in a twitch VOD. This will be created through the following steps:
1. Creation of various algorithms that isolate `min_` (2 by default) minute chunks. The basic workflow:
   1. Create variable (ex: `num_words`, for number of words in the body of a chat message)
   1. Group df by `min_` chunks, average/sum/etc the variable for each `min_` chunks
   1. Sort new df by variable, from highest "value" to lowest "value"
   1. Save this new df as json
1. Users rate clips provided by each algorithm
2. Useless algorithms thrown away
3. Rest of the algorithms merged into one overarching algorithm, with weights distributed based on user ratings
