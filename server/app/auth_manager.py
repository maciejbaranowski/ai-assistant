import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

class GoogleAuthManager:
    SCOPES = [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/tasks'
    ]
    
    def __init__(self, token_path="token.json", credentials_path="credentials.json"):
        self.token_path = token_path
        self.credentials_path = credentials_path
        self._credentials = None
    
    def get_credentials(self):
        if self._credentials and self._credentials.valid:
            return self._credentials
        
        creds = None
        
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Token refresh failed: {e}")
                    creds = None
            
            if not creds:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(f"Credentials file not found: {self.credentials_path}")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        self._credentials = creds
        return creds
    
    def check_scopes(self):
        """
        Check what scopes are currently available in the token.
        Returns dict with scope information.
        """
        if not os.path.exists(self.token_path):
            return {"error": "No token file found"}
        
        try:
            with open(self.token_path, 'r') as f:
                token_data = json.load(f)
            
            current_scopes = token_data.get('scopes', [])
            required_scopes = self.SCOPES
            
            missing_scopes = [scope for scope in required_scopes if scope not in current_scopes]
            
            return {
                "current_scopes": current_scopes,
                "required_scopes": required_scopes,
                "missing_scopes": missing_scopes,
                "has_all_scopes": len(missing_scopes) == 0,
                "has_calendar": any('calendar' in scope for scope in current_scopes),
                "has_tasks": any('tasks' in scope for scope in current_scopes)
            }
        except Exception as e:
            return {"error": f"Failed to read token: {e}"}
    
    def force_reauth(self):
        """
        Force re-authentication by removing the token file.
        """
        if os.path.exists(self.token_path):
            os.remove(self.token_path)
        self._credentials = None
        return self.get_credentials()

# Global auth manager instance
auth_manager = GoogleAuthManager()