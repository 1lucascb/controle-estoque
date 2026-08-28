from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.infrastructure.database import get_db
from src.api.schemas.schemas import CategoryCreate, CategoryResponse
from src.api.services.category_service import CategoryService
from src.api.utils.jwt_handler import require_access_token

router = APIRouter(
    prefix="/api/v1/categories",
    tags=["Categories"],
    dependencies=[Depends(require_access_token)],
)


@router.get("", response_model=list[CategoryResponse])
async def list_categories(db: Session = Depends(get_db)):
    return CategoryService(db).list_categories()


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(category_data: CategoryCreate, db: Session = Depends(get_db)):
    try:
        return CategoryService(db).create_category(category_data)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    try:
        deleted = CategoryService(db).delete_category(category_id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")