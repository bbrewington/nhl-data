from .base import BaseResource

class TeamsResource(BaseResource):
    def get_info(self, team_id: int, lang: str = 'en'):
        """Get information for a specific team"""
        # Could call league.list_team_info and filter, or implement direct endpoint
        from .league import LeagueResource
        league = LeagueResource(self.session)
        all_teams = league.list_team_info(lang)
        team = [t for t in all_teams['data'] if t['id'] == team_id]
        if not team:
            raise ValueError(f"Team with id {team_id} not found")
        return team[0]
    
    def get_stats(self, team_code: str, stat_type: str, season=None, game_type=None):
        """Get team statistics"""
        if stat_type == "season_game_type":
            if not (season and game_type):
                raise ValueError("season and game_type required for season_game_type")
            game_type_id = 2 if game_type == 'regular' else 3
            endpoint = f"/v1/club-stats/{team_code}/{season}/{game_type_id}"
        elif stat_type == "by_season":
            endpoint = f"/v1/club-stats-season/{team_code}"
        elif stat_type == "now":
            endpoint = f"/v1/club-stats/{team_code}/now"
        else:
            raise ValueError(f"Invalid stat_type: {stat_type}")
        
        return self._get(endpoint)
    
    def get_scoreboard(self, team_code: str):
        """Get current scoreboard for team"""
        endpoint = f"/v1/scoreboard/{team_code}/now"
        return self._get(endpoint)
    
    def get_schedule(self, team_code: str, schedule_type: str = 'season', 
                     time: str = 'now', period=None):
        """Get team schedule"""
        # Implementation from your current get_team_schedule
        if schedule_type not in ['season', 'month', 'week']:
            raise ValueError("schedule_type must be 'season', 'month', or 'week'")
        
        if schedule_type == 'season':
            endpoint = f"/v1/club-schedule-season/{team_code}"
            if time == 'now':
                endpoint += "/now"
            elif time == 'season' and period:
                endpoint += f"/{period}"
        # ... rest of implementation
        
        return self._get(endpoint)
