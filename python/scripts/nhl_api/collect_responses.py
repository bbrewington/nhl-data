"""
NHL API Response Collector Script

This script helps collect real NHL API responses for testing.
Run this to generate JSON files

Usage:
    python collect_responses.py
    
The script will create a 'test_responses/' directory with JSON files
containing real API responses that you can then upload.
"""

import json
from pathlib import Path
import requests
from datetime import datetime
from argparse import ArgumentParser

BASE_URL = "http://api-web.nhle.com"
STATS_URL = "https://api.nhle.com/stats/rest"
ENDPOINTS = [
    # League endpoints
    {
        "name": "standings_now",
        "url": f"{BASE_URL}/v1/standings/now",
        "description": "Current NHL standings"
    },
    {
        "name": "standings_date",
        "url": f"{BASE_URL}/v1/standings/2024-01-15",
        "description": "Standings for specific date"
    },
    {
        "name": "season_ids",
        "url": f"{BASE_URL}/v1/season",
        "description": "All season IDs"
    },
    {
        "name": "schedule_calendar",
        "url": f"{BASE_URL}/v1/schedule-calendar/2024-12-01",
        "description": "Schedule calendar for date"
    },
    {
        "name": "team_info_list",
        "url": f"{STATS_URL}/en/team",
        "description": "List of all teams"
    },
    {
        "name": "games_list",
        "url": f"{STATS_URL}/en/game",
        "description": "All games (warning: large response)"
    },
    {
        "name": "glossary",
        "url": f"{STATS_URL}/en/glossary",
        "description": "NHL glossary terms"
    },
    
    # Team endpoints
    {
        "name": "team_stats_stl_now",
        "url": f"{BASE_URL}/v1/club-stats/STL/now",
        "description": "Current STL team stats"
    },
    {
        "name": "team_stats_stl_season",
        "url": f"{BASE_URL}/v1/club-stats/STL/20232024/2",
        "description": "STL 2023-24 regular season stats"
    },
    {
        "name": "team_schedule_stl",
        "url": f"{BASE_URL}/v1/club-schedule-season/STL/now",
        "description": "STL current season schedule"
    },
    {
        "name": "team_scoreboard_stl",
        "url": f"{BASE_URL}/v1/scoreboard/STL/now",
        "description": "STL current scoreboard"
    },
    
    # Player endpoints
    {
        "name": "player_8478402_mcdavid",
        "url": f"{BASE_URL}/v1/player/8478402/landing",
        "description": "Connor McDavid player page"
    },
    {
        "name": "player_8478402_mcdavid_game_log_20232024_regular_season",
        "url": f"{BASE_URL}/v1/player/8478402/game-log/20232024/2",
        "description": "McDavid 2023-24 regular season game log"
    },
    {
        "name": "player_8478402_mcdavid_game_log_now",
        "url": f"{BASE_URL}/v1/player/8478402/game-log/now",
        "description": "McDavid current game log"
    },
    {
        "name": "stats_leaders_skater_current",
        "url": f"{BASE_URL}/v1/skater-stats-leaders/current",
        "description": "Current skater stats leaders"
    },
    {
        "name": "stats_leaders_goalie_current",
        "url": f"{BASE_URL}/v1/goalie-stats-leaders/current",
        "description": "Current goalie stats leaders"
    },
    {
        "name": "stats_leaders_skater_20232024_regular",
        "url": f"{BASE_URL}/v1/skater-stats-leaders/20232024/2",
        "description": "2023-24 regular season skater leaders"
    },
    {
        "name": "stats_leaders_skater_goals_limit10",
        "url": f"{BASE_URL}/v1/skater-stats-leaders/current?categories=goals&limit=10",
        "description": "Top 10 current goal leaders"
    },
    {
        "name": "player_spotlight",
        "url": f"{BASE_URL}/v1/player-spotlight",
        "description": "Players in spotlight"
    },
    
    # Game endpoints  
    {
        "name": "game_2023020204_play_by_play",
        "url": f"{BASE_URL}/v1/gamecenter/2023020204/play-by-play",
        "description": "Game play-by-play data"
    },
    {
        "name": "game_2023020204_landing",
        "url": f"{BASE_URL}/v1/gamecenter/2023020204/landing",
        "description": "Game landing page data"
    },
    {
        "name": "game_boxscore",
        "url": f"{BASE_URL}/v1/gamecenter/2023020204/boxscore",
        "description": "Game boxscore data"
    },
    {
        "name": "game_info",
        "url": f"{BASE_URL}/v1/meta/game/2023020204",
        "description": "Basic game information"
    },
    {
        "name": "game_shift_charts",
        "url": f"{STATS_URL}/en/shiftcharts?cayenneExp=gameId=2023020204",
        "description": "Game shift charts"
    }
]

def create_response_dir():
    """Create directory for storing responses"""
    response_dir = Path("test_responses")
    response_dir.mkdir(exist_ok=True)
    return response_dir

def save_response(endpoint_name, response_data, response_dir):
    """Save API response to JSON file"""
    filename = f"{endpoint_name}.json"
    filepath = response_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(response_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved {endpoint_name} response to {filepath}")

def collect_nhl_responses(endpoints):
    """Collect various NHL API responses"""
    response_dir = create_response_dir()
    
    print(f"Collecting NHL API responses...")
    print(f"Responses will be saved to: {response_dir.absolute()}")
    print("=" * 60)
    
    successful = 0
    failed = 0
    
    for endpoint in endpoints:
        try:
            print(f"Fetching: {endpoint['name']} - {endpoint['description']}")
            
            response = requests.get(endpoint['url'], timeout=30)
            response.raise_for_status()
            
            # Try to parse as JSON
            try:
                data = response.json()
            except json.JSONDecodeError:
                print(f"  ⚠️  Warning: Response is not valid JSON, saving as text")
                data = {"raw_text": response.text}
            
            # Add metadata
            response_with_metadata = {
                "metadata": {
                    "endpoint_name": endpoint['name'],
                    "url": endpoint['url'],
                    "description": endpoint['description'],
                    "collected_at": datetime.now().isoformat(),
                    "status_code": response.status_code,
                    "content_type": response.headers.get('content-type', 'unknown')
                },
                "data": data
            }
            
            save_response(endpoint['name'], response_with_metadata, response_dir)
            successful += 1
            
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Failed to fetch {endpoint['name']}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ❌ Unexpected error for {endpoint['name']}: {e}")
            failed += 1
        
        print()  # Empty line for readability
    
    print("=" * 60)
    print(f"Collection complete!")
    print(f"✓ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"\nNext steps:")
    print(f"1. Check the files in {response_dir.absolute()}")

def main():
    """Main function"""
    print("NHL API Response Collector")
    print("=" * 60)
    
    parser = ArgumentParser()
    parser.add_argument("--endpoint")
    
    try:
        collect_nhl_responses(endpoints=ENDPOINTS)
    except KeyboardInterrupt:
        print("\n\nCollection interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        raise

if __name__ == "__main__":
    main()
