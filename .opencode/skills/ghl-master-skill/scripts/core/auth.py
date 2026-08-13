import os
import json
from pathlib import Path
from dotenv import load_dotenv

class GHLAuth:
    def __init__(self, env_path=None):
        self.env_path = env_path or Path(".env")
        load_dotenv(self.env_path)
        self.api_key = os.getenv("GHL_API_KEY")
        self.location_id = os.getenv("GHL_LOCATION_ID")
        self.agency_api_key = os.getenv("GHL_AGENCY_API_KEY")
        self.access_token = os.getenv("GHL_ACCESS_TOKEN")
        self.refresh_token = os.getenv("GHL_REFRESH_TOKEN")

    def get_headers(self, version="2021-04-15"):
        """
        Generates headers based on available credentials.
        Prioritizes Access Token (OAuth2) over API Key (PIT).
        """
        headers = {
            "Version": version,
            "Accept": "application/json"
        }
        
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        elif self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        else:
            raise ValueError("No valid GHL credentials found in .env (GHL_ACCESS_TOKEN or GHL_API_KEY)")
            
        return headers

    def get_location_id(self):
        if not self.location_id:
             raise ValueError("GHL_LOCATION_ID is required but missing from .env")
        return self.location_id
