"""
Authentication Service

Handles user authentication, JWT token management, and password hashing.
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.models.user import User, UserCreate, UserInDB, Token, TokenPayload
from src.services.database import get_db

# Configuration
SECRET_KEY = "your-secret-key-here"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


class AuthService:
    """
    Service class for authentication operations.

    Manages user registration, authentication, and JWT tokens.
    """

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    def hash_password(self, password: str) -> str:
        """Hash a password for storage."""
        return pwd_context.hash(password)

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """
        Find a user by their email address.

        Args:
            email: The email to search for.

        Returns:
            The user if found, None otherwise.
        """
        db = await get_db()
        user_data = await db.users.find_one({"email": email})
        return UserInDB(**user_data) if user_data else None

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Find a user by their username.

        Args:
            username: The username to search for.

        Returns:
            The user if found, None otherwise.
        """
        db = await get_db()
        user_data = await db.users.find_one({"username": username})
        return User(**user_data) if user_data else None

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Find a user by their ID.

        Args:
            user_id: The user's unique identifier.

        Returns:
            The user if found, None otherwise.
        """
        db = await get_db()
        user_data = await db.users.find_one({"id": user_id})
        return User(**user_data) if user_data else None

    async def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user account.

        Args:
            user_data: The registration data.

        Returns:
            The created user (without password).
        """
        db = await get_db()

        now = datetime.utcnow()
        user = UserInDB(
            id=await self._get_next_id(db),
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=self.hash_password(user_data.password),
            is_active=True,
            is_admin=False,
            created_at=now,
            last_login=None,
        )

        await db.users.insert_one(user.model_dump())

        # Return user without hashed password
        return User(**user.model_dump(exclude={"hashed_password"}))

    async def authenticate_user(
        self,
        email: str,
        password: str
    ) -> Optional[User]:
        """
        Authenticate a user with email and password.

        Args:
            email: The user's email.
            password: The plain text password.

        Returns:
            The user if authentication succeeds, None otherwise.
        """
        user = await self.get_user_by_email(email)

        if not user:
            return None

        if not self.verify_password(password, user.hashed_password):
            return None

        # Update last login
        db = await get_db()
        await db.users.update_one(
            {"id": user.id},
            {"$set": {"last_login": datetime.utcnow()}}
        )

        return User(**user.model_dump(exclude={"hashed_password"}))

    async def create_access_token(self, user: User) -> Token:
        """
        Create a JWT access token for a user.

        Args:
            user: The authenticated user.

        Returns:
            Token object with access_token and metadata.
        """
        now = datetime.utcnow()
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        payload = TokenPayload(
            sub=user.id,
            exp=expire,
            iat=now,
        )

        token = jwt.encode(
            payload.model_dump(),
            SECRET_KEY,
            algorithm=ALGORITHM
        )

        return Token(
            access_token=token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def _get_next_id(self, db) -> int:
        """Generate the next auto-increment ID for users."""
        result = await db.counters.find_one_and_update(
            {"_id": "users"},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=True
        )
        return result["seq"]


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Dependency to get the current authenticated user from JWT token.

    Args:
        token: The JWT token from the Authorization header.

    Returns:
        The authenticated user.

    Raises:
        HTTPException: If token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    service = AuthService()
    user = await service.get_user_by_id(user_id)

    if user is None:
        raise credentials_exception

    return user
