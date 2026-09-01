import httpx
from .auth import GHLAuth

class GHLClient:
    BASE_URL = "https://services.leadconnectorhq.com"
    
    def __init__(self, auth: GHLAuth = None):
        self.auth = auth or GHLAuth()
        self.client = httpx.Client(base_url=self.BASE_URL, timeout=30.0)

    def request(self, method: str, path: str, **kwargs):
        headers = self.auth.get_headers()
        # Merge custom headers from kwargs if any
        if "headers" in kwargs:
             headers.update(kwargs.pop("headers"))
             
        response = self.client.request(method, path, headers=headers, **kwargs)
        
        try:
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Error {response.status_code}: {response.text}")
            raise e
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            raise e

    def get(self, path, params=None):
        return self.request("GET", path, params=params)

    def post(self, path, json_data=None):
        return self.request("POST", path, json=json_data)

    def put(self, path, json_data=None):
        return self.request("PUT", path, json=json_data)

    def delete(self, path):
        return self.request("DELETE", path)
