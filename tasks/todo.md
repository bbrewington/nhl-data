# Tasks: Ingestion Test Suite

Plan: [tasks/plan.md](plan.md) · Spec: [docs/features/ingestion_test_suite.md](../docs/features/ingestion_test_suite.md)

## Task 1: Add pytest deps and markers, create conftest.py fixtures

**Description:** Add `pytest` and `pytest-mock` as dev dependencies in `ingestion/pyproject.toml`, register `unit`/`slow` markers under `[tool.pytest.ini_options]`, create the `tests/` directory with `conftest.py` providing an `example_response` fixture (loads JSON from `src/nhl_api/example_responses/`) and a `mock_session` fixture (`Mock()` standing in for `NHLSession`).

**Acceptance criteria:**
- [x] `uv run pytest --markers` lists `unit` and `slow` with no "unknown marker" warnings anywhere else in the run
- [x] `example_response("team_info_list")` returns the parsed contents of `src/nhl_api/example_responses/team_info_list.json`
- [x] `mock_session` fixture yields a `Mock()` with a `get_url` attribute usable via `mock_session.get_url.assert_called_once_with(...)`

**Verification:**
- [x] `cd ingestion && uv run pytest` — collects 0 tests, exits 0, no errors
- [x] Temporarily add one throwaway test asserting `example_response("player_8478402_mcdavid")["playerId"] == 8478402` (or similar), confirm it passes, then delete it before committing

**Dependencies:** None

**Files likely touched:**
- `ingestion/pyproject.toml`
- `ingestion/tests/conftest.py`

**Estimated scope:** Small: 1-2 files

---

## Task 2: `tests/nhl_api/test_session.py`

**Description:** Test `NHLSession.get_url` directly (not through a resource) with `requests.Session.get` mocked. Cover both `base_url_type` values, `response_type='json'` vs `'text'`, `params` passthrough, the `ValueError` on bad `base_url_type`/`response_type`, and the `SystemExit` raised on `HTTPError`.

**Acceptance criteria:**
- [x] `base_url_type='default'` hits `http://api-web.nhle.com` + endpoint; `base_url_type='stats'` hits `https://api.nhle.com/stats/rest` + endpoint
- [x] Invalid `base_url_type` raises `ValueError`; invalid `response_type` raises `ValueError`
- [x] An `HTTPError` from the mocked response's `raise_for_status()` results in `pytest.raises(SystemExit)`
- [x] `params` dict is passed through to the underlying `requests` call

**Verification:**
- [x] `uv run pytest tests/nhl_api/test_session.py -v` — all green

**Dependencies:** Task 1

**Files likely touched:**
- `ingestion/tests/nhl_api/test_session.py`

**Estimated scope:** Small: 1 file

---

## Task 3: `tests/nhl_api/test_client.py`

**Description:** Test `NHLClient.__init__` wires up `.league`/`.teams`/`.players`/`.games` as the correct resource types sharing one `NHLSession`, and that the context manager (`__enter__`/`__exit__`) calls `close()` on the session.

**Acceptance criteria:**
- [x] `NHLClient().league` is a `LeagueResource` (same for teams/players/games)
- [x] All four resources share the same `session` instance
- [x] `with NHLClient() as client:` calls `session.close()` on exit

**Verification:**
- [x] `uv run pytest tests/nhl_api/test_client.py -v` — all green

**Dependencies:** Task 1

**Files likely touched:**
- `ingestion/tests/nhl_api/test_client.py`

**Estimated scope:** Small: 1 file

---

## Task 4: `tests/nhl_api/test_league.py`

**Description:** Test `LeagueResource`'s five methods using `mock_session`: `get_schedule_calendar` (including the `date < "1916-12-19"` `ValueError`), `list_season_ids`, `get_standings` (all three branches: `season_info`, `date`, neither), `list_team_info`, `list_games`, `get_glossary`.

**Acceptance criteria:**
- [x] Each method's endpoint string is asserted exactly via `mock_session.get_url.assert_called_once_with(...)`
- [x] `get_schedule_calendar`'s `ValueError` branch is covered
- [x] `get_standings`'s three branches each produce the right endpoint

**Verification:**
- [x] `uv run pytest tests/nhl_api/test_league.py -v` — all green

**Dependencies:** Task 1

**Files likely touched:**
- `ingestion/tests/nhl_api/test_league.py`

**Estimated scope:** Small: 1 file

---

## Task 5: `tests/nhl_api/test_teams.py`

**Description:** Test `TeamsResource`. `get_info` is the interesting one — it internally constructs its own `LeagueResource(self.session)` and filters `list_team_info()['data']`, so use the `example_response("team_info_list")` fixture as the mocked return value and cover both the found and "not found" (`ValueError`) paths. Cover `get_stats`'s three `stat_type` branches plus its `ValueError`s, `get_scoreboard`, and `get_schedule`'s branches plus its `ValueError`.

**Acceptance criteria:**
- [x] `get_info` returns the matching team dict from the fixture when the id exists
- [x] `get_info` raises `ValueError` when the id doesn't exist in the fixture
- [x] `get_stats` covers `season_game_type` (incl. missing-args `ValueError`), `by_season`, `now`, and invalid `stat_type`
- [x] `get_schedule` covers `schedule_type` branches and its `ValueError`

**Verification:**
- [x] `uv run pytest tests/nhl_api/test_teams.py -v` — all green

**Dependencies:** Task 1 (needs `example_response` fixture and `team_info_list.json`)

**Files likely touched:**
- `ingestion/tests/nhl_api/test_teams.py`

**Estimated scope:** Small: 1 file

---

## Task 6: `tests/nhl_api/test_players.py`

**Description:** Test `PlayersResource`: `get`, `get_game_log` (both `ValueError`s — bad `game_type`, bad `season_id` format), `get_game_log_current`, `get_stats_leaders` (both `player_type` values, with/without `season`+`game_type`, with/without `categories`/`limit`, and its `ValueError`), `get_spotlight`.

**Acceptance criteria:**
- [x] `get_game_log`'s two `ValueError` branches are both covered
- [x] `get_stats_leaders` endpoint construction is verified for all four combinations of (season/game_type present or not) × (categories/limit present or not)
- [x] `get_stats_leaders` invalid `player_type` raises `ValueError`

**Verification:**
- [x] `uv run pytest tests/nhl_api/test_players.py -v` — all green

**Dependencies:** Task 1

**Files likely touched:**
- `ingestion/tests/nhl_api/test_players.py`

**Estimated scope:** Small: 1 file

---

## Task 7: `tests/nhl_api/test_games.py`

**Description:** Test `GamesResource`'s five methods: `get_play_by_play`, `get_landing`, `get_boxscore`, `get_info`, `get_shift_charts` (note: uses `base_url_type='stats'` and a query-string-style endpoint, not a path segment).

**Acceptance criteria:**
- [x] All five methods' endpoint strings asserted exactly
- [x] `get_shift_charts` asserted with `base_url_type='stats'`

**Verification:**
- [x] `uv run pytest tests/nhl_api/test_games.py -v` — all green

**Dependencies:** Task 1

**Files likely touched:**
- `ingestion/tests/nhl_api/test_games.py`

**Estimated scope:** Small: 1 file

---

## Task 8: `tests/moneypuck/test_moneypuck.py`

**Description:** Test `get_moneypuck_data`: URL construction from `season`, the current-season default logic (mock `datetime.datetime.now()` for both the `month >= 9` and `month < 9` branches), and that `save=False` skips the file-write path entirely (verify no `Path.mkdir`/`to_csv` calls). Mock `pandas.read_csv` so no network call happens. Per the plan's risk note: do **not** let `save=True` write to real disk — mock `Path.mkdir` and `DataFrame.to_csv` if that path needs covering, or scope this task to `save=False` only and note the gap.

**Acceptance criteria:**
- [x] URL is built as `.../seasons/{season}/{season}_skaters.csv` for an explicit `season`
- [x] Season defaulting picks `{year}{year+1}` for month >= 9 and `{year-1}{year}` for month < 9
- [x] No real HTTP call and no real file write occurs anywhere in this test file

**Verification:**
- [x] `uv run pytest tests/moneypuck/test_moneypuck.py -v` — all green
- [x] `git status` shows no new files created under `data/` after running this file in isolation

**Dependencies:** Task 1 (conftest structure/conventions only — no shared fixtures required)

**Files likely touched:**
- `ingestion/tests/moneypuck/test_moneypuck.py`

**Estimated scope:** Small: 1 file

---

## Task 9: `tests/utility/test_aws.py`

**Description:** Test `upload_file_to_s3` and `run_s3_upload_fileext` in `utility/aws.py`, with `boto3.client('s3')` mocked. **Resolve the import-time risk first**: `aws.py` calls `boto3.client('s3')` and `load_dotenv("../.env")` at module import time, so a `mocker.patch("boto3.client")` applied *after* import won't intercept the module-level `s3` object — patch `utility.aws.s3` directly (the already-constructed client object) instead of trying to intercept the constructor.

**Acceptance criteria:**
- [x] `upload_file_to_s3` calls the mocked `s3.upload_fileobj` with the right bucket/key for a given file path
- [x] `run_s3_upload_fileext` globs the right files by extension and builds `dest_object_name` from the last 3 path parts, per existing logic
- [x] `run_s3_upload_fileext` on an empty glob result raises the existing `assert` (covered, not treated as a bug to fix)
- [x] No real AWS call occurs; test passes with no AWS credentials configured in the environment

**Verification:**
- [x] `uv run pytest tests/utility/test_aws.py -v` — all green, run once with `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` unset to confirm no real-network dependency

**Dependencies:** Task 1

**Files likely touched:**
- `ingestion/tests/utility/test_aws.py`

**Estimated scope:** Small: 1 file

---

## Task 10: Restore CLAUDE.md Tests section + final full-suite verification

**Description:** Run the complete suite, confirm all spec Success Criteria are met, and restore an accurate `## Tests` section to `CLAUDE.md` (removed earlier this session for being stale — this time it should describe what's actually there).

**Acceptance criteria:**
- [x] `cd ingestion && uv run pytest` — full suite green
- [x] `uv run pytest -m unit` and `uv run pytest -m "not slow"` run cleanly
- [x] `CLAUDE.md` has a `### Tests (from ingestion/)` section with real, working commands

**Verification:**
- [x] Full pytest run with no `.env` file present and no network access (e.g. temporarily rename `.env` or run with network disabled) — suite still passes
- [x] Manually diff `CLAUDE.md`'s new Tests section against actual working commands

**Dependencies:** Tasks 1-9

**Files likely touched:**
- `CLAUDE.md`

**Estimated scope:** Small: 1 file
