from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from src.api.infrastructure.database import get_db
from src.api.schemas.schemas import LoginRequest, TokenResponse
from fastapi.responses import RedirectResponse
from src.api.services.user_service import UserService
from src.api.utils.jwt_handler import create_access_token, require_access_token

router = APIRouter(prefix="/api/v1/data", tags=["Export & Import"])