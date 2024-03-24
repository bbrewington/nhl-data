from nhl_api.nhl import Nhl

class Team:
    def __init__(self, team_id):
        self.nhl_client = Nhl()
        self.team_id = team_id
        self.team_info = self.get_team_info(self.team_id)
        self.team_code = self.team_info['triCode']
    
    def get_team_info(self, lang='en'):
        """
        Retrieve information on a single team

        Parameters:
            lang (str, optional): Language code (either 'en' or 'fr'). Defaults to 'en'.

        Returns:
            dictionary of team attributes.  Example:
                {'franchiseId': 18,
                 'fullName': 'St. Louis Blues',
                 'id': 19,
                 'leagueId': 133,
                 'rawTricode': 'STL',
                 'triCode': 'STL'
                }
        """
        all_teams = self.nhl_client.list_team_info(lang)
        team = [team for team in all_teams['data'] if team['id'] == self.team_id]
        assert len(team) == 1, f"Multiple teams from Nhl.list_team_info with id: {self.team_id}"
        return team[0]

    def get_team_stats(self, season=None, game_type=None):
        """
        Retrieve statistics for a specific team. Can fetch current stats, stats for each season, or stats for a specific season and game type.

        Parameters:
            season (int, optional) - Season in YYYYYYYY format. Specifies the season for which to fetch stats.
            game_type (int, optional) - Game type (2 for regular season, 3 for playoffs). Required if season is specified.

        Returns:
            JSON response containing the requested team statistics.
        """
        if season and game_type:
            endpoint = f"/v1/club-stats/{self.team_code}/{season}/{game_type}"
        elif season:
            endpoint = f"/v1/club-stats-season/{self.team_code}"
        else:
            endpoint = f"/v1/club-stats/{self.team_code}/now"
        
        return self.nhl_client.get_url(endpoint=endpoint)

    def get_team_scoreboard_now(self):
        """
        Retrieve the scoreboard for a specific team as of the current moment.

        Parameters:
            team (str) - The three-letter team code.

        Returns:
            Dictionary - example shown below:
            {   'focusedDate': '2024-03-23',
                'focusedDateCount': 11,
                'clubTimeZone': 'US/Central',
                'clubUTCOffset': '-05:00',
                'clubScheduleLink': '/blues/schedule',
                'gamesByDate': [
                    {
                        'date': '2024-03-17',
                        'games': [
                            {
                                'id': 2023021079,
                                'season': 20232024,
                                'gameType': 2,
                                'gameDate': '2024-03-17',
                                'gameCenterLink': '/gamecenter/ana-vs-stl/2024/03/17/2023021079',
                                'venue': {'default': 'Enterprise Center'},
                                'startTimeUTC': '2024-03-17T23:00:00Z',
                                'easternUTCOffset': '-04:00',
                                'venueUTCOffset': '-05:00',
                                'tvBroadcasts': [
                                    {
                                        'id': 357,
                                        'market': 'H',
                                        'countryCode': 'US',
                                        'network': 'BSMW',
                                        'sequenceNumber': 95
                                    },
                                    ...
                                ],
                                'gameState': 'OFF',
                                'gameScheduleState': 'OK',
                                'awayTeam': {
                                    'id': 24,
                                    'name': {'default': 'Anaheim Ducks', 'fr': "Ducks d'Anaheim"},
                                    'abbrev': 'ANA',
                                    'score': 2,
                                    'logo': 'https://assets.nhle.com/logos/nhl/svg/ANA_light.svg'
                                },
                                'homeTeam': {
                                    'id': 19,
                                    'name': {'default': 'St. Louis Blues', 'fr': 'Blues de St. Louis'},
                                    'abbrev': 'STL',
                                    'score': 4,
                                    'logo': 'https://assets.nhle.com/logos/nhl/svg/STL_light.svg'
                                },
                                'ticketsLink': 'https://www.ticketmaster.com/event/06005EDABF6C3BB5?brand=blues&artistid=806025&wt.mc_id=NHL_TEAM_STL_WEB_MIG_GM33&utm_source=nhl.com&utm_medium=client&utm_campaign=NHL_TEAM_STL&utm_content=WEB_MIG_GM33',
                                'period': 3,
                                'periodDescriptor': {'number': 3, 'periodType': 'REG'},
                                'threeMinRecap': '/video/recap-ducks-at-blues-3-17-24-6349153126112'
                            }
                        ]
                    }
                ]
            }
        """
        endpoint = f"/v1/scoreboard/{self.team_code}/now"
        return self.nhl_client.get_url(endpoint=endpoint)

    def get_schedule(self, schedule_type='season', time='now', period=None):
        """
        Retrieve the schedule for a specific team. Can fetch season, monthly, or weekly schedules for current or specific periods.

        Parameters:
            schedule_type (str) - Type of schedule to retrieve ('season', 'month', 'week'). Default is 'season'.
            time (str) - When to retrieve the schedule for ('now' for current, or specify 'season' for a specific season, 'month', or 'date'). Default is 'now'.
            period (str, optional) - Specific period for the schedule in 'YYYYYYYY' format for season, 'YYYY-MM' format for month, or 'YYYY-MM-DD' format for week. Required if time is not 'now'.

        Returns:
            Dictionary - example shown below:
            {   'clubTimezone': 'US/Central',
                'clubUTCOffset': '-05:00',
                'currentSeason': 20232024,
                'previousSeason': 20222023,
                'games':
                    [
                        {
                            'awayTeam': {'abbrev': 'ARI',
                                        'awaySplitSquad': True,
                                        'darkLogo': 'https://assets.nhle.com/logos/nhl/svg/ARI_dark.svg',
                                        'id': 53,
                                        'logo': 'https://assets.nhle.com/logos/nhl/svg/ARI_light.svg',
                                        'placeName': {'default': 'Arizona'},
                                        'score': 2},
                            'easternUTCOffset': '-04:00',
                            'gameCenterLink': '/gamecenter/ari-vs-stl/2023/09/23/2023010002',
                            'gameDate': '2023-09-23',
                            'gameOutcome': {'lastPeriodType': 'REG'},
                            'gameScheduleState': 'OK',
                            'gameState': 'FINAL',
                            'gameType': 1,
                            'homeTeam': {'abbrev': 'STL',
                                        'darkLogo': 'https://assets.nhle.com/logos/nhl/svg/STL_dark.svg',
                                        'homeSplitSquad': True,
                                        'hotelDesc': 'Stay at Hilton',
                                        'hotelLink': 'https://www.stlouisunionstation.com/hotel-packages',
                                        'id': 19,
                                        'logo': 'https://assets.nhle.com/logos/nhl/svg/STL_light.svg',
                                        'placeName': {'default': 'St. Louis'},
                                        'score': 3},
                            'id': 2023010002,
                            'neutralSite': False,
                            'periodDescriptor': {'periodType': 'REG'},
                            'season': 20232024,
                            'startTimeUTC': '2023-09-23T19:00:00Z',
                            'tvBroadcasts': [{'countryCode': 'US',
                                            'id': 389,
                                            'market': 'H',
                                            'network': 'BSMW APP',
                                            'sequenceNumber': 69}],
                            'venue': {'default': 'Enterprise Center'},
                            'venueTimezone': 'US/Central',
                            'venueUTCOffset': '-05:00',
                            'winningGoalScorer': {'firstInitial': {'default': 'J.'},
                                                'lastName': {'default': 'Kyrou'},
                                                'playerId': 8479385},
                            'winningGoalie': {'firstInitial': {'default': 'V.'},
                                            'lastName': {'default': 'Zherenko'},
                                            'playerId': 8481689}
                        },
                        ...
                    ]
            }
        """
        # Validate input parameters
        if schedule_type not in ['season', 'month', 'week']:
            raise ValueError("schedule_type must be 'season', 'month', or 'week'.")
        if time not in ['now', 'season', 'month', 'date']:
            raise ValueError("time must be 'now', 'season', 'month', or 'date'.")
        if time != 'now' and not period:
            raise ValueError("period is required when time is not 'now'.")

        # Construct the endpoint based on parameters
        if schedule_type == 'season':
            endpoint = f"/v1/club-schedule-season/{self.team_code}"
            if time == 'now':
                endpoint += "/now"
            elif time == 'season' and period:
                endpoint += f"/{period}"
        elif schedule_type in ['month', 'week']:
            endpoint = f"/v1/club-schedule/{self.team_code}/{schedule_type}"
            if time == 'now':
                endpoint += "/now"
            elif (time == 'month' and period) or (time == 'date' and period):
                endpoint += f"/{period}"

        return self.nhl_client.get_url(endpoint=endpoint)
