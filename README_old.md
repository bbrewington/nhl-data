# nhl-data

## Repo Organization

- `dbt/`: Contains a dbt (Data Build Tool) project for Transforming and modeling raw data
- `get_data/`: Scripts and automation for sourcing raw data
  - `moneypuck/`: Download CSV's from [moneypuck.com/data.htm](https://moneypuck.com/data.htm) and ingest to S3
  - `nhl_api/`: Ingest data from (not officially documented) NHL API
    - Note, this is currently just Python code mapping to the API.  Need to update to get it to write out to S3 <!-- TODO: Write NHL API to S3 -->

## 

Key:
- 🚧: Data source has & code needs more work
- ✅: Data source has & code is done enough
- ❌: Data source doesn't have this entity

Entity | Moneypuck | NHL API | Notes
---|---|---|---
Season | ✅ | ✅ | Moneypuck has season-level summary data for teams, goalies, lines, and skaters
Game | ✅ | ✅ |
Line | ✅ | TBD | 
Player | ✅ | 🚧 |
Play | ❌ | ✅ | nhl_api.resources.games.get_play_by_play
Shot | ✅ | 🚧 |
Team | ✅ | ✅ |

## Individual Endpoints / Methods / Data Sources

### Moneypuck

