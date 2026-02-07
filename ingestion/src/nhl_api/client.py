from .session import NHLSession
from .resources.league import LeagueResource
from .resources.teams import TeamsResource
from .resources.players import PlayersResource
from .resources.games import GamesResource


class NHLClient:
    def __init__(self, verbose: bool = False):
        self.session = NHLSession()
        self.session.verbose = verbose
        
        # Initialize resource clients
        self.league = LeagueResource(self.session)
        self.teams = TeamsResource(self.session)
        self.players = PlayersResource(self.session)
        self.games = GamesResource(self.session)
    
    def close(self):
        """Close the session"""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
