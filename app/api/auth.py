from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.db.models import User
from app.db.postgres import get_db
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    UserResponse,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.username == payload.username)
        .first()
    )

    if not user or not verify_password(
        payload.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    return TokenResponse(
        access_token=create_access_token(user)
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
def me(
    user: User = Depends(get_current_user),
):
    return user


def seed_admin(db: Session):
    """
    Create the configured admin account if it does not already exist.

    Local development defaults:
        username: admin
        password: admin123

    Production values should be supplied through:
        ADMIN_USERNAME
        ADMIN_PASSWORD
    """

    existing_admin = (
        db.query(User)
        .filter(User.username == settings.admin_username)
        .first()
    )

    if existing_admin:
        return

    db.add(
        User(
            username=settings.admin_username,
            password_hash=hash_password(
                settings.admin_password
            ),
            role="admin",
        )
    )

    db.commit()