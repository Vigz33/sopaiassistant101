import os

# Azure app registration details
# Get details for the app SiriusLite-Authenticator 
tenant_id = os.environ.get('tenant_id')                  # Directory (tenant) ID fixed for Maersk all apps
client_id = os.environ.get('client_id')                  # Application (client) ID 
client_secret = os.environ.get('client_secret')          # Client secret from Certificates & secrets
redirect_base_uri = os.environ.get('redirect_base_uri')  # Local "http://localhost:8080" Or Redirect URI (should match what's registered in Azure)


# Dify details
dify_base_url = os.environ.get('dify_base_url')         # Dify api url 
dify_api_key = os.environ.get('dify_api_key')           # Dify api  key
