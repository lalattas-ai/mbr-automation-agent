import requests
from config import Config

class OutlookService:
    """
    Microsoft Graph API integration for Outlook emails.
    READY but not actively called - for future use.
    """
    
    def __init__(self):
        self.access_token = Config.OUTLOOK_ACCESS_TOKEN
        self.graph_endpoint = "https://graph.microsoft.com/v1.0"
    
    def search_emails(self, customer_name, token=None):
        """
        Search emails related to customer.
        Returns empty list if token not configured.
        """
        access_token = token or self.access_token
        
        if not access_token:
            return []
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Search for emails containing customer name
        search_url = f"{self.graph_endpoint}/me/messages"
        params = {
            '$search': f'"{customer_name}"',
            '$top': 10,
            '$select': 'subject,bodyPreview,receivedDateTime,from'
        }
        
        try:
            response = requests.get(search_url, headers=headers, params=params)
            if response.status_code == 200:
                return response.json().get('value', [])
        except Exception as e:
            print(f"Outlook API error: {e}")
        
        return []
