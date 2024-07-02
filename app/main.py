# Author: Shomu Maitra
# Email: s.maitra@maersk.com
# Description: Sirus MDP APIs Endpoints
# Date: 26th March 2024 

import uvicorn
from fastapi import FastAPI, Response, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from fastapi import HTTPException
import requests
from urllib.parse import urlencode
from dotenv import load_dotenv
from time import sleep
import base64
import hashlib
import uuid  # For unique session management
import os
import json

# from typing import Optional
import config
import api.dify as backendapi
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# Load environment variables
load_dotenv()

# FastAPI application setup
app = FastAPI()

# Mount static files directory
app.mount("/ui", StaticFiles(directory="ui"), name="ui")

# Set up templating with Jinja2, pointing to the 'templates' directory
templates = Jinja2Templates(directory="ui")

#------------------ Authorization methods -----------------------------#
# Azure configuration from environment variables
TENANT_ID = os.getenv("tenant_id")                  # Directory (tenant) ID fixed for Maersk all apps
CLIENT_ID = os.getenv("client_id")                  # Application (client) ID 
CLIENT_SECRET = os.getenv("client_secret")          # Client secret from Certificates & secrets
REDIRECT_BASE_URI = os.getenv("redirect_base_uri")  # Base URI for redirects
REDIRECT_URI = f"{REDIRECT_BASE_URI}/callback"      # Full redirect URI for OAuth callback

class SiteSalt(BaseModel):
    session_id: str 
    code_verifier: str

class SiteAcid(BaseModel):
    state_value: str 
    code_challenge: str  

class SiteUser(BaseModel):
    session_id: str 
    access_token: str 

# Endpoint to initiate login
@app.get("/")
async def prepare(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,     # Required when rendering a template in FastAPI
        },
    )

# Function to generate PKCE code verifier and code challenge
def generate_pkce():
    code_verifier = base64.urlsafe_b64encode(os.urandom(32)).decode("utf-8").strip("=")
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode("utf-8")).digest()
    ).decode("utf-8").strip("=")
    return code_verifier, code_challenge

# Function will save the Authorisation Cookie 
def setAuthCookie(response: Response, salt: SiteSalt, acid: SiteAcid):
    json_compatible_item_data = jsonable_encoder(salt)
    json_content = json.dumps(json_compatible_item_data)
    response.set_cookie(
        key="session_id",           # Key
        value=f"{json_content}",    # Value
        max_age=3600,               # The cookie will expire in 1 hour (3600 seconds)
        httponly=True,              # This flag restricts cookie access from JavaScript
        secure=False,               # Only send the cookie over HTTPS (set to False for development)
        samesite="lax",             # Controls cookie sending with cross-site requests, ## 'lax', 'strict', 'none'
        #domain="http://0.0.0.0:8080"
    )
    if not json_content:
        raise HTTPException(status_code=400, detail="Invalid session to store")
    else :
        return {"result": acid.dict()}

# Function will save the User Cookie 
def setUserCookie(response: Response, user: SiteUser):
    json_compatible_item_data = jsonable_encoder(user)
    json_content = json.dumps(json_compatible_item_data)
    response.set_cookie(
        key="session_user",         # Key
        value=f"{json_content}",    # Value
        max_age=3600,               # The cookie will expire in 1 hour (3600 seconds)
        httponly=True,              # This flag restricts cookie access from JavaScript
        secure=False,               # Only send the cookie over HTTPS (set to False for development)
        samesite="lax",             # Controls cookie sending with cross-site requests, ## 'lax', 'strict', 'none'
        #domain="http://0.0.0.0:8080"
    )
    if not json_content:
        raise HTTPException(status_code=400, detail="Invalid session to store")
    else :
        return {"result": user.dict()}

@app.get("/challange")
async def challange(response: Response, action: str = "ui"):  # Default to "ui" if not provided
    
    code_verifier, code_challenge = generate_pkce() # Generate PKCE code verifier and code challenge
    session_id = str(uuid.uuid4())                  # Create a unique session ID
    state_value = f"{session_id}:{action}"          # Additional context for the state 
    salt = SiteSalt(session_id=session_id, code_verifier=code_verifier)
    acid = SiteAcid(state_value=state_value, code_challenge=code_challenge)
    return setAuthCookie(response, salt=salt, acid=acid)

@app.get("/login")
async def login(response: Response, state_value, code_challenge: str):  

    # Authorization parameters
    auth_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize"
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": "openid profile email User.Read",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "state": state_value,
    }
    ##print("params ==> ", params)
    redirect_url = f"{auth_url}?{urlencode(params)}"
    return RedirectResponse(redirect_url)

# Endpoint to handle callback after Microsoft authorization
@app.get("/callback")
async def callback(request: Request): 

    #print("callback ==> ")
    # Retrieve the authorization code and state from query parameters
    auth_code = request.query_params.get("code")
    state = request.query_params.get("state")
    if not auth_code or not state:
        raise HTTPException(status_code=400, detail="Authorization code or state is missing")

    # Split the state into session ID and action
    session_id, action = state.split(":")
    #print("session_id ==> ", session_id)
    #print("action ==> ", action)

    # Get the cookie value from the request
    cookie_content = request.cookies.get("session_id", None)
    if not cookie_content:
        raise HTTPException(status_code=400, detail="Invalid session ID")
    
    # Retrieve the code verifier from the session
    cookie_data = json.loads(cookie_content)
    code_verifier = cookie_data["code_verifier"]
    session_id_saved = cookie_data["session_id"]

    if session_id != session_id_saved:
        raise HTTPException(status_code=400, detail="Session ID did not match")
    #print("code_verifier ", code_verifier)

    # Token endpoint for Azure
    token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    
    # Data for token exchange
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": auth_code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
        "code_verifier": code_verifier,
    }
    response = requests.post(token_url, data=data)
    if response.status_code != 200:
        raise HTTPException(
            status_code=400, 
            detail=f"Token exchange failed: {response.status_code}",
        )

    token_data = response.json()
    #print("token_data ==> ", token_data)
    
    access_token = token_data.get("access_token")
    #print("access_token ==> ", access_token)

    return templates.TemplateResponse(
        "action.html",
        {
            "request": request,     # Required when rendering a template in FastAPI
            "session_id": session_id,
            "access_token": access_token,
            "action": action
        },
    )

@app.get("/user_challange")
async def user_challange(response: Response, session_id, access_token: str):  
    # Save User cookie
    return setUserCookie(response=response, user=SiteUser(session_id=session_id, access_token=access_token) )

@app.get("/present_ui")
async def present_ui(response: Response, session_id, access_token, action: str):
    
    # Redirect to the appropriate endpoint based on the action
    if action == "ui":
        return RedirectResponse(f"/ui?session_id={session_id}&access_token={access_token}")
    elif action == "health":
        return RedirectResponse(f"/health?session_id={session_id}&access_token={access_token}")
    else:
        return JSONResponse(f"Request can not be served to unknown UI")

# Endpoint for logout
@app.get("/logout")
async def logout(response: Response):
    response.delete_cookie("session_id")
    response.delete_cookie("session_user")
    logout_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/logout"
    logout_url_with_redirect = f"{logout_url}?post_logout_redirect_uri={REDIRECT_URI}"
    
    return RedirectResponse(logout_url_with_redirect)

# Dependency function to check authentication and retrieve user information
async def get_authenticated_user(request: Request):
    session_id = request.query_params.get("session_id")
    access_token = request.query_params.get("access_token")
    if not session_id or not access_token:
        raise HTTPException(status_code=401, detail="Unauthorized. Please login.")

    #print("session_id ==> ", session_id)
    #print("access_token ==> ", access_token)
    # If the username is not already retrieved, fetch from Microsoft Graph
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    user_info_url = "https://graph.microsoft.com/v1.0/me"
    response = requests.get(user_info_url, headers=headers)
    if response.status_code == 200:
        user_data = response.json()
        user_name = user_data.get("displayName", "User")  # Default to "User" if missing
    else:
        raise HTTPException(status_code=400, detail="Failed to fetch user information")
    return {"session_id": session_id, "user_name": user_name}

# Define a function to create a URL with query parameters
def create_url_with_params(base_url, params):
    # Add the query parameters to the base URL
    url_with_params = f"{base_url}?{urlencode(params)}"
    return url_with_params
#-----------------------------------------------------------------#

#------------------ Protected methods -----------------------------#
# Show the UI
@app.get("/ui") 
async def ui(request: Request, authenticated_user=Depends(get_authenticated_user)):
    user_name = authenticated_user["user_name"]
    return templates.TemplateResponse(
        "SiriusLiteUI.html",
        {
            "request": request,     # Required when rendering a template in FastAPI
            "user_name": user_name, # Variable to pass to the template
        },
    )

# Check health
@app.get("/health")
async def health():
    return {"Health": f"I am doing fine!"}

# Send chat messages
@app.post('/dify/chat')
async def create_chat(request: Request, payload: dict):
    url = config.dify_base_url+"/chat-messages"
    api = backendapi.DifyApi(url, config.dify_api_key)
    return StreamingResponse(api.create(payload), media_type='text/event-stream')

#-----------------------------------------------------------------#

    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
