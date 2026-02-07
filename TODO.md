Key:
- 🚧: Data source has & code needs more work
- ✅: Data source has & code is done enough
- ❌: Data source doesn't have this entity

Entity | Moneypuck | NHL API | Notes
---|---|---|---
Season | ✅ | ✅ | Moneypuck has season-level summary data for teams, goalies, lines, and skaters
Game | ✅ | ✅ |
Line | ✅ | ❌ |
Player | ✅ | ✅ | NHL API: player info, game logs, stats leaders
Play | ❌ | ✅ | nhl_api.resources.games.get_play_by_play
Shot | ✅ | ❌ | NHL API: no dedicated endpoint; could be derived from play-by-play
Team | ✅ | ✅ |

## dbt improvements

- [ ] Fix `penalityMinutesFor`/`Against` typo in `stg_moneypuck__team_game_situation` (rename to `penalty_minutes_*` like other models)
- [ ] Investigate whether `shot_id` is unique in `stg_moneypuck__shots` and add `unique` test if so
- [ ] Add column-level descriptions to `_models.yml` files (currently only model-level descriptions)
- [ ] Add uniqueness tests to season segment models (skater/goalie/line situation)
- [ ] Resolve `opposing_team_abbr` in `int__team_game` (still raw, unlike `team_abbr_raw` which is now resolved)
- [ ] Consolidate `models/staging/_sources.yml` and `snapshots/_sources.yml` into a single file

## Repo cleanup

- [ ] Move `get_data/src/nhl_api/README.md` to `python/src/nhl_api/README.md` (API docs with example responses)
- [ ] Move `get_data/src/moneypuck/README.md` to `python/src/moneypuck/README.md` (setup/usage docs)
- [ ] Delete `get_data/` after moving READMEs (remnant from repo reorganization; no code, only stale configs)
