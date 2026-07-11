import datetime

import pandas as pd
import pytest

from moneypuck import moneypuck


@pytest.fixture(autouse=True)
def mock_read_csv(mocker):
    """Every test in this file must be network-free."""
    return mocker.patch.object(pd, "read_csv", return_value=pd.DataFrame({"col": [1]}))


def test_explicit_season_builds_url(mock_read_csv):
    moneypuck.get_moneypuck_data(season="20222023", save=False)

    mock_read_csv.assert_called_once_with(
        "https://moneypuck.com/moneypuck/playerData/seasons/20222023/20222023_skaters.csv"
    )


def test_default_season_after_september(mocker, mock_read_csv):
    fake_now = datetime.datetime(2023, 10, 15)
    mocker.patch("datetime.datetime", mocker.Mock(now=mocker.Mock(return_value=fake_now)))

    moneypuck.get_moneypuck_data(save=False)

    mock_read_csv.assert_called_once_with(
        "https://moneypuck.com/moneypuck/playerData/seasons/20232024/20232024_skaters.csv"
    )


def test_default_season_before_september(mocker, mock_read_csv):
    fake_now = datetime.datetime(2024, 3, 1)
    mocker.patch("datetime.datetime", mocker.Mock(now=mocker.Mock(return_value=fake_now)))

    moneypuck.get_moneypuck_data(save=False)

    mock_read_csv.assert_called_once_with(
        "https://moneypuck.com/moneypuck/playerData/seasons/20232024/20232024_skaters.csv"
    )


def test_save_false_does_not_touch_disk(mocker, mock_read_csv):
    mkdir = mocker.patch("pathlib.Path.mkdir")
    to_csv = mocker.patch.object(pd.DataFrame, "to_csv")

    moneypuck.get_moneypuck_data(season="20222023", save=False)

    mkdir.assert_not_called()
    to_csv.assert_not_called()


def test_save_true_writes_via_mocked_filesystem(mocker, mock_read_csv):
    mkdir = mocker.patch("pathlib.Path.mkdir")
    to_csv = mocker.patch.object(pd.DataFrame, "to_csv")

    result = moneypuck.get_moneypuck_data(season="20222023", save=True)

    mkdir.assert_called_once_with(parents=True, exist_ok=True)
    to_csv.assert_called_once()
    assert result is not None
