from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.infrastructure.database import get_db
from src.api.schemas.schemas import StockLogResponse
from src.api.services.stock_log_service import StockLogService
from src.api.utils.jwt_handler import require_access_token

router = APIRouter(
    prefix="/api/v1/stock-logs",
    tags=["Logs"],
    dependencies=[Depends(require_access_token)],
)


@router.get("", response_model=list[StockLogResponse])
async def list_stock_logs(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """List all stock logs with pagination."""
    service = StockLogService(db)
    logs = service.list_stock_logs(skip=skip, limit=limit)
    return [StockLogResponse(
        user_name=i.user_name,
        product_name=i.product_name,
        previous_amount=i.previous_amount,
        new_amount=i.new_amount,
        reason=i.reason,
        created_at=i.created_at,
        difference=i.new_amount - i.previous_amount,
    ) for i in logs]

