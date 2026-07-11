import pytest

from nhl_api.resources.teams import TeamsResource


@pytest.fixture
def teams(mock_session):
    return TeamsResource(mock_session)


def test_get_info_returns_matching_team(teams, mock_session, example_response):
    mock_session.get_url.return_value = example_response("team_info_list")

    team = teams.get_info(team_id=8)

    assert team["fullName"] == "Montréal Canadiens"
    assert team["triCode"] == "MTL"


def test_get_info_raises_when_team_not_found(teams, mock_session, example_response):
    mock_session.get_url.return_value = example_response("team_info_list")

    with pytest.raises(ValueError, match="Team with id 999999 not found"):
        teams.get_info(team_id=999999)


def test_get_stats_season_game_type(teams, mock_session):
    teams.get_stats(
        team_code="STL", stat_type="season_game_type", season=20232024, game_type="regular"
    )

    mock_session.get_url.assert_called_once_with("/v1/club-stats/STL/20232024/2")


def test_get_stats_season_game_type_playoffs(teams, mock_session):
    teams.get_stats(
        team_code="STL", stat_type="season_game_type", season=20232024, game_type="playoffs"
    )

    mock_session.get_url.assert_called_once_with("/v1/club-stats/STL/20232024/3")


def test_get_stats_season_game_type_requires_season_and_game_type(teams):
    with pytest.raises(ValueError, match="season and game_type required"):
        teams.get_stats(team_code="STL", stat_type="season_game_type")


def test_get_stats_by_season(teams, mock_session):
    teams.get_stats(team_code="STL", stat_type="by_season")

    mock_session.get_url.assert_called_once_with("/v1/club-stats-season/STL")


def test_get_stats_now(teams, mock_session):
    teams.get_stats(team_code="STL", stat_type="now")

    mock_session.get_url.assert_called_once_with("/v1/club-stats/STL/now")


def test_get_stats_invalid_stat_type_raises(teams):
    with pytest.raises(ValueError, match="Invalid stat_type: bogus"):
        teams.get_stats(team_code="STL", stat_type="bogus")


def test_get_scoreboard(teams, mock_session):
    teams.get_scoreboard(team_code="STL")

    mock_session.get_url.assert_called_once_with("/v1/scoreboard/STL/now")


def test_get_schedule_season_now(teams, mock_session):
    teams.get_schedule(team_code="STL")

    mock_session.get_url.assert_called_once_with("/v1/club-schedule-season/STL/now")


def test_get_schedule_season_with_period(teams, mock_session):
    teams.get_schedule(team_code="STL", schedule_type="season", time="season", period="20232024")

    mock_session.get_url.assert_called_once_with("/v1/club-schedule-season/STL/20232024")


def test_get_schedule_invalid_schedule_type_raises(teams):
    with pytest.raises(ValueError, match="schedule_type must be"):
        teams.get_schedule(team_code="STL", schedule_type="bogus")
