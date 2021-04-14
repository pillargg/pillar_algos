"""
Runs tests on the `helper` scripts in the helper folder, but first navigates to correct dirs
[Navigation source](https://towardsdatascience.com/pytest-for-data-scientists-2990319e55e6)
"""
import os.path  # get dir path
import sys  # append dir path to sys.path
import json  # load sample data
import pytest  # test
import pandas.api.types as ptypes  # to check dataframe dtypes assertions
import pandas as pd
import numpy as np


#### Grab Directory Locations ####
cd = os.path.pardir  # go back one dir
current_dir = os.path.dirname(__file__)  # get dir of current filename
prod_dir = os.path.join(current_dir, cd)  # join it with cd to go to parent
pill_dir = os.path.join(prod_dir, "pillaralgos")  # join parent with pillaralgos folder
algos_path = os.path.abspath(pill_dir)  # get the absolute path

base_dir = os.path.join(prod_dir, cd, cd)
data_folder = "sample_data"  # location of sample data

#### Append Algos Dir to Sys.path ####
sys.path.append(algos_path)  # append the path to sys.path

#### Testing Area ####
from helpers import data_handler as dh  # from pillaralgos folder
from helpers import emoji_getter as eg

###############################################################################


@pytest.fixture()
def empty_file():
    "load raw empty file"
    data = json.load(open(f"{data_folder}/sample_nan.json"))
    return data


@pytest.fixture()
def med_file():
    "load raw med sized file"
    data = json.load(open(f"{data_folder}/sample_med.json"))
    return data


@pytest.fixture()
def lg_file():
    "load raw large sized file"
    data = json.load(open(f"{data_folder}/sample_lg.json"))
    return data


@pytest.fixture()
def med_file_results_df():
    "load sample results df, (vars created from sample_med.json and algo1)"
    results_df = pd.read_csv(f"{data_folder}/sample_med_resultsdf.csv")
    results_df = results_df.astype(
        {"start": "datetime64[ns]", "end": "datetime64[ns]", "perc_rel_unique": float}
    )
    return results_df


@pytest.fixture()
def med_file_results_json():
    "load a sample list of dictionaries"
    json_results = [
        {"startTime": 25874.858, "endTime": 25994.723},
        {"startTime": 25630.013, "endTime": 25749.664},
        {"startTime": 25753.034, "endTime": 25870.105},
        {"startTime": 12177.737, "endTime": 12293.058},
        {"startTime": 26005.689, "endTime": 26046.392},
    ]
    return json_results


def test_organize_twitch_chat_empty(empty_file):
    "Checks the organizer gets right output"
    data = dh.organize_twitch_chat(empty_file)
    assert data.size == 0


def test_organize_twitch_chat_lg(med_file):
    "Checks the organizer gets right output"
    data = dh.organize_twitch_chat(med_file)
    assert type(data) == pd.DataFrame


def test_organize_twitch_chat_cols(med_file):
    "Checks basic cols are in the returned df"
    data = dh.organize_twitch_chat(med_file)
    needed_cols = ["created_at", "updated_at", "body", "emoticons", "is_action", "type"]
    assert all(col in data.columns for col in needed_cols)


def test_organize_twitch_chat_dtypes(med_file):
    "Checks the basic cols are right dtype"
    data = dh.organize_twitch_chat(med_file)
    time_cols = ["created_at", "updated_at"]
    obj_cols = ["body", "emoticons"]

    assert all(ptypes.is_datetime64_any_dtype(data[col]) for col in time_cols)
    assert ptypes.is_bool_dtype(data["is_action"])
    assert ptypes.is_integer_dtype(data["_id"])
    assert all(ptypes.is_object_dtype(data[col]) for col in obj_cols)


def test_results_jsonified(med_file_results_df, med_file_results_json):
    'Compares calculated json from "sample_med_resultsdf.csv" to stored results'
    col = "perc_rel_unique"
    # "Unnamed: 0" is the original index. Find first sec by sorting by it.
    first_sec = med_file_results_df.sort_values("Unnamed: 0").iloc[0, 1]
    calc_json = dh.results_jsonified(med_file_results_df.head(), first_sec, col)
    assert calc_json == med_file_results_json


def test_chunker():
    "future site of testing minute chunker and hour splitter"


def test_emoji_getter(lg_file):
    ee = eg.emoticonExtractor(data=lg_file, min_use="mean", limit=None)
    calc_result = ee.run()
    calc_result = calc_result.head(10).astype(
        {
            "vid_id": int,
            "emoji_id": int,
            "occurrance": int,
        }
    )
    answer = {
        "vid_id": [
            964075925,
            964075925,
            964075925,
            964075925,
            964075925,
            964075925,
            964075925,
            964075925,
            964075925,
            964075925,
        ],
        "emoji_id": [114836, 425618, 555555584, 27509, 41, 34, 33, 1, 25, 28087],
        "occurrance": [7709, 5541, 3106, 2163, 1826, 1602, 1229, 1140, 1130, 1046],
        "emoji_name": [
            "Jebaited",
            "LUL",
            "<3",
            "PermaSmug",
            "Kreygasm",
            "SwiftRage",
            "DansGame",
            ":)",
            "Kappa",
            "WutFace",
        ],
        "label": ["", "", "", "", "", "", "", "", "", ""],
    }
    answer = pd.DataFrame(answer)

    for col in answer:
        assert all(calc_result[col] == answer[col])
