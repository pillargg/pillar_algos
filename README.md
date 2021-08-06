# Table of Contents
1. [Background](#background)
   1. [Algorithms](#algorithms)
   2. [Datasets](#datasets)
3. [Current Goal](#current-goal)
4. [Long Term Goal](#long-term-goal)
5. [Testing Locally](#testing-locally)
6. [Usage](#usage)

# Background
Pillar is creating an innovative way to automatically select and splice clips from Twitch videos for streamers. This repo is focusing on the algorithm aspect. Three main algorithms are being tested.

## Algorithms

1. [Algorithm 1](https://github.com/pomkos/twitch_chat_analysis/blob/reorganize_repo/algorithm_1.ipynb): Find the best moments in clips based on where the most users participated. Most is defined as the *ratio of unique users* during a 2 min section to unique users for the entire session.
1. [Algorithm 2](https://github.com/pomkos/twitch_chat_analysis/blob/reorganize_repo/algorithm_2.ipynb) Find the best moments in clips based on when rate of messages per user peaked. This involves answering the question "at which 2 min segment do the most users send the most messages?". If users X, Y, and Z all send 60% of their messages at timestamp range delta, then that timestamp might qualify as a "best moment"
   1. __NOTE__: Currently answers the question "at which 2 min segment do users send the most messages fastest"
1. [Algorithm 3 (WIP)](https://github.com/pomkos/twitch_chat_analysis/blob/reorganize_repo/algorithm_3.ipynb) Weigh each user by their chat rate, account age, etc. Heavier users predicted to chat more often at "best moment" timestamps 
   1. __STATUS__: current weight determined by (`num_words_of_user`/`num_words_of_top_user`)
   1. [Algorithm 3.5](https://github.com/pomkos/twitch_chat_analysis/blob/reorganize_repo/algorithm_3.5.ipynb) Finds the best moments in clips based on most number of words/emojis/both used in chat
   2. Algo 3.6: Average sentiment of emojis used in the clip range
4. Algo 4: Average NLP sentiment during clip range
   1. Make sentiment for the overall stream, and rank clip for how intense of an emotion it is compared to the overall sentiment

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

# Testing Locally

There are two methods to test locally, with one working on just Unix-based OSes, and one working on all OSes. Testing with Containers will work on all OSes with Docker installed. 

## Testing with Containers

This is the recommended method for testing and should work on all operating systems.

First, install [Docker](https://docs.docker.com/get-docker/) and [act](https://github.com/nektos/act). This is a tool that allows the running of GitHub Actions CI locally, which is how we will run the tests on your local machine. After both are installed, you have to generate a GitHub Token. See [here] on how to do that. The token should be stored in a file called `.secrets` in your working directory (this file is in the .gitignore so it will not be committed). Here is what the file should look like:

```bash
GITHUB_TOKEN=<your token here>
```

After, you can run the tests with the following:

```bash
act
```

Here is an example of what output should look like:
<details>
  <summary>Log</summary>

```none
[Run Unit Tests/test] 🚀  Start image=catthehacker/ubuntu:act-20.04
[Run Unit Tests/test]   🐳  docker run image=catthehacker/ubuntu:act-20.04 platform= entrypoint=["/usr/bin/tail" "-f" "/dev/null"] cmd=[]
[Run Unit Tests/test] ⭐  Run Checkout Code
[Run Unit Tests/test]   ☁  git clone 'https://github.com/actions/checkout' # ref=v2
[Run Unit Tests/test]   🐳  docker cp src=C:\Users\chizz\.cache\act/actions-checkout@v2/ dst=/mnt/c/Users/chizz/Documents/pillar/pillar_algos/_actions/actions-checkout@v2/
[Run Unit Tests/test]   ❓  ::save-state name=isPost,::true
[Run Unit Tests/test]   💬  ::debug::GITHUB_WORKSPACE = '/mnt/c/Users/chizz/Documents/pillar/pillar_algos'
[Run Unit Tests/test]   💬  ::debug::qualified repository = 'pillargg/pillar_algos'
[Run Unit Tests/test]   💬  ::debug::ref = 'refs/heads/ci-cd'
[Run Unit Tests/test]   💬  ::debug::commit = '74c766153947d78164c3dc4fde3cffac2efe3630'
[Run Unit Tests/test]   💬  ::debug::clean = true
[Run Unit Tests/test]   💬  ::debug::fetch depth = 1
[Run Unit Tests/test]   💬  ::debug::lfs = false
[Run Unit Tests/test]   💬  ::debug::submodules = false
[Run Unit Tests/test]   💬  ::debug::recursive submodules = false
[Run Unit Tests/test]   ❓  ::add-matcher::/mnt/c/Users/chizz/Documents/pillar/pillar_algos/_actions/actions-checkout@v2/dist/problem-matcher.json
| Syncing repository: pillargg/pillar_algos
[Run Unit Tests/test]   ❓  ::group::Getting Git version info
| Working directory is '/mnt/c/Users/chizz/Documents/pillar/pillar_algos'
[Run Unit Tests/test]   💬  ::debug::Getting git version
| [command]/usr/bin/git version
| git version 2.25.1
[Run Unit Tests/test]   💬  ::debug::Set git useragent to: git/2.25.1 (github-actions-checkout)
[Run Unit Tests/test]   ❓  ::endgroup::
| Deleting the contents of '/mnt/c/Users/chizz/Documents/pillar/pillar_algos'
[Run Unit Tests/test]   ❓  ::save-state name=repositoryPath,::/mnt/c/Users/chizz/Documents/pillar/pillar_algos
[Run Unit Tests/test]   ❓  ::group::Initializing the repository
| [command]/usr/bin/git init /mnt/c/Users/chizz/Documents/pillar/pillar_algos
| Initialized empty Git repository in /mnt/c/Users/chizz/Documents/pillar/pillar_algos/.git/
| [command]/usr/bin/git remote add origin https://github.com/pillargg/pillar_algos
[Run Unit Tests/test]   ❓  ::endgroup::
[Run Unit Tests/test]   ❓  ::group::Disabling automatic garbage collection
| [command]/usr/bin/git config --local gc.auto 0
[Run Unit Tests/test]   ❓  ::endgroup::
[Run Unit Tests/test]   ⚙  ::add-mask::eC1hY2Nlc3MtdG9rZW46Z2hwX0d0ZDR4TUlDcVp6cGZoNkI5T1BRdGJOdXpvOGdBNTNiTmd6Vg==
[Run Unit Tests/test]   ❓  ::group::Setting up auth
| [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
| [command]/usr/bin/git submodule foreach --recursive git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :
| [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
| [command]/usr/bin/git submodule foreach --recursive git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :
| [command]/usr/bin/git config --local http.https://github.com/.extraheader AUTHORIZATION: basic ***
[Run Unit Tests/test]   ❓  ::endgroup::
[Run Unit Tests/test]   ❓  ::group::Fetching the repository
| [command]/usr/bin/git -c protocol.version=2 fetch --no-tags --prune --progress --no-recurse-submodules --depth=1 origin +74c766153947d78164c3dc4fde3cffac2efe3630:refs/remotes/origin/ci-cd
| remote: Enumerating objects: 56, done.        
remote: Counting objects: 100% (56/56), done.        
remote: Compressing objects: 100% (48/48), done.
| remote: Total 56 (delta 3), reused 33 (delta 1), pack-reused 0        
| From https://github.com/pillargg/pillar_algos
|  * [new ref]         74c766153947d78164c3dc4fde3cffac2efe3630 -> origin/ci-cd
[Run Unit Tests/test]   ❓  ::endgroup::
[Run Unit Tests/test]   ❓  ::group::Determining the checkout info
[Run Unit Tests/test]   ❓  ::endgroup::
[Run Unit Tests/test]   ❓  ::group::Checking out the ref
| [command]/usr/bin/git checkout --progress --force -B ci-cd refs/remotes/origin/ci-cd
| Switched to a new branch 'ci-cd'
| Branch 'ci-cd' set up to track remote branch 'ci-cd' from 'origin'.
[Run Unit Tests/test]   ❓  ::endgroup::
| [command]/usr/bin/git log -1 --format='%H'
| '74c766153947d78164c3dc4fde3cffac2efe3630'
[Run Unit Tests/test]   ❓  ::remove-matcher owner=checkout-git,::
[Run Unit Tests/test]   ✅  Success - Checkout Code
[Run Unit Tests/test] ⭐  Run Setup Python 3.8
[Run Unit Tests/test]   ☁  git clone 'https://github.com/actions/setup-python' # ref=v2
[Run Unit Tests/test]   🐳  docker cp src=C:\Users\chizz\.cache\act/actions-setup-python@v2/ dst=/mnt/c/Users/chizz/Documents/pillar/pillar_algos/_actions/actions-setup-python@v2/
[Run Unit Tests/test]   💬  ::debug::Semantic version spec of 3.8 is 3.8
[Run Unit Tests/test]   💬  ::debug::isExplicit: 
[Run Unit Tests/test]   💬  ::debug::explicit? false
[Run Unit Tests/test]   💬  ::debug::evaluating 0 versions
[Run Unit Tests/test]   💬  ::debug::match not found
| Version 3.8 was not found in the local cache
[Run Unit Tests/test]   💬  ::debug::set auth
[Run Unit Tests/test]   💬  ::debug::check 3.10.0-beta.1 satisfies 3.8
[Run Unit Tests/test]   💬  ::debug::check 3.10.0-alpha.7 satisfies 3.8
[Run Unit Tests/test]   💬  ::debug::check 3.10.0-alpha.6 satisfies 3.8
[Run Unit Tests/test]   💬  ::debug::check 3.10.0-alpha.5 satisfies 3.8
[Run Unit Tests/test]   💬  ::debug::check 3.10.0-alpha.4 satisfies 3.8
[Run Unit Tests/test]   💬  ::debug::check 3.10.0-alpha.3 satisfies 3.8
[Run Unit Tests/test]   💬  ::debug::check 3.10.0-alpha.2 satisfies 3.8
[Run Unit Tests/test]   💬  ::debug::check 3.10.0-alpha.1 satisfies 3.8
[Run Unit Tests/test]   💬  ::debug::check 3.9.5 satisfies 3.8
[Run Unit Tests/test]   💬  ::debug::check 3.9.4 satisfies 3.8
[Run Unit Tests/test]   💬  ::debug::check 3.9.3 satisfies 3.8
[Run Unit Tests/test]   💬  ::debug::check 3.9.2 satisfies 3.8
[Run Unit Tests/test]   💬  ::debug::check 3.9.2-rc.1 satisfies 3.8
[Run Unit Tests/test]   💬  ::debug::check 3.9.1 satisfies 3.8
[Run Unit Tests/test]   💬  ::debug::check 3.9.1-rc.1 satisfies 3.8
[Run Unit Tests/test]   💬  ::debug::check 3.9.0 satisfies 3.8
[Run Unit Tests/test]   💬  ::debug::check 3.9.0-rc.2 satisfies 3.8
[Run Unit Tests/test]   💬  ::debug::check 3.9.0-rc.1 satisfies 3.8
[Run Unit Tests/test]   💬  ::debug::check 3.9.0-beta.5 satisfies 3.8
[Run Unit Tests/test]   💬  ::debug::check 3.9.0-beta.4 satisfies 3.8
[Run Unit Tests/test]   💬  ::debug::check 3.8.10 satisfies 3.8
[Run Unit Tests/test]   💬  ::debug::x64===x64 && darwin===linux
[Run Unit Tests/test]   💬  ::debug::x64===x64 && linux===linux
[Run Unit Tests/test]   💬  ::debug::x64===x64 && linux===linux
[Run Unit Tests/test]   💬  ::debug::x64===x64 && linux===linux
[Run Unit Tests/test]   💬  ::debug::matched 3.8.10
| Version 3.8 is available for downloading
| Download from "https://github.com/actions/python-versions/releases/download/3.8.10-107001/python-3.8.10-linux-20.04-x64.tar.gz"
[Run Unit Tests/test]   💬  ::debug::Downloading https://github.com/actions/python-versions/releases/download/3.8.10-107001/python-3.8.10-linux-20.04-x64.tar.gz
[Run Unit Tests/test]   💬  ::debug::Destination /tmp/bfc2b5ad-62f1-4101-8131-960763558bae
[Run Unit Tests/test]   💬  ::debug::set auth
[Run Unit Tests/test]   💬  ::debug::download complete
| Extract downloaded archive
[Run Unit Tests/test]   💬  ::debug::Checking tar --version
[Run Unit Tests/test]   💬  ::debug::tar (GNU tar) 1.30%0ACopyright (C) 2017 Free Software Foundation, Inc.%0ALicense GPLv3+: GNU GPL version 3 or later <https://gnu.org/licenses/gpl.html>.%0AThis is free software: you are free to change and redistribute it.%0AThere is NO WARRANTY, to the extent permitted by law.%0A%0AWritten by John Gilmore and Jay Fenlason.
| [command]/usr/bin/tar xz --warning=no-unknown-keyword -C /tmp/b50560b8-c29b-4368-9961-8116845c95a2 -f /tmp/bfc2b5ad-62f1-4101-8131-960763558bae
| Execute installation script
| Check if Python hostedtoolcache folder exist...
| Creating Python hostedtoolcache folder...
| Create Python 3.8.10 folder
| Copy Python binaries to hostedtoolcache folder
| Create additional symlinks (Required for the UsePythonVersion Azure Pipelines task and the setup-python GitHub Action)
| Upgrading PIP...
| Looking in links: /tmp/tmp46b32jk4
| Requirement already satisfied: setuptools in /opt/hostedtoolcache/Python/3.8.10/x64/lib/python3.8/site-packages (56.0.0)
| Requirement already satisfied: pip in /opt/hostedtoolcache/Python/3.8.10/x64/lib/python3.8/site-packages (21.1.1)
[Run Unit Tests/test]   ❗  ::error::WARNING: Running pip as root will break packages and permissions. You should install packages reliably by using venv: https://pip.pypa.io/warnings/venv
| Collecting pip
| Downloading pip-21.1.1-py3-none-any.whl (1.5 MB)
| Installing collected packages: pip
| Successfully installed pip-21.1.1
[Run Unit Tests/test]   ❗  ::error::WARNING: Running pip as root will break packages and permissions. You should install packages reliably by using venv: https://pip.pypa.io/warnings/venv
| Create complete file
[Run Unit Tests/test]   💬  ::debug::isExplicit: 
[Run Unit Tests/test]   💬  ::debug::explicit? false
[Run Unit Tests/test]   💬  ::debug::isExplicit: 3.8.10
[Run Unit Tests/test]   💬  ::debug::explicit? true
[Run Unit Tests/test]   💬  ::debug::evaluating 1 versions
[Run Unit Tests/test]   💬  ::debug::matched: 3.8.10
[Run Unit Tests/test]   💬  ::debug::checking cache: /opt/hostedtoolcache/Python/3.8.10/x64
[Run Unit Tests/test]   💬  ::debug::Found tool in cache Python 3.8.10 x64
[Run Unit Tests/test]   ⚙  ::set-output:: python-version=3.8.10
| Successfully setup CPython (3.8.10)
[Run Unit Tests/test]   ❓  ##[add-matcher]/mnt/c/Users/chizz/Documents/pillar/pillar_algos/_actions/actions-setup-python@v2/.github/python.json
[Run Unit Tests/test]   ✅  Success - Setup Python 3.8
[Run Unit Tests/test] ⭐  Run Install Dependencies
| Collecting pandas
|   Downloading pandas-1.2.4-cp38-cp38-manylinux1_x86_64.whl (9.7 MB)
     |████████████████████████████████| 9.7 MB 2.9 MB/s
| Collecting numpy
|   Downloading numpy-1.20.3-cp38-cp38-manylinux_2_12_x86_64.manylinux2010_x86_64.whl (15.4 MB)
     |████████████████████████████████| 15.4 MB 62.5 MB/s
| Collecting pre-commit
|   Downloading pre_commit-2.12.1-py2.py3-none-any.whl (189 kB)
     |████████████████████████████████| 189 kB 55.3 MB/s
| Collecting pillaralgos
|   Downloading pillaralgos-1.0.18-py3-none-any.whl (18 kB)
| Collecting python-dateutil>=2.7.3
|   Downloading python_dateutil-2.8.1-py2.py3-none-any.whl (227 kB)
     |████████████████████████████████| 227 kB 37.9 MB/s
| Collecting pytz>=2017.3
|   Downloading pytz-2021.1-py2.py3-none-any.whl (510 kB)
     |████████████████████████████████| 510 kB 54.0 MB/s
| Collecting six>=1.5
|   Downloading six-1.16.0-py2.py3-none-any.whl (11 kB)
| Collecting toml
|   Downloading toml-0.10.2-py2.py3-none-any.whl (16 kB)
| Collecting virtualenv>=20.0.8
|   Downloading virtualenv-20.4.6-py2.py3-none-any.whl (7.2 MB)
     |████████████████████████████████| 7.2 MB 28.6 MB/s
| Collecting identify>=1.0.0
|   Downloading identify-2.2.4-py2.py3-none-any.whl (98 kB)
     |████████████████████████████████| 98 kB 14.4 MB/s
| Collecting nodeenv>=0.11.1
|   Downloading nodeenv-1.6.0-py2.py3-none-any.whl (21 kB)
| Collecting cfgv>=2.0.0
|   Downloading cfgv-3.2.0-py2.py3-none-any.whl (7.3 kB)
| Collecting pyyaml>=5.1
|   Downloading PyYAML-5.4.1-cp38-cp38-manylinux1_x86_64.whl (662 kB)
     |████████████████████████████████| 662 kB 42.5 MB/s
| Collecting filelock<4,>=3.0.0
|   Downloading filelock-3.0.12-py3-none-any.whl (7.6 kB)
| Collecting appdirs<2,>=1.4.3
|   Downloading appdirs-1.4.4-py2.py3-none-any.whl (9.6 kB)
| Collecting distlib<1,>=0.3.1
|   Downloading distlib-0.3.1-py2.py3-none-any.whl (335 kB)
     |████████████████████████████████| 335 kB 48.7 MB/s
| Installing collected packages: six, pytz, python-dateutil, numpy, filelock, distlib, appdirs, virtualenv, toml, pyyaml, pandas, nodeenv, identify, cfgv, pre-commit, pillaralgos
| Successfully installed appdirs-1.4.4 cfgv-3.2.0 distlib-0.3.1 filelock-3.0.12 identify-2.2.4 nodeenv-1.6.0 numpy-1.20.3 pandas-1.2.4 pillaralgos-1.0.18 pre-commit-2.12.1 python-dateutil-2.8.1 pytz-2021.1 pyyaml-5.4.1 six-1.16.0 toml-0.10.2 virtualenv-20.4.6
| WARNING: Running pip as root will break packages and permissions. You should install packages reliably by using venv: https://pip.pypa.io/warnings/venv
| Collecting pytest
|   Downloading pytest-6.2.4-py3-none-any.whl (280 kB)
     |████████████████████████████████| 280 kB 2.8 MB/s
| Collecting py>=1.8.2
|   Downloading py-1.10.0-py2.py3-none-any.whl (97 kB)
     |████████████████████████████████| 97 kB 4.3 MB/s
| Collecting attrs>=19.2.0
|   Downloading attrs-21.2.0-py2.py3-none-any.whl (53 kB)
     |████████████████████████████████| 53 kB 2.6 MB/s
| Requirement already satisfied: toml in /opt/hostedtoolcache/Python/3.8.10/x64/lib/python3.8/site-packages (from pytest) (0.10.2)
| Collecting iniconfig
|   Downloading iniconfig-1.1.1-py2.py3-none-any.whl (5.0 kB)
| Collecting packaging
|   Downloading packaging-20.9-py2.py3-none-any.whl (40 kB)
     |████████████████████████████████| 40 kB 4.0 MB/s
| Collecting pluggy<1.0.0a1,>=0.12
|   Downloading pluggy-0.13.1-py2.py3-none-any.whl (18 kB)
| Collecting pyparsing>=2.0.2
|   Downloading pyparsing-2.4.7-py2.py3-none-any.whl (67 kB)
     |████████████████████████████████| 67 kB 4.0 MB/s
| Installing collected packages: pyparsing, py, pluggy, packaging, iniconfig, attrs, pytest
| Successfully installed attrs-21.2.0 iniconfig-1.1.1 packaging-20.9 pluggy-0.13.1 py-1.10.0 pyparsing-2.4.7 pytest-6.2.4
| WARNING: Running pip as root will break packages and permissions. You should install packages reliably by using venv: https://pip.pypa.io/warnings/venv
[Run Unit Tests/test]   ✅  Success - Install Dependencies
[Run Unit Tests/test] ⭐  Run Run Tests
| ============================= test session starts ==============================
| platform linux -- Python 3.8.10, pytest-6.2.4, py-1.10.0, pluggy-0.13.1
| rootdir: /mnt/c/Users/chizz/Documents/pillar/pillar_algos/prod/test
collected 17 items
| 
| test_algos.py ........                                                   [ 47%]
| test_brain.py ..                                                         [ 58%]
| test_helpers.py .......                                                  [100%]
| 
| ============================== slowest durations ===============================
| 30.90s call     test_algos.py::test_algo2_diffs
| 17.57s call     test_brain.py::test_length
| 17.45s call     test_brain.py::test_brain
| 14.16s call     test_algos.py::test_algo30_diffs
| 11.40s call     test_algos.py::test_algo2
| 9.11s call     test_algos.py::test_algo35_diffs
| 4.88s call     test_algos.py::test_algo3_0
| 4.32s call     test_algos.py::test_algo3_5
| 2.48s call     test_helpers.py::test_emoji_getter
| 2.21s call     test_algos.py::test_algo1_diffs
| 1.49s setup    test_helpers.py::test_emoji_getter
| 0.97s call     test_algos.py::test_algo1
| 0.08s call     test_helpers.py::test_organize_twitch_chat_lg
| 0.08s call     test_helpers.py::test_organize_twitch_chat_dtypes
| 0.08s call     test_helpers.py::test_organize_twitch_chat_cols
| 0.08s setup    test_brain.py::test_brain
| 0.07s setup    test_brain.py::test_length
| 0.06s setup    test_helpers.py::test_organize_twitch_chat_cols
| 0.06s setup    test_helpers.py::test_organize_twitch_chat_dtypes
| 0.06s setup    test_algos.py::test_algo30_diffs
| 0.06s setup    test_algos.py::test_algo2
| 0.06s setup    test_algos.py::test_algo3_5
| 0.05s setup    test_algos.py::test_algo1
| 0.05s setup    test_helpers.py::test_organize_twitch_chat_lg
| 0.05s setup    test_algos.py::test_algo3_0
| 0.04s setup    test_algos.py::test_algo35_diffs
| 0.04s setup    test_algos.py::test_algo1_diffs
| 0.04s setup    test_algos.py::test_algo2_diffs
|
| (23 durations < 0.005s hidden.  Use -vv to show these durations.)
| ======================== 17 passed in 118.31s (0:01:58) ========================
[Run Unit Tests/test]   ✅  Success - Run Tests
```

</details>


## Testing without Containers

You need [Python 3.8]() or newer installed. Run the following in the project directory.

```bash
pip install -r requirement.txt
pip install pytest
cd prod/test
pytest --duration=0 
```

## Usage
```python
from pillaralgos import OPTIONS  # replace options with an algo
OPTIONS.run(data)                # see algo docstring for descriptions
```
