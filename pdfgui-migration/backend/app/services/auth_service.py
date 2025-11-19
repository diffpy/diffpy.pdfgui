"""Authentication service - user management with bcrypt."""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from ..models.user import Session as UserSession
from ..models.user import User, UserSettings


class AuthService:
    """Service for user authentication and management."""

    def __init__(self, db: Session):
        self.db = db

    def create_user(
        self, email: str, password: str, first_name: Optional[str] = None, last_name: Optional[str] = None
    ) -> User:
        """Create new user with hashed password."""
        # Check if user exists
        existing = self.db.query(User).filter(User.email == email).first()
        if existing:
            raise ValueError("User with this email already exists")

        # Create user with bcrypt hashed password
        user = User(
            email=email, password_hash=get_password_hash(password), first_name=first_name, last_name=last_name
        )
        self.db.add(user)

        # Create default settings
        user_settings = UserSettings(
            user_id=user.id,
            plot_preferences={
                "default_colors": ["#1f77b4", "#ff7f0e", "#2ca02c"],
                "line_width": 1.5,
                "marker_size": 4,
            },
            default_parameters={"qmax": 32.0, "fit_rmax": 30.0},
            ui_preferences={"theme": "light", "auto_save": True},
        )
        self.db.add(user_settings)

        self.db.commit()
        self.db.refresh(user)

        return user

    def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    def create_session(
        self, user: User, ip_address: Optional[str] = None, user_agent: Optional[str] = None
    ) -> dict:
        """Create new session with JWT tokens."""
        # Create tokens
        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))

        # Calculate expiration
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        # Store session
        session = UserSession(
            user_id=user.id,
            token=refresh_token,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.add(session)

        # Update last login
        user.last_login = datetime.utcnow()

        self.db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    def refresh_access_token(self, refresh_token: str) -> Optional[dict]:
        """Refresh access token using refresh token."""
        # Decode refresh token
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None

        # Find session
        session = (
            self.db.query(UserSession)
            .filter(UserSession.token == refresh_token, UserSession.expires_at > datetime.utcnow())
            .first()
        )

        if not session:
            return None

        # Create new access token
        access_token = create_access_token(payload["sub"])

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    def logout(self, refresh_token: str) -> bool:
        """Invalidate session."""
        session = self.db.query(UserSession).filter(UserSession.token == refresh_token).first()

        if session:
            self.db.delete(session)
            self.db.commit()
            return True

        return False

    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()

    def update_password(self, user: User, old_password: str, new_password: str) -> bool:
        """Update user password."""
        if not verify_password(old_password, user.password_hash):
            return False

        user.password_hash = get_password_hash(new_password)
        self.db.commit()
        return True

    def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from access token."""
        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        return self.get_user_by_id(UUID(user_id))
