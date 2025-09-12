from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from database import get_db
from schemas.auth import UserCreate, UserLogin, UserResponse, Token, RefreshTokenRequest
from services.auth_service import AuthService
from middleware.auth_middleware import get_current_active_user
from models.user import User
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    auth_service = AuthService(db)
    try:
        user = auth_service.create_user(user)
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user"
        )

@router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    response: Response,
    db: Session = Depends(get_db)
):
    """Login user and return tokens."""
    auth_service = AuthService(db)
    try:
        user, access_token, refresh_token = auth_service.login_user(user_credentials)
        
        # Set secure HTTP-only cookies
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="none",
            max_age=30 * 60  # 30 minutes
        )
        
        response.set_cookie(
            key="refresh_token", 
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="none",
            max_age=7 * 24 * 60 * 60  # 7 days
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during login"
        )

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token."""
    auth_service = AuthService(db)
    try:
        access_token, refresh_token = auth_service.refresh_access_token(refresh_request.refresh_token)
        
        # Update cookies
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="none",
            max_age=30 * 60
        )
        
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="none",
            max_age=7 * 24 * 60 * 60
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error refreshing token"
        )

@router.post("/logout")
async def logout(response: Response):
    """Logout user by clearing cookies."""
    response.delete_cookie(key="access_token", samesite="none")
    response.delete_cookie(key="refresh_token", samesite="none")
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user

@router.get("/verify")
async def verify_token_endpoint(current_user: User = Depends(get_current_active_user)):
    """Verify if token is valid."""
    return {"valid": True, "user": current_user.username}
