from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.api.infrastructure.database import Base
from src.api.infrastructure.models import Category, Product
from src.api.schemas.schemas import CategoryCreate
from src.api.services.category_service import CategoryService


def test_category_cannot_be_deleted_while_referenced():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        category = CategoryService(db).create_category(CategoryCreate(name="Bebidas"))
        db.add(
            Product(
                name="Cafe",
                current_amount=10,
                min_stock_threshold=2,
                category_id=category.id,
            )
        )
        db.commit()

        try:
            CategoryService(db).delete_category(category.id)
        except ValueError as error:
            assert str(error) == "Category cannot be deleted while products reference it"
        else:
            raise AssertionError("Referenced category deletion should fail")

        assert db.query(Category).filter(Category.id == category.id).first() is not None