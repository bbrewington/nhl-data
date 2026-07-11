import json
from pathlib import Path

import pytest

EXAMPLES = Path(__file__).parents[1] / "src/nhl_api/example_responses"


@pytest.fixture
def example_response():
    """Load a captured NHL API response, unwrapped to the actual response body.

    Files under example_responses/ are {"metadata": {...}, "data": <actual body>},
    produced by scripts/nhl_api/collect_responses.py. get_url() itself returns
    only the body, so callers get that shape here too.
    """

    def _load(name: str):
        return json.loads((EXAMPLES / f"{name}.json").read_text())["data"]

    return _load


@pytest.fixture
def mock_session(mocker):
    return mocker.Mock()
