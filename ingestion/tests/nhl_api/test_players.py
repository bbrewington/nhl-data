import pytest

from nhl_api.resources.players import PlayersResource


@pytest.fixture
def players(mock_session):
    return PlayersResource(mock_session)


def test_get(players, mock_session):
    players.get(player_id=8478402)

    mock_session.get_url.assert_called_once_with("/v1/player/8478402/landing")


def test_get_game_log(players, mock_session):
    players.get_game_log(player_id=8478402, season_id=20232024, game_type="regular")

    mock_session.get_url.assert_called_once_with("/v1/player/8478402/game-log/20232024/2")


def test_get_game_log_playoffs(players, mock_session):
    players.get_game_log(player_id=8478402, season_id=20232024, game_type="playoffs")

    mock_session.get_url.assert_called_once_with("/v1/player/8478402/game-log/20232024/3")


def test_get_game_log_invalid_game_type_raises(players):
    with pytest.raises(ValueError, match="game_type must be 'regular' or 'playoffs'"):
        players.get_game_log(player_id=8478402, season_id=20232024, game_type="bogus")


def test_get_game_log_invalid_season_id_raises(players):
    with pytest.raises(ValueError, match="season_id must be YYYYYYYY format"):
        players.get_game_log(player_id=8478402, season_id=2023, game_type="regular")


def test_get_game_log_current(players, mock_session):
    players.get_game_log_current(player_id=8478402)

    mock_session.get_url.assert_called_once_with("/v1/player/8478402/game-log/now")


def test_get_stats_leaders_current_no_filters(players, mock_session):
    players.get_stats_leaders(player_type="skater")

    mock_session.get_url.assert_called_once_with("/v1/skater-stats-leaders/current", params={})


def test_get_stats_leaders_with_season_and_game_type(players, mock_session):
    players.get_stats_leaders(player_type="goalie", season=20232024, game_type="regular")

    mock_session.get_url.assert_called_once_with(
        "/v1/goalie-stats-leaders/20232024/2", params={}
    )


def test_get_stats_leaders_with_categories_and_limit(players, mock_session):
    players.get_stats_leaders(player_type="skater", categories="goals", limit=10)

    mock_session.get_url.assert_called_once_with(
        "/v1/skater-stats-leaders/current", params={"categories": "goals", "limit": 10}
    )


def test_get_stats_leaders_invalid_player_type_raises(players):
    with pytest.raises(ValueError, match="player_type must be 'skater' or 'goalie'"):
        players.get_stats_leaders(player_type="bogus")


def test_get_spotlight(players, mock_session):
    players.get_spotlight()

    mock_session.get_url.assert_called_once_with("/v1/player-spotlight")
