import requests

class Nhl:
    def __init__(self):
        self.base_url = "http://api-web.nhle.com"
    
    def get_url(self, endpoint, response_type):
        try:
            r = requests.get(self.base_url + endpoint)
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
    
    def schedule_calendar(self, date):
        """Get schedule calendar
        Parameters:
            date (str): Date in YYYY-MM-DD format

        URL Response:
            endDate: string
            nextStartDate: string
            previousStartDate: string
            startDate: string
            teams: array<object>
                Items: object
                    id: integer
                    seasonId: integer
                    commonName: object
                    abbrev: string
                    name: object
                    placeName: object
                    logo: string
                    darkLogo: string
                    isNhl: boolean
                    french: boolean

        """
        url_suffix = "/v1/schedule-calendar/" + date
        return self.get_url(url_suffix=url_suffix, response_type='json')

    def game_play_by_play(self, game_id):
        url_suffix = f"/v1/gamecenter/{game_id}/play-by-play"
        return self.get_url(url_suffix=url_suffix, response_type='json')
