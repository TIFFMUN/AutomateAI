from fastapi import Request, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db, SessionLocal
from auth.auth_utils import verify_token
from services.auth_service import AuthService

async def get_current_user(request: Request):
    """Get current authenticated user from token."""
    # Try to get token from Authorization header first
    authorization = request.headers.get("Authorization")
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
    else:
        # Try to get token from cookies
        token = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        username = verify_token(token, "access")
        print(f"Token verified for username: {username}")
        db = SessionLocal()
        try:
            auth_service = AuthService(db)
            user = auth_service.get_user_by_username(username)
            print(f"User found: {user}")
            return user
        finally:
            db.close()
    except HTTPException as e:
        print(f"HTTPException in auth middleware: {e.detail}")
        raise
    except Exception as e:
        print(f"Exception in auth middleware: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_active_user(request: Request):
    """Get current active user."""
    user = await get_current_user(request)
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return user

async def get_current_superuser(request: Request):
    """Get current superuser."""
    user = await get_current_active_user(request)
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return user
