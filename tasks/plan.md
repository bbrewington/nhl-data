# Implementation Plan: Ingestion Test Suite

Spec: [docs/features/ingestion_test_suite.md](../docs/features/ingestion_test_suite.md)

## Overview

Add a pytest suite to `ingestion/`, currently at zero coverage. All tests mock at the `NHLSession.get_url` / `requests` / `boto3` boundary — no live network or credentials required. NHL API resource tests reuse the JSON files already captured in `src/nhl_api/example_responses/`. `tests/` mirrors `src/` 1:1.

## Architecture Decisions

- **Mock at `NHLSession.get_url`, not `requests`** for resource-layer tests (`league`/`teams`/`players`/`games`) — that's the actual seam `BaseResource._get` uses, so tests don't need to know about HTTP internals. `NHLSession.get_url` itself gets tested once, directly, with `requests` mocked underneath it.
- **`tests/conftest.py` is a dependency of every other test file** — it provides the `example_response` fixture (loads `src/nhl_api/example_responses/*.json`) and a `mock_session` fixture (a `Mock()` standing in for `NHLSession`). Built first, nothing else can be verified without it.
- **`moneypuck` and `utility/aws` are independent of the `nhl_api` work** — different mocking targets (`requests.get`/`pandas` and `boto3` respectively), no shared fixtures. Safe to build in either order relative to the `nhl_api` slice, or in parallel.
- **`pyproject.toml` changes (deps + markers) land in the same task as `conftest.py`** — a `conftest.py` that can't run because `pytest`/`pytest-mock` aren't installed isn't verifiable, so they're one task, not two.

## Task List

### Phase 1: Foundation

- [x] Task 1: Add pytest deps and markers, create conftest.py fixtures

### Checkpoint: Foundation
- [x] `cd ingestion && uv run pytest` runs (0 tests collected, exits 0) with no network access
- [x] `example_response` fixture successfully loads a known file (spot-check in a throwaway test, removed before moving on)

### Phase 2: nhl_api layer

- [x] Task 2: `tests/nhl_api/test_session.py` — `NHLSession.get_url`
- [x] Task 3: `tests/nhl_api/test_client.py` — `NHLClient` wiring
- [x] Task 4: `tests/nhl_api/test_league.py` — `LeagueResource`
- [x] Task 5: `tests/nhl_api/test_teams.py` — `TeamsResource`
- [x] Task 6: `tests/nhl_api/test_players.py` — `PlayersResource`
- [x] Task 7: `tests/nhl_api/test_games.py` — `GamesResource`

### Checkpoint: nhl_api layer
- [x] `uv run pytest tests/nhl_api/ -v` — all green
- [x] Every public method across `resources/{league,teams,players,games}.py` has at least one test

### Phase 3: moneypuck and utility (parallelizable with each other, and could have started alongside Phase 2)

- [x] Task 8: `tests/moneypuck/test_moneypuck.py`
- [x] Task 9: `tests/utility/test_aws.py`

### Checkpoint: Complete
- [x] `cd ingestion && uv run pytest` — full suite green, zero network calls, works with no `.env` present
- [x] `uv run pytest -m unit` and `uv run pytest -m "not slow"` both run without marker warnings
- [x] Every item in the spec's Success Criteria is met
- [x] `CLAUDE.md` Tests section restored (per spec) — accurate this time
- [x] Ready for human review

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| `example_responses/*.json` shapes don't match what today's live API actually returns (unofficial, unversioned API) | Med | Tests validate against the captured fixture, not live truth — acceptable per spec; note in test docstrings that fixtures may drift from live API |
| `moneypuck.py`'s `get_moneypuck_data` does real I/O (`MONEYPUCK_RAW_DIR.mkdir(...)`, `df.to_csv(...)`) when `save=True` | Med | Test with `save=False` for URL/season logic, or mock `Path.mkdir`/`DataFrame.to_csv` if `save=True` path needs covering — decide in Task 8, don't let it write to real disk |
| `utility/aws.py` calls `load_dotenv("../.env")` and `boto3.client('s3')` at **import time**, not inside a function | High | Import-time `boto3.client('s3')` needs a valid (even if fake) AWS region/credentials setup in the test env, or `moto`/env-var stubbing before import — must resolve in Task 9 before writing assertions, since a naive mock-after-import won't intercept it |
| `NHLSession.get_url`'s `except requests.exceptions.HTTPError` raises `SystemExit(err)` | Low | `pytest.raises(SystemExit)` in Task 2; note this in the task so it isn't mistaken for a hang/crash |

## Open Questions

- None blocking. The `utility/aws.py` import-time `boto3.client()` risk (above) needs a concrete decision at Task 9 time — flagged now so it doesn't get discovered mid-task.
