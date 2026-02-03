import requests
from datetime import datetime
from typing import Dict, Any, Optional

class OuraClient:
    """Client for Oura V2 API."""
    
    BASE_URL = "https://api.ouraring.com/v2"

    def __init__(self, client_id: str, client_secret: str, token_file: str = "oura_tokens.json"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_file = token_file
        self.session = requests.Session()
        self._load_tokens()

    def _load_tokens(self):
        """Load tokens from file."""
        import json
        import os
        
        if os.path.exists(self.token_file):
            with open(self.token_file, 'r') as f:
                self.tokens = json.load(f)
            self.session.headers.update({
                "Authorization": f"Bearer {self.tokens.get('access_token')}"
            })
        else:
            raise FileNotFoundError(f"Token file {self.token_file} not found. Run setup_oauth.py first.")

    def _save_tokens(self, tokens: Dict[str, Any]):
        """Save tokens to file."""
        import json
        self.tokens = tokens
        with open(self.token_file, 'w') as f:
            json.dump(tokens, f, indent=4)
        
        self.session.headers.update({
            "Authorization": f"Bearer {self.tokens.get('access_token')}"
        })

    def _refresh_token(self):
        """Refresh the access token."""
        print("🔄 Refreshing access token...")
        url = "https://api.ouraring.com/oauth/token"
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.tokens.get("refresh_token"),
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        response = requests.post(url, data=data)
        response.raise_for_status()
        
        new_tokens = response.json()
        self._save_tokens(new_tokens)
        print("✅ Token refreshed successfully.")

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, retry: bool = True) -> Dict[str, Any]:
        url = f"{self.BASE_URL}{endpoint}"
        response = self.session.get(url, params=params)
        
        if response.status_code == 401 and retry:
            try:
                self._refresh_token()
                # Retry request with new token
                return self._get(endpoint, params, retry=False)
            except Exception as e:
                print(f"❌ Failed to refresh token: {e}")
                response.raise_for_status()
                
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
        return self._get("/usercollection/daily_stress", params={
            "start_date": start_date,
            "end_date": end_date
        })

    def get_daily_spo2(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get daily SpO2 documents."""
        return self._get("/usercollection/daily_spo2", params={
            "start_date": start_date,
            "end_date": end_date
        })

    def get_workouts(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get workout documents."""
        return self._get("/usercollection/workout", params={
            "start_date": start_date,
            "end_date": end_date
        })
