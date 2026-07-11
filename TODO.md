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

## Engineering gaps

- No linter/formatter configured anywhere in the repo (e.g. ruff)
