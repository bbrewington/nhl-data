from nhl_api.nhl import Nhl
import re

class Player:
    def __init__(self, player_id):
        self.player_id = player_id
        self.nhl_client = Nhl()
    
    def get_game_log(self, season_id, game_type):
        """
        Description: Retrieve the game log for a specific player, season, and game type.

        Parameters:
            season_id (int) - Season in YYYYYYYY format, where the first four digits represent the start year of the season, and the last four digits represent the end year.
            game_type (int) - Game type (guessing 2 for regular season, 3 for playoffs)
        
        Example URL: "https://api-web.nhle.com/v1/player/8478402/game-log/20232024/2"
        """
        assert game_type in ['regular', 'playoffs'], f"game_type must be either 'regular' or 'playoffs'.  You provided {game_type}"
        if re.match("((19|20)\d{2}){2}", season_id) is None:
            raise ValueError("season_id must be YYYYYYYY format")
        game_type_id = 2 if game_type == 'regular' else 3
        endpoint = f"/v1/player/{self.player_id}/game-log/{season_id}/{game_type_id}"
        return self.nhl_client.get_url(endpoint=endpoint)
    
    def get_info(self):
        """
        Description: Retrieve player information for a specific player.
        Returns: Dictionary (see README.md for example)
        """
        endpoint = f"/v1/player/{self.player_id}/landing"
        return self.nhl_client.get_url(endpoint=endpoint)
    
    def get_game_log_now(self):
        """
        Description: Retrieve the game log for a specific player as of the current moment.

        Example URL: "https://api-web.nhle.com/v1/player/8478402/game-log/now"
        """
        endpoint = f"/v1/player/{self.player_id}/game-log/now"
        return self.nhl_client.get_url(endpoint=endpoint)

    def get_stats_leaders(self, player_type, season=None, game_type=None, categories=None, limit=None):
        """
        Description: Retrieve current stats leaders or stats leaders for a specific season and game type, 
        for either skaters or goalies.
        
        Parameters:
            player_type (str) - Type of player ('skater' or 'goalie').
            season (int, optional) - Season in YYYYYYYY format. If provided, along with game_type, retrieves stats for the specified season and game type. If omitted, retrieves current stats leaders.
            game_type (int, optional) - Game type (2 for regular season, 3 for playoffs). Required if season is specified.
            categories (str, optional) - Categories to filter the stats leaders (e.g., 'goals', 'assists' for skaters, 'wins' for goalies).
            limit (int, optional) - The number of results to return. A limit of -1 will return all results.
        
        Returns:
            JSON response containing the stats leaders.
        """
        # Validate player type
        if player_type not in ['skater', 'goalie']:
            raise ValueError("player_type must be either 'skater' or 'goalie'.")

        # Construct base endpoint
        endpoint = f"/v1/{player_type}-stats-leaders"
        
        # Add current or specific season/game type to endpoint
        if season is not None and game_type is not None:
            if not isinstance(season, int) or len(str(season)) != 8:
                raise ValueError("Season must be in YYYYYYYY format.")
            if game_type not in [2, 3]:
                raise ValueError("Game type must be either 2 (regular season) or 3 (playoffs).")
            endpoint += f"/{season}/{game_type}"
        else:
            endpoint += "/current"

        # Construct query parameters
        params = {}
        if categories is not None:
            params['categories'] = categories
        if limit is not None:
            params['limit'] = limit
        
        # Make the API call
        return self.nhl_client.get_url(endpoint=endpoint, params=params)

    def get_player_spotlight(self):
        """
        Description: Retrieve information about players in the "spotlight".

        Returns:
            JSON response containing information about spotlighted players.
        """
        endpoint = "/v1/player-spotlight"
        return self.nhl_client.get_url(endpoint=endpoint)
