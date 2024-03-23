from nhl import Nhl
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
        return self.nhl_client.get_url(endpoint=endpoint, response_type = 'json')
    
    def get_info(self):
        """
        Description: Retrieve player information for a specific player.

        Example URL: "https://api-web.nhle.com/v1/player/8478402/landing"
        """
        endpoint = f"/v1/player/{self.player_id}/landing"
        return self.nhl_client.get_url(endpoint=endpoint, response_type='json')
    
    def get_game_log_now(self):
        """
        Description: Retrieve the game log for a specific player as of the current moment.

        Example URL: "https://api-web.nhle.com/v1/player/8478402/game-log/now"
        """
        endpoint = f"/v1/player/{self.player_id}/game-log/now"
        return self.nhl_client.get_url(endpoint=endpoint, response_type='json')
