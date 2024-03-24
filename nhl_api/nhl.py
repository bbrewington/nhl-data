import requests

class Nhl:
    def __init__(self):
        pass
    
    def get_url(self, endpoint, response_type='json', base_url_type='default'):
        if base_url_type == 'default':
            base_url = "http://api-web.nhle.com"
        elif base_url_type == 'stats':
            base_url = "https://api.nhle.com/stats/rest"
        else:
            raise ValueError(f"base_url_type must be one of 'default' or 'stats'. You provided: {base_url_type}")
        
        try:
            r = requests.get(base_url + endpoint)
            if response_type == 'text':
                r_parsed = r.text
            elif response_type == 'json':
                r_parsed = r.json()
            else:
                raise ValueError(f"response_type must be one of 'text', 'json'. You provided: {response_type}")
            return r_parsed
        except Exception as e:
            print(e)
            raise
    
    def get_schedule_calendar(self, date):
        """Get schedule calendar
        Parameters:
            date (str): Date in YYYY-MM-DD format (must be >= 1916-12-19)

        Response example:
        {   'endDate', 'nextStartDate', 'previousStartDate', 'startDate',
            'teams': [
                {'abbrev': 'NJD',
                'commonName': {'default': 'Devils'},
                'darkLogo': 'https://assets.nhle.com/logos/nhl/svg/NJD_dark.svg',
                'french': False,
                'id': 1,
                'isNhl': True,
                'logo': 'https://assets.nhle.com/logos/nhl/svg/NJD_light.svg',
                'name': {'default': 'New Jersey Devils', 'fr': 'Devils du New Jersey'},
                'placeName': {'default': 'New Jersey'},
                'seasonId': 20232024
                },
                ...
            ]
        }
        """
        if date < "1916-12-19":
            raise ValueError("date must be value >= 1916-12-19")
        endpoint = "/v1/schedule-calendar/" + date
        return self.get_url(endpoint=endpoint)

    def list_team_info(self, lang='en'):
        """
        Retrieve a list of all teams in the specified language.

        Parameters:
            lang (str, optional): Language code (either 'en' or 'fr'). Defaults to 'en'.

        Returns:            
            {'data':
                [
                    {
                        'franchiseId': 18,
                        'fullName': 'St. Louis Blues',
                        'id': 19,
                        'leagueId': 133,
                        'rawTricode': 'STL',
                        'triCode': 'STL'
                    }, 
                    ...
                ],
             'total': <# of teams>
            }
        """
        endpoint = f"/{lang}/team"
        return self.get_url(endpoint=endpoint, base_url_type='stats')

    def list_seasons(self):
        """Retrieve a list of all season IDs past & present in the NHL.

        Returns:
            list[int]: List of all season ID's
                Example: [19171918, ..., 20232024]
        """
        endpoint = "/v1/season"
        return self.get_url(endpoint=endpoint)

    def list_games(self, lang='en'):
        """Retrieve game information for all completed games, all seasons

        Args:
            lang (str, optional): Language code (either 'en' or 'fr'). Defaults to 'en'.

        Returns dictionary with 2 keys: 'data' (list of games) & 'total' (length of list) - example:
            {
                'data': [
                    {
                        'id': 2023120001,
                        'easternStartTime': '2024-02-01T20:00:00',
                        'gameDate': '2024-02-01',
                        'gameNumber': 1,
                        'gameScheduleStateId': 1,
                        'gameStateId': 6,
                        'gameType': 12,
                        'homeScore': 3,
                        'homeTeamId': 7806,
                        'period': 2,
                        'season': 20232024,
                        'visitingScore': 5,
                        'visitingTeamId': 7805
                    },
                    ...
                ],
                'total': 71032
            }
        """
        
        endpoint = f"/{lang}/game"
        return self.get_url(endpoint=endpoint, base_url_type='stats')

    def get_glossary(self, lang='en'):
        """Get glossary of terms

        Args:
            lang (str, optional): Language code (either 'en' or 'fr'). Defaults to 'en'.

        Returns:
            _type_: _description_
        """
        endpoint = f"/{lang}/glossary"
        return self.get_url(endpoint=endpoint, base_url_type='stats')

    def get_standings(self, date=None, season_info=False):
        """
        Description: Retrieve the NHL standings. Can fetch the current standings, standings for a specific date, 
        or standings information for each season based on the parameters provided.
        
        Parameters:
            date (str, optional) - Date in YYYY-MM-DD format to retrieve the standings for a specific date.
            season_info (bool, optional) - If True, retrieves information for each season's standings instead of current or specific date standings.
            
        Returns:
            JSON response containing the requested standings information.
        """
        # Base URL for the standings endpoint
        base_url = "/v1/standings"
        
        # Determine the endpoint based on the parameters
        if season_info==True:
            endpoint = f"{base_url}-season"
        elif date is not None:
            endpoint = f"{base_url}/{date}"
        else:
            endpoint = f"{base_url}/now"
        
        # Make the API call
        return self.nhl_client.get_url(endpoint=endpoint)
