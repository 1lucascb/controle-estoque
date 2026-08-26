from sqlalchemy.orm import Session
from src.api.infrastructure.models import StockLog, User, Product


class StockLogService:
    def __init__(self, db: Session):
        self.db = db

    def list_stock_logs(self, skip: int = 0, limit: int = 50) -> list[StockLog]:
        """Retrieve all stock logs with pagination."""
        return (
            self.db.query(
                StockLog.previous_amount,
                StockLog.new_amount,
                StockLog.created_at,
                StockLog.reason,
                User.full_name.label("user_name"),
                Product.name.label("product_name"),
            ).select_from(
                StockLog
            ).join(
                User,
                User.id == StockLog.user_id
            ).join(
                Product,
                Product.id == StockLog.product_id
            )
            .order_by(StockLog.created_at.desc())
            .filter(StockLog.id > skip)
            .limit(limit)
            .all()
        )

    def get_stock_logs_by_product(self, product_id: int, skip: int = 0, limit: int = 50) -> list[StockLog]:
        """Retrieve stock logs for a specific product."""
        return (
            self.db.query(StockLog)
            .filter(StockLog.product_id == product_id)
            .order_by(StockLog.created_at.desc())
            .filter(StockLog.id > skip)
            .limit(limit)
            .all()
        )

    def get_stock_logs_by_user(self, user_id: int, skip: int = 0, limit: int = 50) -> list[StockLog]:
        """Retrieve stock logs created by a specific user."""
        return (
            self.db.query(StockLog)
            .filter(StockLog.user_id == user_id)
            .order_by(StockLog.created_at.desc())
            .filter(StockLog.id > skip)
            .limit(limit)
            .all()
        )

    def get_stock_log_by_id(self, log_id: int) -> StockLog | None:
        """Retrieve a specific stock log by ID."""
        return self.db.query(StockLog).filter(StockLog.id == log_id).first()
