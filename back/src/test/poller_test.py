# run_poller.py
import sys
import os


ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(ROOT, ".."))

import asyncio
from back.src.services.integrations.telegram_poller import TelegramPoller
from back.src.repositories.store_repository import StoreRepository
from back.src.repositories.storeChannel_repository import StoreChannel_repository

from back.src.core.settings import settings
from back.src.core.db import SessionLocal

async def main():
    # 1️⃣ گرفتن بات‌ها با مدیریت درست Session
    with SessionLocal() as db:
        str_chn_repo = StoreChannel_repository(db)
        stores_chans = await str_chn_repo.get_all()
        bot_tokens= [s.channel_ref for s in stores_chans]
        
        

    # 2️⃣ ساخت task ها
    tasks = []
    for tokens in bot_tokens:
        poller = TelegramPoller(
            tokens
            # tenant_id=bot.tenant_id
        )
        tasks.append(asyncio.create_task(poller.start()))

    # 3️⃣ زنده نگه داشتن event loop
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())

