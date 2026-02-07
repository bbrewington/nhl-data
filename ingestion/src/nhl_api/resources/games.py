from .base import BaseResource

class GamesResource(BaseResource):
    def get_play_by_play(self, game_id: int):
        """Get game play-by-play data"""
        endpoint = f"/v1/gamecenter/{game_id}/play-by-play"
        return self._get(endpoint)
    
    def get_landing(self, game_id: int):
        """Get comprehensive game details"""
        endpoint = f"/v1/gamecenter/{game_id}/landing"
        return self._get(endpoint)
    
    def get_boxscore(self, game_id: int):
        """Get game boxscore"""
        endpoint = f"/v1/gamecenter/{game_id}/boxscore"
        return self._get(endpoint)
    
    def get_info(self, game_id: int):
        """Get basic game information"""
        endpoint = f"/v1/meta/game/{game_id}"
        return self._get(endpoint)
    
    def get_shift_charts(self, game_id: int, lang: str = 'en'):
        """Get shift charts for game"""
        endpoint = f"/{lang}/shiftcharts?cayenneExp=gameId={game_id}"
        return self._get(endpoint, base_url_type='stats')
