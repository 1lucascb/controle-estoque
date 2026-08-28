from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from src.api.infrastructure.database import get_db
from src.api.schemas.schemas import ChangePasswordRequest, LoginRequest, TokenResponse
from fastapi.responses import RedirectResponse
from src.api.services.user_service import UserService
from src.api.utils.jwt_handler import create_access_token, require_access_token

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, response: Response, db: Session = Depends(get_db)):
    service = UserService(db)
    user = service.authenticate_user(credentials.username, credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create JWT token with user_id and role
    token_data = {
        "user_id": user.id,
        "role": user.role,
        "username": user.username,
    }
    access_token = create_access_token(token_data)

    # Set token as an HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=4 * 3600,  # 4 hours in seconds
    )

    return TokenResponse(access_token=access_token)


@router.post("/logout")
async def logout(_: dict = Depends(require_access_token)):
    response = RedirectResponse(url="/auth/login.html", status_code=303)
    response.delete_cookie("access_token")
    return response


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    token: dict = Depends(require_access_token),
    db: Session = Depends(get_db),
):
    service = UserService(db)
    if not service.change_password(token["user_id"], password_data):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    return {"detail": "Password changed successfully"}
