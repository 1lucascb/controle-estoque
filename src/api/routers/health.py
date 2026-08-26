from fastapi import APIRouter, Depends
from src.api.utils.jwt_handler import require_access_token

router = APIRouter(
    prefix="/api/v1/health",
    include_in_schema=False,
    dependencies=[Depends(require_access_token)],
)

@router.get("")
async def health_check() -> dict:
    return {"status": "ok"}

