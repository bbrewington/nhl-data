"""Fetch play-by-play events and game rosters for a hardcoded list of games.

Writes one Parquet file per game per dataset under data/nhl_api/, matching the
4-level Hive-partitioned layout (nhl_api/{dataset}/game_id={id}/{file}.parquet)
that write_nhl_api_to_s3.py (Task 3) will upload to S3.
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


def write_parquet(df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_pandas(df)
    pq.write_table(table, output_path)
    print(f"Wrote {len(df)} rows to {output_path}")


def fetch_game(client: NHLClient, game_id: int) -> None:
    data = client.games.get_play_by_play(game_id)

    plays = pd.json_normalize(data["plays"], sep="_")
    plays.insert(0, "game_id", game_id)
    write_parquet(plays, DATA_DIR / "play_by_play" / f"game_id={game_id}" / "play_by_play.parquet")

    rosters = pd.json_normalize(data["rosterSpots"], sep="_")
    rosters.insert(0, "game_id", game_id)
    write_parquet(
        rosters, DATA_DIR / "game_rosters" / f"game_id={game_id}" / "game_rosters.parquet"
    )


if __name__ == "__main__":
    with NHLClient() as client:
        for game_id in GAME_IDS:
            print(f"Fetching game {game_id}")
            fetch_game(client, game_id)
