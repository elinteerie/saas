import httpx
from fastapi import APIRouter, HTTPException, status
from security import Token

from third_party_login import (
    CLIENT_ID, CLIENT_SECRET, resolve_github_token, GITHUB_AUTHORIZATION_URL, GITHUB_REDIRECT_URI
)

router = APIRouter()

@router.get('/auth/url')
def github_login():
    return {
        "auth_url": GITHUB_AUTHORIZATION_URL + f"?client_id={CLIENT_ID}"
    }



@router.get('/github/auth/token', response_model=Token)
async def github_callback(code: str):
    token_response = httpx.post("https://github.com/login/oauth/access_token", 
                                data ={
                                    "client_id": CLIENT_ID,
                                    'client_secret': CLIENT_SECRET,
                                    "code": code,
                                    "redirect_uri": GITHUB_REDIRECT_URI,
                                },
                                headers={"Accept": "application/json"},).json()
    access_token = token_response.get('access_token')
    if not access_token:
        raise HTTPException(status_code=401)
    token_type = token_response.get("token_type", "bearer")

    return {
        "access_token": access_token,
        'token_type': token_type
    }