NOTE: This readme is just a quick reference. For more details include todo, near/medium/long term goals please see our GitHub page.

# Table of Contents
1. [Use](#use)
   1. [Input variables](#input-variables)
   2. [Output variables](#output-variables)
2. [Background](#background)
   1. [Algorithms](#algorithms)
   1. [Timeit Results](#timeit-results)
3. [Build and Publis](#build)
4. [Changelog](#changelog)

# Use

To use any of the algorithms just import as needed with `from pillaralgos import algo1`, and then `algo1(data, min_=2, save_json=False)`.

## Input variables

```
save_json: bool
    True if want to save results as json to exports folder
data: list
min_: int
    Approximate number of minutes each clip should be
sort_by: str
    For algo1 ONLY
    'rel': "number of chatters at timestamp"/"number of chatters at that hour"
    'abs': "number of chatters at timestamp"/"total number of chatters in stream"
goal: str
    For algo3_5 ONLY
    'num_words': sum of the number of words in each chat message
    'num_emo': sum of the number of emoticons in each chat message
    'num_words_emo': sum of the number of words + emoticons in each chat message
min_words:int
    For algo3_0 ONLY
    When filtering chunks to top users, at least how many words the top user should send
```

## Output variables

* All algorithms will return a `result_json`, list of dictionaries in the format of `{start:seconds, end:seconds}` where `seconds` is seconds elapsed since start of the stream. List is ordered from predicted best to worst timestamps.
* All algorithms can save the returned list as a .json if `save_json=True` is passed in.

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
Results as of `April 13, 2021 18:31 EST` run on `big_df` with 80841 rows, 10 columns.

| algo1  | algo2        | algo3_0 | algo3_5 |
|--------|--------------|---------|---------|
|2.2 sec | 1 min 23 sec |28.1 sec | 16.3 sec|

# Build
To build and publish this package we are using the [poetry](https://python-poetry.org/) python packager. It takes care of some background stuff that led to [mistakes in the past](https://github.com/pillargg/twitch_chat_analysis/issues/8).

Folder structure:
```
|-- dev_tools
    |-- pillaralgos_dev
        |-- __init__.py
        |-- dev_helpers.py # aws connection, file retrieval script
        |-- sanity_checks.py # placeholder
    |-- README.md 
    |-- pyproject.toml
|-- prod
    |-- pillaralgos  # <---- note that poetry didn't require an additional subfolder
        |-- helpers
            |-- __init__.py
            |-- data_handler.py
            |-- emoji_getter.py
        |-- __init__.py  # must include version number
        |-- algoXX.py  # all algorithms in separate files
        |-- brain.py
    |-- LICENSE
    |-- README.md
    |-- pyproject.toml  # must include version number
    |-- reinstall_pill.sh # quick script to uninstall local pillaralgos, build and install new one
```
To publish just run the `poetry publish --build` command after update version numbers as needed.

# Changelog

* New algorithms
* Algo3.6: rank timestamps by emoji:user ratio
* Algo4: rank timestamps by compound score from SentimentAnalyzer
* Unit testing for algo 3.6