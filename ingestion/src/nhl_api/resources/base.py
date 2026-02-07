class BaseResource:
    def __init__(self, session):
        self.session = session
    
    def _get(self, endpoint: str, **kwargs):
        """Wrapper for GET requests"""
        return self.session.get_url(endpoint, **kwargs)
