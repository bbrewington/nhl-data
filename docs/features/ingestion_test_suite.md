# Spec: Ingestion Test Suite

## Objective

`ingestion/` has zero test coverage — no `tests/` directory, no `pytest` dependency, no markers. The `python/` → `ingestion/` rename (commit `10ce487`) dropped the test suite that used to exist under `python/tests/` and never carried it forward. This spec adds a real, current test suite covering the business logic in `ingestion/src/`.

**Success looks like:** a contributor can change endpoint-building logic, column renaming, or upload logic in `ingestion/src/` and get a fast, deterministic pass/fail signal without hitting the live NHL API, MoneyPuck, or AWS.

## Tech Stack

- `pytest` (new dev dependency)
- `pytest-mock` or stdlib `unittest.mock` for mocking `NHLSession.get_url`, `requests`, and `boto3`
- No new HTTP-recording dependency (e.g. `vcrpy`) — rejected in favor of the fixtures already in `ingestion/src/nhl_api/example_responses/*.json`

## Commands

```bash
cd ingestion
uv add --dev pytest pytest-mock       # one-time setup
uv run pytest                         # all tests
uv run pytest -m unit                 # unit tests only
uv run pytest -m "not slow"           # skip slow tests
uv run pytest tests/nhl_api/test_teams.py -v   # single file
```

## Project Structure

```
ingestion/
  tests/
    conftest.py              → shared fixtures (mock session, loaded example_responses/*.json)
    nhl_api/
      test_client.py         → NHLClient construction, context manager, resource wiring
      test_session.py        → NHLSession.get_url: base_url_type switching, params, backoff-on-timeout
      test_league.py         → LeagueResource
      test_teams.py          → TeamsResource (endpoint construction, ValueError branches, get_info team-not-found)
      test_players.py        → PlayersResource
      test_games.py          → GamesResource
    moneypuck/
      test_moneypuck.py      → get_moneypuck_data: URL construction, season defaulting, save-to-csv path
    utility/
      test_aws.py            → upload_file_to_s3, run_s3_upload_fileext (mocked boto3 client)
```

Mirrors `ingestion/src/` package layout 1:1 so a source file's test is always found at the same relative path under `tests/`.

## Code Style

Mock at the `NHLSession.get_url` boundary (not `requests` directly) for resource tests — it's the actual seam the codebase already uses (`BaseResource._get` → `self.session.get_url`), so tests don't need to know about HTTP internals:

```python
# tests/nhl_api/test_teams.py
import pytest
from nhl_api.resources.teams import TeamsResource

@pytest.fixture
def teams(mocker):
    session = mocker.Mock()
    return TeamsResource(session), session

def test_get_stats_season_game_type_builds_correct_endpoint(teams):
    resource, session = teams
    resource.get_stats(team_code="STL", stat_type="season_game_type", season=20232024, game_type="regular")
    session.get_url.assert_called_once_with("/v1/club-stats/STL/20232024/2")

def test_get_stats_invalid_stat_type_raises(teams):
    resource, session = teams
    with pytest.raises(ValueError, match="Invalid stat_type"):
        resource.get_stats(team_code="STL", stat_type="bogus")
```

For tests needing realistic response *shapes* (e.g. `TeamsResource.get_info` filtering `league.list_team_info()['data']`), load the matching file from `ingestion/src/nhl_api/example_responses/` via a `conftest.py` fixture rather than hand-writing fake JSON:

```python
# tests/conftest.py
import json
from pathlib import Path
import pytest

EXAMPLES = Path(__file__).parents[1] / "src/nhl_api/example_responses"

@pytest.fixture
def example_response():
    def _load(name: str):
        return json.loads((EXAMPLES / f"{name}.json").read_text())
    return _load
```

## Testing Strategy

- **Framework:** `pytest`, markers registered in `ingestion/pyproject.toml` under `[tool.pytest.ini_options]` (`unit`, `slow` — no `integration` marker yet, see below)
- **No live network/credentials in any test.** `NHLSession.get_url`, `requests.get` (in `moneypuck.py`), and `boto3.client('s3')` (in `utility/aws.py`) are always mocked. CI must be able to run the full suite with zero external access.
- **Fixtures over hand-written JSON:** prefer `ingestion/src/nhl_api/example_responses/*.json` for response bodies; only hand-write minimal JSON when no example file covers the shape needed.
- **Coverage focus:** endpoint/URL construction, `ValueError` branches on bad input, response parsing/filtering (e.g. `TeamsResource.get_info`), column renaming and season-defaulting logic in `moneypuck.py`, and `upload_file_to_s3`/`run_s3_upload_fileext` logic in `utility/aws.py` (glob, dest-path construction, empty-dir assertion). Not aiming for a numeric coverage target — aiming to cover every branch that isn't a bare pass-through to `requests`/`boto3`.
- **No `integration` marker or live-API tests in this pass.** If/when needed later, add a `pytest -m integration` marker gated on real credentials, skipped by default — out of scope for this spec.

## Boundaries

- **Always do:** mock all network/AWS calls; register new pytest markers in `pyproject.toml` (not a separate `pytest.ini`, keeping config in one file per existing convention); mirror `src/` layout under `tests/`
- **Ask first:** adding any new runtime (non-dev) dependency; changing `NHLSession`/`BaseResource` production code to make it more testable (e.g. dependency injection changes) — flag the seam, don't silently refactor around it
- **Never do:** write a test that requires `AWS_ACCESS_KEY_ID`/`MOTHERDUCK_TOKEN`/live network to pass; add `vcrpy` or other HTTP-recording deps without discussing first; touch `dbt/` (separate test mechanism, `dbt test`)

## Follow-ups (explicitly out of scope here)

- **Pydantic response models** for `nhl_api/resources/*.py` — would catch upstream field-shape drift automatically instead of only via a docstring comment, but means modeling 30+ endpoint response shapes against an unofficial, unversioned API. Worth its own spec, not bundled into test infrastructure work.
- **`pydantic-settings` for `moneypuck/config/settings.py`** — currently a bag of module-level `os.environ.get()` calls with no validation. Also worth its own spec.

## Success Criteria

- `cd ingestion && uv run pytest` passes with zero network/AWS access, in an environment with no `.env` file present
- Every public method in `nhl_api/resources/{league,teams,players,games}.py` has at least one test exercising its happy path and, where present, its `ValueError` branches
- `moneypuck.get_moneypuck_data` and both functions in `utility/aws.py` have test coverage
- `pyproject.toml` has `pytest` + `pytest-mock` as dev dependencies and a `[tool.pytest.ini_options]` markers block for `unit`/`slow`
- `CLAUDE.md` gets a Tests section re-added once this lands (removed earlier this session because it had gone stale — should be restored, accurately, as part of this work)

## Open Questions

- None blocking — resolved during spec review: tests mock at the `get_url`/`requests`/`boto3` boundary and reuse existing `example_responses/*.json` fixtures; no live-integration marker in this first pass.
