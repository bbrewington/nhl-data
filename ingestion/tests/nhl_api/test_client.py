from nhl_api.client import NHLClient
from nhl_api.resources.league import LeagueResource
from nhl_api.resources.teams import TeamsResource
from nhl_api.resources.players import PlayersResource
from nhl_api.resources.games import GamesResource


def test_client_wires_resource_types():
    client = NHLClient()

    assert isinstance(client.league, LeagueResource)
    assert isinstance(client.teams, TeamsResource)
    assert isinstance(client.players, PlayersResource)
    assert isinstance(client.games, GamesResource)


def test_client_resources_share_one_session():
    client = NHLClient()

    assert client.league.session is client.session
    assert client.teams.session is client.session
    assert client.players.session is client.session
    assert client.games.session is client.session


def test_context_manager_closes_session(mocker):
    client = NHLClient()
    close = mocker.patch.object(client.session, "close")

    with client as c:
        assert c is client

    close.assert_called_once()
