import sys
import os
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(ROOT, ".."))

import asyncio
from back.src.repositories.product_repository import InMemoryProductRepository


async def main():
	product_repo = InMemoryProductRepository()

	product = await product_repo.create({"name": "Laptop", "price": 1000})
	print(product)

	all_products = await product_repo.get_all()
	print(all_products)


asyncio.run(main())