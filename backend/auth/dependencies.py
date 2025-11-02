"""
Auth dependencies for FastAPI endpoints
"""
from fastapi import Request, HTTPException, status
from typing import Optional
from .jwt_handler import verify_token

async def get_current_user(request: Request) -> dict:
    """
    Get current authenticated user from session_token cookie or Authorization header
    """
    # Try cookie first (primary)
    session_token = request.cookies.get('session_token')
    
    # Fallback to Authorization header
    if not session_token:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            session_token = auth_header.split(' ')[1]
    
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # Verify token
    payload = verify_token(session_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return payload

async def get_current_user_optional(request: Request) -> Optional[dict]:
    """
    Get current user if authenticated, otherwise return None
    """
    try:
        return await get_current_user(request)
    except HTTPException:
        return None
