import pytest
import requests

from nhl_api.session import NHLSession


@pytest.fixture
def session():
    return NHLSession()


def _mock_response(mocker, json_data=None, text_data=None, status_code=200):
    response = mocker.Mock()
    response.json.return_value = json_data
    response.text = text_data
    response.raise_for_status.return_value = None
    if status_code >= 400:
        response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=response)
    return response


def test_get_url_default_base_url(session, mocker):
    response = _mock_response(mocker, json_data={"ok": True})
    get = mocker.patch.object(requests.Session, "get", return_value=response)

    session.get_url("/v1/season")

    get.assert_called_once_with("http://api-web.nhle.com/v1/season", params=None)


def test_get_url_stats_base_url(session, mocker):
    response = _mock_response(mocker, json_data={"ok": True})
    get = mocker.patch.object(requests.Session, "get", return_value=response)

    session.get_url("/en/team", base_url_type="stats")

    get.assert_called_once_with("https://api.nhle.com/stats/rest/en/team", params=None)


def test_get_url_invalid_base_url_type_raises(session):
    with pytest.raises(ValueError, match="base_url_type must be one of"):
        session.get_url("/v1/season", base_url_type="bogus")


def test_get_url_response_type_json(session, mocker):
    response = _mock_response(mocker, json_data={"a": 1})
    mocker.patch.object(requests.Session, "get", return_value=response)

    assert session.get_url("/v1/season") == {"a": 1}


def test_get_url_response_type_text(session, mocker):
    response = _mock_response(mocker, text_data="raw text")
    mocker.patch.object(requests.Session, "get", return_value=response)

    assert session.get_url("/v1/season", response_type="text") == "raw text"


def test_get_url_invalid_response_type_raises(session, mocker):
    response = _mock_response(mocker, json_data={"a": 1})
    mocker.patch.object(requests.Session, "get", return_value=response)

    with pytest.raises(ValueError, match="response_type must be 'json' or 'text'"):
        session.get_url("/v1/season", response_type="xml")


def test_get_url_params_passthrough(session, mocker):
    response = _mock_response(mocker, json_data={})
    get = mocker.patch.object(requests.Session, "get", return_value=response)

    session.get_url("/v1/skater-stats-leaders/current", params={"limit": 10})

    get.assert_called_once_with(
        "http://api-web.nhle.com/v1/skater-stats-leaders/current", params={"limit": 10}
    )


def test_get_url_http_error_raises_system_exit(session, mocker):
    response = _mock_response(mocker, status_code=404)
    mocker.patch.object(requests.Session, "get", return_value=response)

    with pytest.raises(SystemExit):
        session.get_url("/v1/does-not-exist")
