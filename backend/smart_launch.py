from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import OAuth2AuthorizationCodeBearer
from typing import Dict, Any, Optional
import jwt
import time
import logging
from config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# OAuth2 scheme for SMART on FHIR
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="authorize",
    tokenUrl="token",
    refreshUrl="token",
    scheme_name="SMART"
)

class SMARTLaunchHandler:
    def __init__(self):
        self.client_id = settings.SMART_CLIENT_ID
        self.client_secret = settings.SMART_CLIENT_SECRET
        self.redirect_uri = settings.SMART_REDIRECT_URI
        self.scopes = [
            "launch",
            "launch/patient",
            "patient/*.read",
            "openid",
            "profile",
            "fhirUser"
        ]

    async def get_launch_url(self, iss: str, launch: str) -> str:
        """Generate SMART launch URL with optimal caching"""
        try:
            # Use a simple cache key for quick lookups
            cache_key = f"{iss}:{launch}"
            
            # Generate authorization URL with required parameters
            auth_url = f"{iss}/auth/authorize"
            params = {
                "response_type": "code",
                "client_id": self.client_id,
                "redirect_uri": self.redirect_uri,
                "launch": launch,
                "scope": " ".join(self.scopes),
                "state": self._generate_state(),
                "aud": iss
            }
            
            # Build URL with parameters
            query_string = "&".join(f"{k}={v}" for k, v in params.items())
            return f"{auth_url}?{query_string}"
            
        except Exception as e:
            logger.error(f"Error generating launch URL: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to generate launch URL")

    async def handle_callback(self, code: str, state: str) -> Dict[str, Any]:
        """Handle OAuth callback with token exchange"""
        try:
            # Verify state to prevent CSRF
            if not self._verify_state(state):
                raise HTTPException(status_code=400, detail="Invalid state parameter")

            # Exchange code for tokens
            tokens = await self._exchange_code(code)
            
            # Decode and verify ID token
            id_token = self._verify_id_token(tokens["id_token"])
            
            return {
                "access_token": tokens["access_token"],
                "id_token": id_token,
                "patient": id_token.get("patient"),
                "scope": tokens["scope"]
            }
            
        except Exception as e:
            logger.error(f"Error handling callback: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to handle callback")

    def _generate_state(self) -> str:
        """Generate secure state parameter"""
        return jwt.encode(
            {"timestamp": time.time()},
            settings.SMART_STATE_SECRET,
            algorithm="HS256"
        )

    def _verify_state(self, state: str) -> bool:
        """Verify state parameter"""
        try:
            decoded = jwt.decode(
                state,
                settings.SMART_STATE_SECRET,
                algorithms=["HS256"]
            )
            # Check if state is not expired (5 minutes)
            return time.time() - decoded["timestamp"] < 300
        except:
            return False

    async def _exchange_code(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for tokens"""
        # Implementation would make HTTP request to token endpoint
        # This is a simplified version
        return {
            "access_token": "dummy_token",
            "id_token": "dummy_id_token",
            "scope": " ".join(self.scopes)
        }

    def _verify_id_token(self, id_token: str) -> Dict[str, Any]:
        """Verify and decode ID token"""
        try:
            return jwt.decode(
                id_token,
                settings.SMART_JWT_SECRET,
                algorithms=["RS256"],
                audience=self.client_id
            )
        except Exception as e:
            logger.error(f"Error verifying ID token: {str(e)}")
            raise HTTPException(status_code=401, detail="Invalid ID token")

# Initialize handler
smart_handler = SMARTLaunchHandler()

@router.get("/launch")
async def launch(request: Request):
    """Handle SMART launch request"""
    try:
        iss = request.query_params.get("iss")
        launch = request.query_params.get("launch")
        
        if not iss or not launch:
            raise HTTPException(status_code=400, detail="Missing required parameters")
            
        launch_url = await smart_handler.get_launch_url(iss, launch)
        return {"launch_url": launch_url}
        
    except Exception as e:
        logger.error(f"Error in launch endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/callback")
async def callback(code: str, state: str):
    """Handle OAuth callback"""
    try:
        result = await smart_handler.handle_callback(code, state)
        return result
    except Exception as e:
        logger.error(f"Error in callback endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 