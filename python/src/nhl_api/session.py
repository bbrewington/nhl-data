import requests
import backoff

from typing import Dict, Any, Optional

class NHLSession(requests.Session):
    def __init__(self, verbose: bool = False):
        super().__init__()
        self.base_urls = {
            'default': "http://api-web.nhle.com",
            'stats': "https://api.nhle.com/stats/rest"
        }
        self.verbose = verbose
        
        # Set default headers
        self.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'nhl-api-client/1.0.0'
        })
    
    @backoff.on_exception(backoff.expo,
                      (requests.exceptions.Timeout,
                       requests.exceptions.ConnectionError),
                      max_time=15)
    def get_url(self, endpoint: str, response_type: str = 'json', 
                base_url_type: str = 'default', params: Optional[Dict] = None) -> Any:
        """Centralized request method with error handling"""
        if base_url_type not in self.base_urls:
            raise ValueError(f"base_url_type must be one of {list(self.base_urls.keys())}")
        
        base_url = self.base_urls[base_url_type]
        url = base_url + endpoint
        
        if self.verbose:
            print(f"Making request: {url}")
        
        try:
            response = super().get(url, params=params)
            # Let requests handle HTTP errors - clean and simple!
            response.raise_for_status()
            
            if response_type == 'json':
                return response.json()
            elif response_type == 'text':
                return response.text
            else:
                raise ValueError(f"response_type must be 'json' or 'text', got: {response_type}")
                
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)
