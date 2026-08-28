from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.api.infrastructure.models import Category, Product
from src.api.schemas.schemas import CategoryCreate


class CategoryService:
    def __init__(self, db: Session):
        self.db = db

    def list_categories(self) -> list[Category]:
        return self.db.query(Category).order_by(Category.name).all()

    def get_category(self, category_id: int) -> Category | None:
        return self.db.query(Category).filter(Category.id == category_id).first()

    def create_category(self, category_data: CategoryCreate) -> Category:
        name = category_data.name.strip()
        if not name:
            raise ValueError("Category name cannot be blank")
        category = Category(name=name)
        self.db.add(category)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ValueError(f"Category with name '{name}' already exists")
        self.db.refresh(category)
        return category

    def delete_category(self, category_id: int) -> bool:
        category = self.get_category(category_id)
        if not category:
            return False
        if self.db.query(Product.id).filter(Product.category_id == category_id).first():
            raise ValueError("Category cannot be deleted while products reference it")
        self.db.delete(category)
        self.db.commit()
        return True