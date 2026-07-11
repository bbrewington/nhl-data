import pytest

from nhl_api.resources.league import LeagueResource


@pytest.fixture
def league(mock_session):
    return LeagueResource(mock_session)


def test_get_schedule_calendar_builds_endpoint(league, mock_session):
    league.get_schedule_calendar("2023-10-10")

    mock_session.get_url.assert_called_once_with("/v1/schedule-calendar/2023-10-10")


def test_get_schedule_calendar_rejects_dates_before_nhl_founding(league):
    with pytest.raises(ValueError, match="date must be >= 1916-12-19"):
        league.get_schedule_calendar("1900-01-01")


def test_list_season_ids(league, mock_session):
    league.list_season_ids()

    mock_session.get_url.assert_called_once_with("/v1/season")


def test_get_standings_season_info(league, mock_session):
    league.get_standings(season_info=True)

    mock_session.get_url.assert_called_once_with("/v1/standings-season")


def test_get_standings_specific_date(league, mock_session):
    league.get_standings(date="2023-11-01")

    mock_session.get_url.assert_called_once_with("/v1/standings/2023-11-01")


def test_get_standings_now(league, mock_session):
    league.get_standings()

    mock_session.get_url.assert_called_once_with("/v1/standings/now")


def test_list_team_info_uses_stats_base_url(league, mock_session):
    league.list_team_info(lang="fr")

    mock_session.get_url.assert_called_once_with("/fr/team", base_url_type="stats")


def test_list_games_uses_stats_base_url(league, mock_session):
    league.list_games()

    mock_session.get_url.assert_called_once_with("/en/game", base_url_type="stats")


def test_get_glossary_uses_stats_base_url(league, mock_session):
    league.get_glossary()

    mock_session.get_url.assert_called_once_with("/en/glossary", base_url_type="stats")
