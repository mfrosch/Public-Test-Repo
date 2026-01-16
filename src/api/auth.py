"""
Authentication API Router

Handles user registration, login, and token management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.models.user import User, UserCreate, UserLogin, Token
from src.services.auth_service import AuthService, get_current_user

router = APIRouter()


@router.post("/register", response_model=User, status_code=201)
async def register(user_data: UserCreate):
    """
    Register a new user.

    Returns the created user (without password).
    Raises 400 if email or username already exists.
    """
    service = AuthService()

    # Check for existing user
    if await service.get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    if await service.get_user_by_username(user_data.username):
        raise HTTPException(
            status_code=400,
            detail="Username already taken"
        )

    return await service.create_user(user_data)


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """
    Authenticate user and return JWT token.

    Returns access token on success.
    Raises 401 if credentials are invalid.
    """
    service = AuthService()
    user = await service.authenticate_user(
        email=credentials.email,
        password=credentials.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    return await service.create_access_token(user)


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token endpoint.

    Accepts form data for compatibility with OAuth2 clients.
    """
    service = AuthService()
    user = await service.authenticate_user(
        email=form_data.username,  # OAuth2 uses 'username' field
        password=form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await service.create_access_token(user)


@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user's information.
    """
    return current_user


@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_user: User = Depends(get_current_user)
):
    """
    Refresh the access token.

    Requires a valid (non-expired) token.
    """
    service = AuthService()
    return await service.create_access_token(current_user)
