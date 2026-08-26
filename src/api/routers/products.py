from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.infrastructure.database import get_db
from src.api.schemas.schemas import ProductCreate, ProductUpdate, ProductResponse, StockAdjustment, StockLogResponse
from src.api.services.product_service import ProductService
from src.api.utils.jwt_handler import require_access_token

router = APIRouter(
    prefix="/api/v1/products",
    tags=["Products"],
    dependencies=[Depends(require_access_token)],
)


@router.get("", response_model=list[ProductResponse])
async def list_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all products with pagination."""
    service = ProductService(db)
    return service.list_products(skip=skip, limit=limit)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a product by ID."""
    service = ProductService(db)
    product = service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product_data: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product."""
    service = ProductService(db)
    return service.create_product(product_data)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, product_data: ProductUpdate, db: Session = Depends(get_db)):
    """Update an existing product."""
    service = ProductService(db)
    product = service.update_product(product_id, product_data)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete a product by ID."""
    service = ProductService(db)
    if not service.delete_product(product_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")


@router.patch("/{product_id}/stock", status_code=status.HTTP_204_NO_CONTENT)
async def adjust_stock(product_id: int, adjustment: StockAdjustment, db: Session = Depends(get_db), token = Depends(require_access_token)):
    """Adjust product stock level and create a log entry."""
    service = ProductService(db)

    try:
        product = service.adjust_stock(token["user_id"], product_id, adjustment)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
