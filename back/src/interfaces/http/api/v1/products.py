from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from back.src.repositories.product_repository import ProductRepository
from back.src.services.product_service import ProductService
from back.src.interfaces.http.dependencies import get_db
from back.src.interfaces.http.api.v1.schemas.product import ProductResponse


router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


def get_product_service(
    db: Session = Depends(get_db),
) -> ProductService:
    product_repo = ProductRepository(db)
    return ProductService(product_repo)


@router.get(
    "/",
    response_model=list[ProductResponse],
)
async def list_products(
    service: ProductService = Depends(get_product_service),
):
    return await service.list_products()