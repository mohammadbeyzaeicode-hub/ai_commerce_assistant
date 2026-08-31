import hashlib
import hmac
import json
from urllib.parse import parse_qsl

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from back.src.core.context.request_context import RequestContext
from back.src.core.context.resolver import ContextResolver
from back.src.core.settings import settings
from back.src.models.product.aplication.services.product_service import ProductService
from back.src.interfaces.http.dependencies import get_db
from back.src.interfaces.http.api.v1.schemas.product import ProductResponse
from back.src.models.product.infrastructure.repositories.sqlalchemy_product_repository import SqlAlchemyProductRepository
from back.src.repositories.storeChannel_repository import StoreChannel_repository
from back.src.repositories.store_repository import StoreRepository


router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


async def resolve_mini_app_context(
    x_telegram_init_data: str | None = Header(default=None),
    x_telegram_bot_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> RequestContext:
    print(f"🔍 API Request Headers:")
    print(f"   init_data: {bool(x_telegram_init_data)} (length: {len(x_telegram_init_data) if x_telegram_init_data else 0})")
    print(f"   bot_token: {bool(x_telegram_bot_token)} (length: {len(x_telegram_bot_token) if x_telegram_bot_token else 0})")
    
    if not x_telegram_init_data or not x_telegram_bot_token:
        raise HTTPException(status_code=401, detail="Telegram init data is required")

    fields = dict(parse_qsl(x_telegram_init_data, keep_blank_values=True))
    received_hash = fields.pop("hash", None)
    if not received_hash:
        raise HTTPException(status_code=401, detail="Invalid Telegram init data")

    data_check_string = "\n".join(
        f"{key}={value}" for key, value in sorted(fields.items())
    )
    secret_key = hmac.new(
        b"WebAppData",
        x_telegram_bot_token.encode(),
        hashlib.sha256,
    ).digest()
    expected_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(received_hash, expected_hash):
        raise HTTPException(status_code=401, detail="Invalid Telegram init data")

    try:
        telegram_user = json.loads(fields["user"])
        user_id = str(telegram_user["id"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=401, detail="Telegram user is missing") from error

    try:
        return await ContextResolver(
            store_channel_repo=StoreChannel_repository(db),
            store_repo=StoreRepository(db),
        ).resolve(
            user_id=user_id,
            channel="telegram",
            channel_ref=x_telegram_bot_token,
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail="Store not found for Telegram bot") from error


def get_product_service(
    db: Session = Depends(get_db),
) -> ProductService:
    product_repo = SqlAlchemyProductRepository(db)
    return ProductService(product_repo)


@router.get(
    "/",
    response_model=list[ProductResponse],
)
async def list_products(
    service: ProductService = Depends(get_product_service),
    context: RequestContext = Depends(resolve_mini_app_context),
):
    return await service.list_products(context.store_id)