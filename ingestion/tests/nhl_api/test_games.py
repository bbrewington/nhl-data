import pytest

from nhl_api.resources.games import GamesResource


@pytest.fixture
def games(mock_session):
    return GamesResource(mock_session)


def test_get_play_by_play(games, mock_session):
    games.get_play_by_play(game_id=2023020204)

    mock_session.get_url.assert_called_once_with("/v1/gamecenter/2023020204/play-by-play")


def test_get_landing(games, mock_session):
    games.get_landing(game_id=2023020204)

    mock_session.get_url.assert_called_once_with("/v1/gamecenter/2023020204/landing")


def test_get_boxscore(games, mock_session):
    games.get_boxscore(game_id=2023020204)

    mock_session.get_url.assert_called_once_with("/v1/gamecenter/2023020204/boxscore")


def test_get_info(games, mock_session):
    games.get_info(game_id=2023020204)

    mock_session.get_url.assert_called_once_with("/v1/meta/game/2023020204")


def test_get_shift_charts_uses_stats_base_url(games, mock_session):
    games.get_shift_charts(game_id=2023020204)

    mock_session.get_url.assert_called_once_with(
        "/en/shiftcharts?cayenneExp=gameId=2023020204", base_url_type="stats"
    )
