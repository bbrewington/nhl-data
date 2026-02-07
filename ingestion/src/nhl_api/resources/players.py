import re
from .base import BaseResource

class PlayersResource(BaseResource):
    def get(self, player_id: int):
        """Get player information"""
        endpoint = f"/v1/player/{player_id}/landing"
        return self._get(endpoint)
    
    def get_game_log(self, player_id: int, season_id: int, game_type: str):
        """Get player game log for specific season"""
        if game_type not in ['regular', 'playoffs']:
            raise ValueError("game_type must be 'regular' or 'playoffs'")
        if not re.match(r"((19|20)\d{2}){2}", str(season_id)):
            raise ValueError("season_id must be YYYYYYYY format")
        
        game_type_id = 2 if game_type == 'regular' else 3
        endpoint = f"/v1/player/{player_id}/game-log/{season_id}/{game_type_id}"
        return self._get(endpoint)
    
    def get_game_log_current(self, player_id: int):
        """Get current game log for player"""
        endpoint = f"/v1/player/{player_id}/game-log/now"
        return self._get(endpoint)
    
    def get_stats_leaders(self, player_type: str, season=None, game_type=None, 
                         categories=None, limit=None):
        """Get stats leaders"""
        if player_type not in ['skater', 'goalie']:
            raise ValueError("player_type must be 'skater' or 'goalie'")
        
        endpoint = f"/v1/{player_type}-stats-leaders"
        
        if season and game_type:
            game_type_id = 2 if game_type == 'regular' else 3
            endpoint += f"/{season}/{game_type_id}"
        else:
            endpoint += "/current"
        
        params = {}
        if categories:
            params['categories'] = categories
        if limit:
            params['limit'] = limit
        
        return self._get(endpoint, params=params)
    
    def get_spotlight(self):
        """Get players in spotlight"""
        return self._get("/v1/player-spotlight")
