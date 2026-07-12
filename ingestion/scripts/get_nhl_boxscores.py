"""Fetch boxscores for a hardcoded list of games.

Writes one Parquet file per game under data/nhl_api/boxscores/, matching the
4-level Hive-partitioned layout (nhl_api/{dataset}/game_id={id}/{file}.parquet)
that write_nhl_api_to_s3.py (Task 3) will upload to S3.

Flattens playerByGameStats (grouped by team and position) into one row per
player-game, per the spec's stg_nhl_api__boxscores grain.
"""

from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from nhl_api.client import NHLClient

DATA_DIR = Path("../data/nhl_api")

# STL, 2024-2025 regular season, 2024-10-08 through 2024-11-21.
# 16 REG / 4 OT / 1 SO, chosen for situationCode/game-state coverage.
# See tasks/plan.md "Resolved Decisions" for how this list was derived.
GAME_IDS = [
    2024020003,
    2024020019,
    2024020023,
    2024020052,
    2024020068,
    2024020084,
    2024020099,
    2024020110,
    2024020126,
    2024020150,
    2024020162,
    2024020181,
    2024020199,
    2024020215,
    2024020229,
    2024020248,
    2024020257,
    2024020272,
    2024020284,
    2024020296,
    2024020312,
]

POSITION_GROUPS = ("forwards", "defense", "goalies")


def write_parquet(df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_pandas(df)
    pq.write_table(table, output_path)
    print(f"Wrote {len(df)} rows to {output_path}")


def fetch_game(client: NHLClient, game_id: int) -> None:
    data = client.games.get_boxscore(game_id)

    rows = []
    for team_key in ("awayTeam", "homeTeam"):
        team_id = data[team_key]["id"]
        team_stats = data["playerByGameStats"][team_key]
        for position_group in POSITION_GROUPS:
            for player in team_stats.get(position_group, []):
                rows.append({**player, "team_id": team_id, "position_group": position_group})

    boxscores = pd.json_normalize(rows, sep="_")
    boxscores.insert(0, "game_id", game_id)
    write_parquet(boxscores, DATA_DIR / "boxscores" / f"game_id={game_id}" / "boxscores.parquet")


if __name__ == "__main__":
    with NHLClient() as client:
        for game_id in GAME_IDS:
            print(f"Fetching game {game_id}")
            fetch_game(client, game_id)
