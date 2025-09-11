from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
from models.user import User
from schemas.auth import UserCreate, UserLogin
from auth.auth_utils import verify_password, get_password_hash, create_tokens, verify_token

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user: UserCreate) -> User:
        """Create a new user."""
        # Check if user already exists
        db_user = self.db.query(User).filter(
            (User.username == user.username) | (User.email == user.email)
        ).first()
        
        if db_user:
            if db_user.username == user.username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already registered"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # Create new user
        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            full_name=user.full_name
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def authenticate_user(self, username: str, password: str) -> User:
        """Authenticate a user with username and password."""
        user = self.db.query(User).filter(User.username == username).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        return user

    def login_user(self, user_credentials: UserLogin) -> tuple[User, str, str]:
        """Login a user and return user data with tokens."""
        user = self.authenticate_user(user_credentials.username, user_credentials.password)
        
        # Update last login
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        # Create tokens
        access_token, refresh_token = create_tokens(user.id, user.username)
        
        return user, access_token, refresh_token

    def get_user_by_username(self, username: str) -> User:
        """Get user by username."""
        user = self.db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    def get_user_by_id(self, user_id: int) -> User:
        """Get user by ID."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    def refresh_access_token(self, refresh_token: str) -> tuple[str, str]:
        """Refresh access token using refresh token."""
        try:
            username = verify_token(refresh_token, "refresh")
            user = self.get_user_by_username(username)
            
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Inactive user"
                )
            
            # Create new tokens
            access_token, new_refresh_token = create_tokens(user.id, user.username)
            return access_token, new_refresh_token
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
