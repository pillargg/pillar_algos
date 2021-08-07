# Table of Contents
1. [Background](#background)
1. [Features](#features)
   1. New ideas from readings
3. [Dataset](#dataset)


# Background
Pillar is creating machine learning models to detect great content during twitch streams. We have two models in mind: 1) predict which clips in a stream have potential to go viral 2) predict which clips (and in what order) could be used in a youtube video. 

All code and documentation so far is focused on 1) predict which clips in a stream have potential to viral. 

## Features

1. [Algorithm 1](https://github.com/pomkos/twitch_chat_analysis/blob/reorganize_repo/algorithm_1.ipynb): Find the best moments in clips based on where the most users participated. Most is defined as the *ratio of unique users* during a 2 min section to unique users for the entire session.
1. [Algorithm 2](https://github.com/pomkos/twitch_chat_analysis/blob/reorganize_repo/algorithm_2.ipynb) Find the best moments in clips based on when rate of messages per user peaked. This involves answering the question "at which 2 min segment do the most users send the most messages?". If users X, Y, and Z all send 60% of their messages at timestamp range delta, then that timestamp might qualify as a "best moment"
   1. __NOTE__: Currently answers the question "at which 2 min segment do users send the most messages fastest"
1. [Algorithm 3 (WIP)](https://github.com/pomkos/twitch_chat_analysis/blob/reorganize_repo/algorithm_3.ipynb) Weigh each user by their chat rate, account age, etc. Heavier users predicted to chat more often at "best moment" timestamps 
   1. __STATUS__: current weight determined by (`num_words_of_user`/`num_words_of_top_user`)
   1. [Algorithm 3.5](https://github.com/pomkos/twitch_chat_analysis/blob/reorganize_repo/algorithm_3.5.ipynb) Weighs clips based on most number of words/emojis/both used in chat
   2. Algo 3.6: ranks algorithms based mean emoji use by users, calculated as "number of emojis used at timestamp divided by number of unique users at that timestamp"
4. Algo 4: NLP sentiment per clip segment
   1. Weighs each timestamp by what percent of sentiment was positive, negative, or neutral

### New ideas from readings

1. _This is basically algo 3_5_: Repeated Lines This simple comparison is also a running percentage of the number of repeated lines in a segment. Emotes excluded again this is a very simple text comparison. In future iterations I would hope to be able to take advantage of a better (and cheaper :)) text analysis tool to better compare text lines for similarity.
1. _This is basically algo 3_6_: Emote Spam This simple calculation shows the percentage of chat lines that were emote only and contained more than one emote. No hard calculations here as I am able to grab the emote tags to determine if emotes are present and how many and this becomes my counter.

## Dataset:

ML_Infra created a dataset from the top 100 CCCs for the top 50 games, and pulled the chat logs for each videoId that the CCCs came from. 

Currently its in https://github.com/pillargg/timestamps/tree/add-datasetcreator-lambda/lambdas/datasetcreator, but it will be moved to the ML_Infra repo soon. 
