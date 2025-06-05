import asyncio
import os
import logging
import shared
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from handlers import (
    access_router, admin_router, reports_router,
    start_router, menu_router, errors_router, broadcast_router
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден в .env")

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

shared.bot_instance = bot
shared.ADMIN_ID = ADMIN_ID

# Подключение твоих существующих роутеров
dp.include_router(access_router)
dp.include_router(admin_router)
dp.include_router(reports_router)
dp.include_router(start_router)
dp.include_router(menu_router)
dp.include_router(errors_router)
dp.include_router(broadcast_router)

# Планировщик отчётов (оставляем как есть)
async def schedule_daily_report():
    import datetime
    while True:
        now = datetime.datetime.now()
        target = now.replace(hour=21, minute=0, second=0, microsecond=0)
        if now > target:
            target += datetime.timedelta(days=1)
        wait = (target - now).total_seconds()
        await asyncio.sleep(wait)
        try:
            report = await shared.db.generate_daily_report()
            await bot.send_message(shared.ADMIN_ID, report, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"[REPORT] Ошибка при отправке отчета: {e}")

async def main():
    try:
        await shared.db.initialize_db()
        asyncio.create_task(schedule_daily_report())
        logger.info("✅ Бот успешно запущен")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")

if __name__ == "__main__":
    asyncio.run(main())
