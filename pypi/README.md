For background information, including a description of each algorithm, see the `README.md` of the [parent folder](https://github.com/pillargg/twitch_chat_analysis) in the github repo.
# Table of Contents
1. [Use](#use)
   1. [Input variables](#input-variables)
   2. [Output variables](#output-variables)
5. [Build and Publish](#build)

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
   
# Build
To build and publish this package we are using the [poetry](https://python-poetry.org/) python packager. It takes care of some background stuff that led to [mistakes in the past](https://github.com/pillargg/twitch_chat_analysis/issues/8).

Folder structure:
```
|-- pypi
    |-- pillaralgos  # <---- note that poetry didn't require an additional subfolder
        |-- helpers
            |-- __init__.py
            |-- data_handler.py
            |-- graph_helpers.py
            |-- sanity_checks.py
        |-- __init__.py  # must include version number
        |-- algoXX.py  # all algorithms in separate files
    |-- LICENSE
    |-- README.md
    |-- pyproject.toml  # must include version number
```
To publish just run the `poetry publish --build` command after update version numbers as needed.
