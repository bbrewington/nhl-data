from nhl_api.nhl import Nhl

class Game:
    """Represents an NHL game.

    Attributes:
        game_id (int): The ID of the game (example: 2023020204)
        nhl_client (Nhl): An instance of the Nhl class used for making API requests.

    Methods:
        get_play_by_play(): Retrieve play-by-play information
        get_landing(): Retrieve landing information (comprehensive game details).
        get_boxscore(): Retrieve boxscore information
        get_game_info(): Retrieve high level info (season info & teams)
        get_all_details(): Get superset of play-by-play, landing, and boxscore details
    """
    def __init__(self, game_id):
        self.game_id = game_id
        self.nhl_client = Nhl()

    def get_all_details(self):
        """Get superset of play-by-play, landing, and boxscore details
        """
        play_by_play = self.get_play_by_play()
        landing = self.get_landing()
        boxscore = self.get_boxscore()
        game_info = self.get_game_info()
        shift_charts = self.get_shift_charts()
        
        all_details = dict()
        all_details.update(play_by_play)
        all_details.update(landing)
        all_details.update(boxscore)
        all_details.update(game_info)
        all_details.update(shift_charts)
        
        return all_details
    
    def get_play_by_play(self):
        """Retrieve play-by-play information

        Args:
            game_id (int): Game ID

        Returns:
            Dictionary with keys:
                ['id', 'season', 'gameType', 'limitedScoring', 'gameDate', 'venue',
                'venueLocation', 'startTimeUTC', 'easternUTCOffset', 'venueUTCOffset',
                'tvBroadcasts', 'gameState', 'gameScheduleState', 'periodDescriptor',
                'awayTeam', 'homeTeam', 'shootoutInUse', 'otInUse', 'clock',
                'displayPeriod', 'maxPeriods', 'gameOutcome', 'plays', 'rosterSpots',
                'gameVideo', 'regPeriods', 'summary']
        
        Example URL: https://api-web.nhle.com/v1/gamecenter/2023020204/play-by-play
        """
        endpoint = f"/v1/gamecenter/{self.game_id}/play-by-play"
        return self.nhl_client.get_url(endpoint=endpoint)
    
    def get_landing(self):
        """Retrieve landing information (comprehensive game details)

        Returns:
            Dictionary with keys:
                ['id', 'season', 'gameType', 'limitedScoring', 'gameDate', 'venue',
                'venueLocation', 'startTimeUTC', 'easternUTCOffset', 'venueUTCOffset',
                'venueTimezone', 'periodDescriptor', 'tvBroadcasts', 'gameState',
                'gameScheduleState', 'awayTeam', 'homeTeam', 'shootoutInUse', 'maxPeriods',
                'regPeriods', 'otInUse', 'tiesInUse', 'summary', 'clock', 'gameVideo']
        
        Example URL: "https://api-web.nhle.com/v1/gamecenter/2023020204/landing"
        """
        endpoint = f"/v1/gamecenter/{self.game_id}/landing"
        return self.nhl_client.get_url(endpoint=endpoint)
    
    def get_boxscore(self):
        """Retrieve boxscore information
        
        Returns:
            Dictionary with keys:
                ['id', 'season', 'gameType', 'limitedScoring', 'gameDate', 'venue',
                'venueLocation', 'startTimeUTC', 'easternUTCOffset', 'venueUTCOffset',
                'tvBroadcasts', 'gameState', 'gameScheduleState', 'periodDescriptor',
                'regPeriods', 'awayTeam', 'homeTeam', 'clock', 'playerByGameStats',
                'summary', 'gameOutcome', 'gameVideo']
        
        Example URL: "https://api-web.nhle.com/v1/gamecenter/2023020204/boxscore"
        """
        endpoint = f"/v1/gamecenter/{self.game_id}/boxscore"
        return self.nhl_client.get_url(endpoint=endpoint)

    def get_game_info(self):
        """Retrieve information
        
        Example URL: "https://api-web.nhle.com/v1/meta/game/2023020204"
        
        Returns:
            Dictionary with two elements:
                seasonStates - dict with keys: date, gameType, season
                teams - list (length 2) of dicts with keys: name, teamId, tricode
        """
        endpoint = f"/v1/meta/game/{self.game_id}"
        return self.nhl_client.get_url(endpoint=endpoint)

    def get_shift_charts(self, lang='en'):
        """Get shift charts (raw data behind a chart like this: https://www.nhl.com/stats/shiftcharts?id=2023020204)

        Args:
            lang (str, optional): Language code (either 'en' or 'fr'). Defaults to 'en'.

        Returns:
            Dictionary with 2 keys: ['data', 'total']
                'data' is a list of dicts, each element representing one player's shift
                Example shift:
                {   'detailCode': 0, 'duration': '00:47', 'endTime': '03:29',
                    'eventDescription': None, 'eventDetails': None, 'eventNumber': 81,
                    'firstName': 'Erik', 'gameId': 2023020204, 'hexValue': '#041E42',
                    'id': 13399553, 'lastName': 'Johnson', 'period': 1, 'playerId': 8473446,
                    'shiftNumber': 1, 'startTime': '02:42', 'teamAbbrev': 'BUF',
                    'teamId': 7, 'teamName': 'Buffalo Sabres', 'typeCode': 517}
        """
        endpoint = f"/{lang}/shiftcharts?cayenneExp=gameId={self.game_id}"
        return self.nhl_client.get_url(endpoint=endpoint, base_url_type='stats')
