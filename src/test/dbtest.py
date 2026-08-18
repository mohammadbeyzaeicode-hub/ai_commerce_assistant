import sys
import os
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(ROOT, ".."))

import asyncio

from core.db import SessionLocal
from repositories.product_repository import ProductRepository
from services.product_service import ProductService
from models.product import Product


async def run():
    # ⚠️ session sync ولی interface async
    db = SessionLocal()

    try:
        product_repo = ProductRepository(db)
        product_service = ProductService(product_repo)

        product = await product_service.create_product(
            name="Test Product3",
            price=300_000,
            seller_id=1,
            inventory=30,
        )

        print("Product created:")
        print(product.id, product.name, product.price)

        products = await product_service.list_products()
        print("Products in DB:")
        for p in products:
            print("-", p.id, p.name, p.price)

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(run())
