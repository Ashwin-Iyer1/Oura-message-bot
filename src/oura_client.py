import requests
from datetime import datetime
from typing import Dict, Any, Optional

class OuraClient:
    """Client for Oura V2 API."""
    
    BASE_URL = "https://api.ouraring.com/v2"

    def __init__(self, access_token: str):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {access_token}"
        })

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_personal_info(self) -> Dict[str, Any]:
        """Get personal info."""
        return self._get("/usercollection/personal_info")

    def get_daily_sleep(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get daily sleep documents."""
        return self._get("/usercollection/daily_sleep", params={
            "start_date": start_date,
            "end_date": end_date
        })

    def get_daily_activity(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get daily activity documents."""
        return self._get("/usercollection/daily_activity", params={
            "start_date": start_date,
            "end_date": end_date
        })

    def get_daily_readiness(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get daily readiness documents."""
        return self._get("/usercollection/daily_readiness", params={
            "start_date": start_date,
            "end_date": end_date
        })

    def get_daily_stress(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get daily stress (using daily_stress endpoint if available or generic getter)."""
        # Note: daily_stress might not be in the v2/usercollection list in all docs, checking...
        # If not, we might need to rely on the others. 
        # But 'daily_stress' is a common newer endpoint. 
        # Let's add it tentatively, or stick to the core 3 needed for now.
        return self._get("/usercollection/daily_stress", params={
            "start_date": start_date,
            "end_date": end_date
        })
