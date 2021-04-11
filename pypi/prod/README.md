# Table of Contents
1. [Build and Publish](#build)
1. [Background](#background)
   1. [Algorithms](#algorithms)
   1. [Timeit Results](#timeit-results)
3. [Current Goal](#current-goal)
4. [Long Term Goal](#long-term-goal)

# Build
To build and publish this package we are using the [poetry](https://python-poetry.org/) python packager. It takes care of some background stuff that led to mistakes in the past.

Folder structure:
```
|-- pypi
    |-- pillaralgos
        |-- helpers
            |-- __init__.py
            |-- data_handler.py
            |-- graph_helpers.py
            |-- sanity_checks.py
        |-- __init__.py  # must include version number
        |-- algoXX.py
    |-- LICENSE
    |-- README.md
    |-- pyproject.toml  # must include version number
```
To publish just run the `poetry publish --build` command after update version numbers as needed.

# Background
Pillar is creating an innovative way to automatically select and splice clips from Twitch videos for streamers. This repo is focusing on the algorithm aspect. Three main algorithms are being tested.

## Algorithms

1. [Algorithm 1](https://github.com/pomkos/twitch_chat_analysis/blob/reorganize_repo/algorithm_1.ipynb): Find the best moments in clips based on where the most users participated. Most is defined as the *ratio of unique users* during a 2 min section to unique users for the entire session.
1. [Algorithm 2](https://github.com/pomkos/twitch_chat_analysis/blob/reorganize_repo/algorithm_2.ipynb) Find the best moments in clips based on when rate of messages per user peaked. This involves answering the question "at which 2 min segment do the most users send the most messages?". If users X, Y, and Z all send 60% of their messages at timestamp range delta, then that timestamp might qualify as a "best moment"
   1. __NOTE__: Currently answers the question "at which 2 min segment do users send the most messages fastest"
1. [Algorithm 3 (WIP)](https://github.com/pomkos/twitch_chat_analysis/blob/reorganize_repo/algorithm_3.ipynb) Weigh each user by their chat rate, account age, etc. Heavier users predicted to chat more often at "best moment" timestamps 
   1. __STATUS__: current weight determined by (`num_words_of_user`/`num_words_of_top_user`)
   1. [Algorithm 3.5](https://github.com/pomkos/twitch_chat_analysis/blob/reorganize_repo/algorithm_3.5.ipynb) Finds the best moments in clips based on most number of words/emojis/both used in chat

### Timeit results
Results as of `4/11/21 12:21am EST` run on `big_df` with 1039228 rows, 11 columns.

| algo1  | algo2        | algo3_0 | algo3_5 |
|--------|--------------|---------|---------|
|3.4 sec | 3 min 14 sec |39.4 sec | 28 sec  |

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
