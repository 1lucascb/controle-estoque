from sqlalchemy.orm import Session
from src.api.infrastructure.models import Category, Product, StockLog
from src.api.schemas.schemas import ProductCreate, ProductUpdate, StockAdjustment
from datetime import datetime, timezone

class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def list_products(self, skip: int = 0, limit: int = 100) -> list[Product]:
        """Retrieve all products with pagination."""
        return self.db.query(Product).filter(Product.id > skip).limit(limit).all()

    def get_product_by_id(self, product_id: int) -> Product | None:
        """Retrieve a product by ID."""
        return self.db.query(Product).filter(Product.id == product_id).first()

    def create_product(self, product_data: ProductCreate) -> Product:
        """Create a new product."""
        now = datetime.now(timezone.utc)
        product = Product(
            name=product_data.name,
            description=product_data.description,
            current_amount=product_data.current_amount,
            min_stock_threshold=product_data.min_stock_threshold,
            image_path=product_data.image_path,
            category_id=self._validate_category(product_data.category_id),
            created_at=now,
            updated_at=now,
        )
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def update_product(self, product_id: int, product_data: ProductUpdate) -> Product | None:
        """Update an existing product."""
        product = self.get_product_by_id(product_id)
        if not product:
            return None

        update_data = product_data.model_dump(exclude_unset=True)

        if "category_id" in update_data:
            update_data["category_id"] = self._validate_category(update_data["category_id"])

        for key, value in update_data.items():
            setattr(product, key, value)

        now = datetime.now(timezone.utc)
        product.updated_at = now

        self.db.commit()
        self.db.refresh(product)
        return product

    def _validate_category(self, category_id: int) -> int:
        if not self.db.query(Category.id).filter(Category.id == category_id).first():
            raise ValueError("Category not found")
        return category_id

    def delete_product(self, product_id: int) -> bool:
        """Delete a product by ID."""
        product = self.get_product_by_id(product_id)
        if not product:
            return False

        self.db.delete(product)
        self.db.commit()
        return True

    def adjust_stock(self, user_id: int, product_id: int, adjustment_data: StockAdjustment) -> tuple[Product | None, StockLog | None]:
        """
        Adjust product stock and create a stock log entry.
        Returns a tuple of (updated_product, stock_log) or (None, None) if product not found.
        """
        product = self.get_product_by_id(product_id)
        if not product:
            return None, None

        previous_amount = product.current_amount
        new_amount = previous_amount + adjustment_data.change_amount

        # Ensure stock doesn't go negative
        if new_amount < 0:
            raise ValueError(f"Stock adjustment would result in negative stock: {new_amount}")

        product.current_amount = new_amount

        # Create stock log entry
        stock_log = StockLog(
            product_id=product_id,
            user_id=user_id,
            previous_amount=previous_amount,
            new_amount=new_amount,
            change_amount=adjustment_data.change_amount,
            reason=adjustment_data.reason,
        )

        self.db.add(stock_log)
        self.db.commit()
        self.db.refresh(product)
        self.db.refresh(stock_log)

        return product, stock_log
