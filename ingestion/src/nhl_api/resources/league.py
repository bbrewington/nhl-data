from .base import BaseResource
# from datetime import datetime

class LeagueResource(BaseResource):
    def get_schedule_calendar(self, date: str):
        """Get schedule calendar for a specific date"""
        if date < "1916-12-19":
            raise ValueError("date must be >= 1916-12-19")
        endpoint = f"/v1/schedule-calendar/{date}"
        return self._get(endpoint)
    
    def list_season_ids(self):
        """Get all season IDs"""
        return self._get("/v1/season")
    
    def get_standings(self, date=None, season_info=False):
        """Get NHL standings"""
        if season_info:
            endpoint = "/v1/standings-season"
        elif date:
            endpoint = f"/v1/standings/{date}"
        else:
            endpoint = "/v1/standings/now"
        return self._get(endpoint)
    
    def list_team_info(self, lang='en'):
        """Get all teams information"""
        endpoint = f"/{lang}/team"
        return self._get(endpoint, base_url_type='stats')
    
    def list_games(self, lang='en'):
        """Get all games information"""
        endpoint = f"/{lang}/game"
        return self._get(endpoint, base_url_type='stats')
    
    def get_glossary(self, lang='en'):
        """Get glossary of terms"""
        endpoint = f"/{lang}/glossary"
        return self._get(endpoint, base_url_type='stats')
