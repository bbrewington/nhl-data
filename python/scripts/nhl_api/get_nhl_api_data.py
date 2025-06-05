from nhl_api.client import NHLClient

# Initialize client
client = NHLClient()

# League operations
standings = client.league.get_standings()
teams = client.league.list_team_info()

# Team operations
team_stats = client.teams.get_stats("STL", "now")
schedule = client.teams.get_schedule("STL")

# Player operations  
player = client.players.get(8478402)
game_log = client.players.get_game_log(8478402, 20232024, 'regular')

# Game operations
boxscore = client.games.get_boxscore(2023020204)
play_by_play = client.games.get_play_by_play(2023020204)

# Context manager support
with NHLClient() as client:
    data = client.league.get_standings()
